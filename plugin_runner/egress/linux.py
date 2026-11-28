"""The Linux namespace, mount, and capability calls the confinement needs, through libc."""

import ctypes
import errno
import fcntl
import functools
import os
import signal
import socket
import struct
from collections.abc import Callable
from pathlib import Path
from typing import Any

CLONE_NEWNS = 0x00020000
CLONE_NEWUSER = 0x10000000
CLONE_NEWNET = 0x40000000

MS_BIND = 0x1000
MS_REC = 0x4000
MS_PRIVATE = 0x40000

PR_SET_PDEATHSIG = 1
PR_CAPBSET_DROP = 24
PR_SET_NO_NEW_PRIVS = 38

SIOCGIFFLAGS = 0x8913
SIOCSIFFLAGS = 0x8914
IFF_UP = 0x1

_LINUX_CAPABILITY_VERSION_3 = 0x20080522


class _CapHeader(ctypes.Structure):
    _fields_ = [("version", ctypes.c_uint32), ("pid", ctypes.c_int)]


class _CapData(ctypes.Structure):
    _fields_ = [
        ("effective", ctypes.c_uint32),
        ("permitted", ctypes.c_uint32),
        ("inheritable", ctypes.c_uint32),
    ]


_SIGNATURES: dict[str, list[Any]] = {
    "unshare": [ctypes.c_int],
    "mount": [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_void_p],
    "prctl": [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong],
    "capset": [ctypes.c_void_p, ctypes.c_void_p],
}


@functools.cache
def _function(name: str) -> Callable[..., int]:
    function = getattr(ctypes.CDLL(None, use_errno=True), name)
    function.argtypes = _SIGNATURES[name]
    function.restype = ctypes.c_int
    return function


def _call(name: str, *args: Any, what: str) -> None:
    if _function(name)(*args) != 0:
        code = ctypes.get_errno()
        raise OSError(code, f"{what}: {os.strerror(code)}")


def enter_namespaces() -> None:
    """Move this process into new user, network, and mount namespaces, as root inside them.

    The process must be single-threaded. Its uid and gid map to 0 inside, so files it creates
    keep their owner outside. Mounts become private, so nothing mounted here shows outside.
    """
    uid, gid = os.getuid(), os.getgid()
    _call("unshare", CLONE_NEWUSER | CLONE_NEWNET | CLONE_NEWNS, what="unshare")
    Path("/proc/self/setgroups").write_text("deny")
    Path("/proc/self/uid_map").write_text(f"0 {uid} 1")
    Path("/proc/self/gid_map").write_text(f"0 {gid} 1")
    _call("mount", None, b"/", None, MS_REC | MS_PRIVATE, None, what="make mounts private")


def bind_mount(source: Path, target: Path) -> None:
    """Mount `source` over `target`."""
    _call("mount", bytes(source), bytes(target), None, MS_BIND, None, what=f"bind {target}")


def bring_up_loopback() -> None:
    """Bring up `lo` if it is down, as Linux starts it; gVisor starts it up."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        request = struct.pack("16sH14s", b"lo", 0, b"")
        flags = struct.unpack("16sH14s", fcntl.ioctl(sock, SIOCGIFFLAGS, request))[1]
        if not flags & IFF_UP:
            fcntl.ioctl(sock, SIOCSIFFLAGS, struct.pack("16sH14s", b"lo", flags | IFF_UP, b""))


def drop_capabilities() -> None:
    """Give up every capability, for this process and anything it runs.

    Root inside the user namespace holds every capability over the new namespaces. With the
    bounding set empty, the runner, though uid 0 inside, execs with none.
    """
    prctl = _function("prctl")
    cap = 0
    while prctl(PR_CAPBSET_DROP, cap, 0, 0, 0) == 0:
        cap += 1
    if ctypes.get_errno() != errno.EINVAL:
        raise OSError(ctypes.get_errno(), f"drop capability {cap} from the bounding set")

    header = _CapHeader(_LINUX_CAPABILITY_VERSION_3, 0)
    data = (_CapData * 2)()
    _call("capset", ctypes.addressof(header), ctypes.addressof(data), what="capset")
    _call("prctl", PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0, what="no_new_privs")


def die_with_parent() -> None:
    """Have the kernel kill this process when its parent exits; for `preexec_fn`."""
    _call("prctl", PR_SET_PDEATHSIG, signal.SIGKILL, 0, 0, 0, what="pdeathsig")

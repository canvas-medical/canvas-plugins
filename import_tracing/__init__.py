import importlib.util
import os
import sys
from collections import defaultdict
from collections.abc import Sequence
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any

from psutil import Process

BIG_THRESHOLD = int(os.getenv("BIG_THRESHOLD", f"{5 * 1024 * 1024}"))
CHAIN = ["ROOT"]
CHILDREN = defaultdict(set)
PID = Process().pid


def log(*message: Any) -> None:
    """
    Log an import tracing line to the file for this PID.
    """
    global PID

    with open(f"./profile-imports-{PID}.txt", "a") as f:
        f.write(" ".join(message) + "\n")


class TraceLoader(importlib.util.LazyLoader):
    """
    An import loader that traces each import that occurs.
    """

    loader: Any

    def exec_module(self, module: Any) -> None:
        """
        Execute a module and trace the memory usage it causes.
        """
        global CHILDREN
        global CHAIN

        # Reset the loader on the module as super() does (issue #6725)
        module.__spec__.loader = self.loader
        module.__loader__ = self.loader

        before = Process().memory_info()

        # prevent cycles
        if CHAIN[-1] != module.__name__:
            CHILDREN[CHAIN[-1]].add(module.__name__)

        CHAIN.append(module.__name__)

        try:
            self.loader.exec_module(module)
        except:  # noqa
            # importing can raise exceptions which are caught elsewhere and
            # used to detect whether packages are installed... so we need to
            # catch and re-raise here but add the `finally` clause to log the
            # stats
            raise
        finally:
            after = Process().memory_info()

            big = " _BIG_ " if after.rss - before.rss > BIG_THRESHOLD else ""
            rss_change = f"{after.rss - before.rss:,}"

            log(" → ".join(CHAIN), big + rss_change)

            CHAIN.pop()

    def get_code(self, fullname: str) -> Any:
        """
        Get the module's code from the original loader (which is probably a SourceCodeLoader).
        """
        return self.loader.get_code(fullname)


class TraceFinder:
    """
    A wrapper around a ``MetaPathFinder`` that makes loaders log memory
    increase.

    ``sys.meta_path`` finders have their ``find_spec()`` called to locate a
    module. This returns a ``ModuleSpec`` if found or ``None``. The
    ``ModuleSpec`` has a ``loader`` attribute, which is called to actually
    load a module.

    Our class wraps an existing finder and overloads its ``find_spec()`` to
    replace the ``loader`` with our lazy loader proxy.

    We have to use __getattribute__ to proxy the instance because some meta
    path finders don't support monkeypatching.
    """

    __slots__ = ("_finder",)

    def __init__(self, finder: Any) -> None:
        object.__setattr__(self, "_finder", finder)

    def __repr__(self) -> str:
        return f"<TraceFinder for {object.__getattribute__(self, '_finder')!r}>"

    # __bool__ is canonical Python 3. But check-code insists on __nonzero__ being
    # defined via `def`.
    def __nonzero__(self) -> bool:
        return bool(object.__getattribute__(self, "_finder"))

    __bool__ = __nonzero__

    def __getattribute__(self, name: str) -> Any:
        if name in ("_finder", "find_spec"):
            return object.__getattribute__(self, name)

        return getattr(object.__getattribute__(self, "_finder"), name)

    def __delattr__(self, name: str) -> Any:
        return delattr(object.__getattribute__(self, "_finder"), name)

    def __setattr__(self, name: str, value: Any) -> Any:
        return setattr(object.__getattribute__(self, "_finder"), name, value)

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: ModuleType | None = None,
        /,
    ) -> ModuleSpec | None:
        """
        Find a spec from its name, path, and target.
        """
        finder = object.__getattribute__(self, "_finder")

        try:
            find_spec = finder.find_spec
        except AttributeError:
            spec = (
                None
                if (loader := finder.find_module(fullname, path)) is None
                else importlib.util.spec_from_loader(fullname, loader)
            )
        else:
            spec = find_spec(fullname, path, target)

        # LazyLoader requires exec_module()
        if (
            spec is not None
            and spec.loader is not None
            and getattr(spec.loader, "exec_module", None)
        ):
            spec.loader = TraceLoader(spec.loader)

        return spec


def enable() -> None:
    """
    Enable import tracing.
    """
    new_finders = []

    for finder in sys.meta_path:
        new_finders.append(TraceFinder(finder) if not isinstance(finder, TraceFinder) else finder)

    sys.meta_path[:] = new_finders

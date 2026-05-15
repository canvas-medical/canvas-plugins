from __future__ import annotations

from urllib.parse import urljoin

import requests
import typer

from canvas_cli.apps.auth.utils import get_default_host, get_or_request_api_token


def namespace_url(host: str, *paths: str) -> str:
    """Generate the URL for namespace management endpoints."""
    join = "/".join(["plugin-io/namespaces", "/".join(paths or [])])
    join = join if join.endswith("/") else join + "/"
    return urljoin(host, join)


def _confirm_destructive_action(namespace: str, action_description: str) -> None:
    """Prompt the user to confirm a destructive action by typing the namespace name."""
    print(f"\nThis will {action_description} namespace '{namespace}'. This cannot be undone.")
    confirmation = input("Type the full namespace name to confirm: ")
    if confirmation != namespace:
        print("Confirmation did not match. Aborting.")
        raise typer.Exit(1)


def list_namespaces(
    host: str | None = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
) -> None:
    """List all custom data namespaces."""
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")

    token = get_or_request_api_token(host)
    url = namespace_url(host)

    try:
        r = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
        )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1) from None

    if r.status_code == requests.codes.ok:
        namespaces = r.json().get("namespaces", [])
        if not namespaces:
            print("No custom data namespaces found.")
            return

        for ns in namespaces:
            print(f"{ns['name']}\ttables: {ns['table_count']}\tcustom: {ns['custom_table_count']}")
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def inspect(
    namespace: str = typer.Argument(..., help="Namespace to inspect"),
    host: str | None = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
) -> None:
    """Inspect tables and columns in a namespace."""
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")

    token = get_or_request_api_token(host)
    url = namespace_url(host, namespace)

    try:
        r = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
        )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1) from None

    if r.status_code == requests.codes.ok:
        data = r.json()
        print(f"\nNamespace: {data['namespace']}")

        if data["system_tables"]:
            print("\nSystem tables:")
            for table in data["system_tables"]:
                print(f"  {table['name']}\t~{table['approx_rows']} rows")

        if data["custom_tables"]:
            print("\nCustom tables:")
            for table in data["custom_tables"]:
                print(f"  {table['name']}\t~{table['approx_rows']} rows")
                for col in table.get("columns", []):
                    nullable = "nullable" if col["nullable"] else "not null"
                    print(f"    {col['name']}\t{col['type']}\t{nullable}")
        elif not data["system_tables"]:
            print("\nNo tables found in this namespace.")
    elif r.status_code == 404:
        print(f"Namespace '{namespace}' does not exist.")
        raise typer.Exit(1)
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def reset(
    namespace: str = typer.Argument(..., help="Namespace to reset"),
    execute: bool = typer.Option(
        False,
        "--execute",
        help="Actually perform the reset (default is dry-run)",
        show_default=False,
    ),
    host: str | None = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
) -> None:
    """Reset a namespace: drop custom tables and truncate data tables (dry-run by default)."""
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")

    token = get_or_request_api_token(host)
    url = namespace_url(host, namespace, "reset")

    if execute:
        # First do a dry run to show what will happen
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params={"dry_run": "true"},
            )
        except requests.exceptions.RequestException:
            print(f"Failed to connect to {host}")
            raise typer.Exit(1) from None

        if r.status_code != requests.codes.ok:
            print(f"Status code {r.status_code}: {r.text}")
            raise typer.Exit(1)

        data = r.json()
        _print_reset_preview(data)
        _confirm_destructive_action(namespace, "reset")

        # Now execute
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params={"dry_run": "false"},
            )
        except requests.exceptions.RequestException:
            print(f"Failed to connect to {host}")
            raise typer.Exit(1) from None

        if r.status_code == requests.codes.ok:
            data = r.json()
            print(f"\nNamespace '{namespace}' has been reset.")
            if data.get("tables_dropped"):
                print(f"  Dropped tables: {', '.join(data['tables_dropped'])}")
            if data.get("tables_truncated"):
                print(f"  Truncated tables: {', '.join(data['tables_truncated'])}")
        else:
            print(f"Status code {r.status_code}: {r.text}")
            raise typer.Exit(1)
    else:
        # Dry run
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params={"dry_run": "true"},
            )
        except requests.exceptions.RequestException:
            print(f"Failed to connect to {host}")
            raise typer.Exit(1) from None

        if r.status_code == requests.codes.ok:
            data = r.json()
            _print_reset_preview(data)
            print("\nThis is a dry run. To execute, re-run with --execute")
        elif r.status_code == 404:
            print(f"Namespace '{namespace}' does not exist.")
            raise typer.Exit(1)
        else:
            print(f"Status code {r.status_code}: {r.text}")
            raise typer.Exit(1)


def _print_reset_preview(data: dict) -> None:
    """Print the preview of a reset operation."""
    print(f"\nNamespace: {data['namespace']}")
    if data.get("tables_to_drop"):
        print("\nCustom tables to drop:")
        for table in data["tables_to_drop"]:
            print(f"  {table['name']}\t~{table['approx_rows']} rows")
    else:
        print("\nNo custom tables to drop.")

    if data.get("tables_to_truncate"):
        print("\nData tables to truncate:")
        for table in data["tables_to_truncate"]:
            print(f"  {table['name']}\t~{table['approx_rows']} rows")


def drop(
    namespace: str = typer.Argument(..., help="Namespace to drop"),
    execute: bool = typer.Option(
        False,
        "--execute",
        help="Actually perform the drop (default is dry-run)",
        show_default=False,
    ),
    host: str | None = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
) -> None:
    """Drop an entire namespace and all its tables (dry-run by default)."""
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")

    token = get_or_request_api_token(host)
    url = namespace_url(host, namespace, "drop")

    if execute:
        # First do a dry run to show what will happen
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params={"dry_run": "true"},
            )
        except requests.exceptions.RequestException:
            print(f"Failed to connect to {host}")
            raise typer.Exit(1) from None

        if r.status_code != requests.codes.ok:
            print(f"Status code {r.status_code}: {r.text}")
            raise typer.Exit(1)

        data = r.json()
        _print_drop_preview(data)
        _confirm_destructive_action(namespace, "permanently drop")

        # Now execute
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params={"dry_run": "false"},
            )
        except requests.exceptions.RequestException:
            print(f"Failed to connect to {host}")
            raise typer.Exit(1) from None

        if r.status_code == requests.codes.ok:
            print(f"\nNamespace '{namespace}' has been dropped.")
        else:
            print(f"Status code {r.status_code}: {r.text}")
            raise typer.Exit(1)
    else:
        # Dry run
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params={"dry_run": "true"},
            )
        except requests.exceptions.RequestException:
            print(f"Failed to connect to {host}")
            raise typer.Exit(1) from None

        if r.status_code == requests.codes.ok:
            data = r.json()
            _print_drop_preview(data)
            print("\nThis is a dry run. To execute, re-run with --execute")
        elif r.status_code == 404:
            print(f"Namespace '{namespace}' does not exist.")
            raise typer.Exit(1)
        else:
            print(f"Status code {r.status_code}: {r.text}")
            raise typer.Exit(1)


def _print_drop_preview(data: dict) -> None:
    """Print the preview of a drop operation."""
    print(f"\nNamespace: {data['namespace']}")
    if data.get("tables"):
        print("\nAll tables that will be dropped:")
        for table in data["tables"]:
            print(f"  {table['name']}\t~{table['approx_rows']} rows")
    else:
        print("\nNo tables in this namespace.")

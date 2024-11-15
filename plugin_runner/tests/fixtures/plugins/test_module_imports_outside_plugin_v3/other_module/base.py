from ...test_module_imports_outside_plugin_v2.other_module.base import (
    import_me as other_module_import_me,
)


def import_me() -> list[str]:
    """Test method."""
    return other_module_import_me()

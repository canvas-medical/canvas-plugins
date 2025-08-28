import importlib
import inspect
import pkgutil


def get_factory_classes_from_data() -> set[str]:
    """Collect names of all top-level factory classes."""
    import factory

    from canvas_sdk.test_utils import factories

    factory_class_names = set()

    for _, module_name, _ in pkgutil.iter_modules(factories.__path__):
        if module_name.startswith("_"):
            continue

        full_module_name = f"{factories.__name__}.{module_name}"
        module = importlib.import_module(full_module_name)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == full_module_name and issubclass(
                obj, factory.django.DjangoModelFactory
            ):
                factory_class_names.add(name)

    return factory_class_names


def test_all_factories_are_exported() -> None:
    """Ensure all factories are exported in the factories module's __all__."""
    from canvas_sdk.test_utils import factories

    declared_exports = set(getattr(factories, "__all__", []))
    factory_classes = get_factory_classes_from_data()

    missing = factory_classes - declared_exports
    assert not missing, f"Factories missing from __all__: {sorted(missing)}"

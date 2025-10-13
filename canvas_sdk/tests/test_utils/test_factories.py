import importlib
import inspect
import pkgutil
from typing import Any

import pytest


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


@pytest.mark.django_db
def test_factory_is_instantiable() -> None:
    """Ensure each factory can be instantiated without errors."""
    from canvas_sdk.test_utils import factories

    factory_classes: list[type] = [
        getattr(factories, factory_name) for factory_name in get_factory_classes_from_data()
    ]

    for factory_class in factory_classes:
        try:
            factory_class()
        except Exception as ex:
            raise Exception(f"Failed to instantiate factory '{factory_class.__name__}'") from ex


@pytest.mark.django_db
def test_task_label_factory_tasks() -> None:
    """Ensure TaskLabelFactory can have tasks added."""
    from canvas_sdk.test_utils.factories import TaskFactory, TaskLabelFactory

    TaskFactory_t: Any = TaskFactory
    TaskLabelFactory_t: Any = TaskLabelFactory

    # Create a label with one newly-created Task (via dict) and one Task instance
    task_instance = TaskFactory_t()

    label = TaskLabelFactory_t(tasks=[{"title": "from-dict"}, task_instance])

    # Reload from DB to ensure relation is persisted
    label.refresh_from_db()

    tasks = list(label.tasks.all())
    titles = {t.title for t in tasks}

    assert "from-dict" in titles
    assert task_instance.title in titles

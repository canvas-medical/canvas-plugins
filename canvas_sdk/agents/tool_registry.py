from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any, Protocol


class ToolExecutor(Protocol):
    """Executor signature: ``fn(arguments, *, ctx)`` returning a JSON-serializable value.

    ``arguments`` is the model's ``tool_use.input`` dict — values the model chose.
    ``ctx`` is the platform's per-run context (``patient_id``, ``note_id``,
    ``effects`` accumulator, etc.) — values the model never sees and never chooses.
    """

    def __call__(self, arguments: dict[str, Any], *, ctx: dict[str, Any]) -> Any:
        """Run the tool with model-supplied ``arguments`` and platform-supplied ``ctx``."""
        ...


@dataclass
class EffectField:
    """One field on the argument schema for an effect tool.

    Used by :meth:`ToolRegistry.originate_command_tool` (and future
    effect-tool helpers) to declare what arguments the model can pass and
    how they map onto the underlying Effect/Command class.

    Attributes:
        type: JSON Schema type — ``"string"``, ``"integer"``, ``"boolean"``,
            ``"number"``, or ``"array"``.
        description: Human-readable description for the model. Drives the
            model's argument-selection quality more than the schema does.
        required: When ``True``, the field is added to the JSON Schema's
            ``required`` list. Default ``False``.
        format: Optional JSON-Schema ``format`` hint (e.g., ``"date"`` for
            ISO 8601 dates).
        minimum: Optional minimum value for numeric/integer fields.
        maximum: Optional maximum value for numeric/integer fields.
        enum: Optional list of allowed string values, advertised as
            JSON-Schema ``enum``. Use for fields backed by a closed set
            (e.g., banner-alert intent: ``"info" / "warning" / "alert"``).
            The model is constrained to choose one of these values. For
            arrays of enums, pass the enum inside ``items`` instead.
        items: For ``type="array"`` — the JSON Schema for each item
            (e.g., ``{"type": "string"}``, or ``{"type": "string",
            "enum": [...]}`` for arrays of enum values).
        min_items: For ``type="array"`` — minimum array length.
        max_items: For ``type="array"`` — maximum array length.
        command_field: When the LLM-facing argument name differs from the
            underlying Command/Effect field name, set this to the target
            field name. Defaults to the LLM-facing name (which is the
            dict key in the ``fields`` mapping).
    """

    type: str
    description: str
    required: bool = False
    format: str | None = None
    minimum: int | None = None
    maximum: int | None = None
    enum: list[str] | None = None
    items: dict[str, Any] | None = None
    min_items: int | None = None
    max_items: int | None = None
    command_field: str | None = None


def _note_id_from_ctx(ctx: dict[str, Any]) -> str | None:
    """Default note resolver: read ``ctx["note_id"]`` set by the trigger.

    For agents triggered on a specific note (the typical ``RunAgentEffect``
    pattern), the trigger handler passes ``note_id`` in ``trigger_payload``
    and the agent makes it available via ``tool_ctx["note_id"]``. This
    resolver just reads that value.

    Returns ``None`` if absent — the helper's executor reports a structured
    error to the model in that case.
    """
    return ctx.get("note_id")


@dataclass
class FilterSpec:
    """One filter parameter advertised on a :meth:`ToolRegistry.filter_search_tool`.

    Captures both the JSON-Schema entry the model sees and the runtime
    semantics — either a Django-lookup-style transformation via
    ``apply``, or "schema-only" when ``apply`` is ``None`` and the
    queryset factory consumes the argument directly (typical use:
    queryset-mode selection like ``active_only``).

    Attributes:
        type: JSON Schema type. One of ``"string"``, ``"integer"``,
            ``"boolean"``, ``"number"``.
        description: Human-readable description for the model. Drives
            tool / parameter selection more than the schema does — be
            specific.
        format: Optional JSON-Schema ``format`` hint (e.g., ``"date"``
            for ISO 8601 dates).
        minimum: Optional minimum value for numeric/integer filters.
        maximum: Optional maximum value for numeric/integer filters.
        enum: Optional list of allowed string values, advertised as
            JSON-Schema ``enum``. Use for closed-set filters (e.g.,
            note_type ∈ {office, inpatient, message, ...}). The LLM
            picks from the listed values — without this, it has to
            guess from natural-language hints in the description.
        apply: Optional ``(queryset, value) -> queryset`` callable that
            applies the filter to the queryset. Invoked only when the
            argument is supplied and truthy. When ``None``, the filter
            is schema-only — the queryset factory is expected to read
            the argument and act on it itself.
    """

    type: str
    description: str
    format: str | None = None
    minimum: int | None = None
    maximum: int | None = None
    enum: list[str] | None = None
    apply: Callable[[Any, Any], Any] | None = None


class ToolNotAllowed(LookupError):
    """Raised by :meth:`ToolRegistry.execute` when a registered tool is filtered out.

    Distinct from ``ValueError("Unknown tool: ...")`` (raised when the tool
    isn't registered at all). A ``ToolNotAllowed`` means the tool exists in
    the registry but is excluded by the caller's allowlist — typically
    because the agent's manifest doesn't grant it, or because the agent
    deliberately narrows its tool surface for a particular run.
    """


class ToolRegistry:
    """A composable catalog of agent tools.

    Pairs each tool's JSON-Schema definition with its executor so they can't
    drift apart. Supports two registration styles:

    1. **Decorator** for inline definition::

        @registry.tool(
            name="find_medications",
            description="...",
            input_schema={...},
        )
        def _find_medications(arguments, *, ctx):
            ...

    2. **Imperative** ``register(definition, executor)`` for cases where the
       definition is built elsewhere (e.g., auto-generated from an effect proto).

    The platform-provided :data:`canvas_sdk.agents.standard_tools` is the
    canonical SDK-side registry; plugin authors call
    ``my_registry.extend(standard_tools)`` to adopt the SDK catalog and then
    layer their own tools on top.
    """

    def __init__(self) -> None:
        self._definitions: list[dict[str, Any]] = []
        self._executors: dict[str, ToolExecutor] = {}
        # category name → set of tool names tagged with that category. Used by
        # `resolve_allowed` to expand `@category` references in manifest
        # allowlists.
        self._categories: dict[str, set[str]] = {}
        # tool name → docs-oriented metadata that the LLM-facing definition
        # doesn't carry (returns description, backing model/command/effect
        # class). Populated by the helper methods; consumed by the docs
        # generator. Tools registered via the raw ``tool()`` decorator can
        # opt in via ``returns_description=`` etc.
        self._metadata: dict[str, dict[str, Any]] = {}

    def register(
        self,
        definition: dict[str, Any],
        executor: ToolExecutor,
        *,
        categories: Iterable[str] = (),
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a tool by passing the definition and executor directly.

        Args:
            definition: Anthropic-shaped tool spec (``name``, ``description``,
                ``input_schema``).
            executor: The runtime function to invoke.
            categories: Optional category tags for the tool. Used by
                :meth:`resolve_allowed` to expand ``@category`` references in
                manifest allowlists. Tools may have zero or more categories.
            metadata: Optional docs-oriented metadata about the tool — e.g.,
                ``returns_description`` (free-text summary of the return
                shape), ``model`` (Django data model backing a read tool),
                ``command_class`` / ``effect_class`` (Effect class for write
                tools). Not used at runtime; consumed by the docs generator.

        Raises:
            ValueError: If ``definition`` is missing a ``"name"`` key or if a
                tool with that name is already registered.
        """
        name = definition.get("name")
        if not name:
            raise ValueError("Tool definition is missing a 'name' key")
        if name in self._executors:
            raise ValueError(f"Tool {name!r} is already registered")
        self._definitions.append(definition)
        self._executors[name] = executor
        for category in categories:
            self._categories.setdefault(category, set()).add(name)
        if metadata:
            self._metadata[name] = dict(metadata)

    def metadata_for(self, name: str) -> dict[str, Any]:
        """Return the docs-oriented metadata for a tool, or an empty dict.

        Used by the docs generator and other introspection callers; the
        runtime tool-dispatch path does not consult this.
        """
        return dict(self._metadata.get(name, {}))

    def categories_for(self, name: str) -> tuple[str, ...]:
        """Return the categories a tool is tagged with, in registration order."""
        return tuple(c for c, names in self._categories.items() if name in names)

    def tool(
        self,
        *,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        categories: Iterable[str] = (),
        returns_description: str | None = None,
    ) -> Callable[[ToolExecutor], ToolExecutor]:
        """Decorator form for registering a tool inline with its executor.

        ``categories`` tags the tool for shorthand allowlist references — see
        :meth:`resolve_allowed`. ``returns_description`` is an optional
        free-text summary of the tool's return shape, consumed by the docs
        generator.
        """

        def decorator(fn: ToolExecutor) -> ToolExecutor:
            metadata: dict[str, Any] = {}
            if returns_description is not None:
                metadata["returns_description"] = returns_description
            self.register(
                {"name": name, "description": description, "input_schema": input_schema},
                fn,
                categories=categories,
                metadata=metadata or None,
            )
            return fn

        return decorator

    def filter_search_tool(
        self,
        *,
        name: str,
        description: str,
        queryset_factory: Callable[[dict[str, Any], str], Any],
        filters: dict[str, FilterSpec] | None = None,
        ordering: tuple[str, ...] = (),
        prefetch_related: tuple[str, ...] = (),
        select_related: tuple[str, ...] = (),
        limit_default: int = 25,
        limit_max: int = 100,
        limit_description: str | None = None,
        categories: Iterable[str] = (),
        model: type | None = None,
        returns_description: str | None = None,
    ) -> Callable[[Callable[[Any], dict[str, Any]]], Callable[[Any], dict[str, Any]]]:
        """Register a patient-scoped filter-spec read tool.

        The decorated function is the per-row serializer — it receives one
        model instance and returns a JSON-serializable dict. The helper
        handles everything else: JSON-Schema synthesis from ``filters``,
        queryset-factory invocation with the model's ``arguments`` and the
        ``patient_id`` from ``ctx``, filter application, ordering,
        ``prefetch_related`` / ``select_related``, limit clamping,
        iteration, and registration on the registry.

        Patient-scope enforcement is the ``queryset_factory``'s
        responsibility — it receives the ``patient_id`` from ``ctx`` and
        is expected to apply it. The helper passes the patient_id through
        but does not itself enforce scope; some clinical models require
        traversal through a related table (e.g.
        ``report__patient__id`` for ``LabValue``) and only the factory
        knows the right path.

        Args:
            name: Tool name as advertised to the model.
            description: Tool description as advertised to the model.
                Description quality drives tool-selection accuracy more
                than schema quality does.
            queryset_factory: ``(arguments, patient_id) -> QuerySet``.
                Builds the base queryset with patient scope applied and
                any queryset-mode selection done (e.g., ``.active()`` vs
                ``.committed()``).
            filters: Filter parameters. Keys are model-facing argument
                names; values are :class:`FilterSpec` entries. Filters
                with ``apply=None`` are schema-only — included in the
                JSON Schema so the model can pass them, but consumed by
                ``queryset_factory`` rather than applied via ``apply``.
            ordering: Tuple passed to ``queryset.order_by(*ordering)``.
            prefetch_related: Tuple passed to
                ``queryset.prefetch_related(*prefetch_related)``.
            select_related: Tuple passed to
                ``queryset.select_related(*select_related)``.
            limit_default: Default value for the auto-added ``limit``
                parameter when the model omits it.
            limit_max: Hard cap on the ``limit`` parameter. The helper
                clamps to this maximum regardless of what the model
                requests.
            limit_description: Optional override for the ``limit``
                parameter's description. Defaults to a sensible message
                including the default and max.
            categories: Optional category tags for shorthand allowlist
                references (e.g., ``"clinical_reads"``). See
                :meth:`resolve_allowed` for how categories are used.
            model: Optional Django model class backing this read tool
                (e.g., :class:`canvas_sdk.v1.data.Medication`). Not used
                at runtime; surfaced via :meth:`metadata_for` for docs
                generation so plugin authors can see what data model
                the tool draws from.
            returns_description: Optional free-text summary of the
                tool's return shape (e.g., ``"Each row: id, name,
                status."``). Not used at runtime; consumed by the docs
                generator.

        Returns:
            A decorator. Apply it to a ``(row) -> dict`` function; the
            helper builds the tool's executor around it and registers
            the tool on this registry.

        Raises:
            ValueError: If ``filters`` already contains a ``"limit"``
                key (reserved by the helper) or if a tool with ``name``
                is already registered on this registry.

        Example::

            @standard_tools.filter_search_tool(
                name="find_medications",
                description="Search the patient's medications...",
                queryset_factory=lambda args, pid: (
                    Medication.objects.active()
                    if args.get("active_only")
                    else Medication.objects.committed()
                ).filter(patient__id=pid),
                filters={
                    "name_contains": FilterSpec(
                        type="string",
                        description="...",
                        apply=lambda qs, v: qs.filter(codings__display__icontains=v),
                    ),
                    "active_only": FilterSpec(
                        type="boolean",
                        description="...",
                        # No apply — consumed by queryset_factory.
                    ),
                },
                ordering=("-start_date",),
                prefetch_related=("codings",),
            )
            def _serialize_medication(medication):
                coding = medication.codings.first()
                return {
                    "name": coding.display if coding else "(unknown)",
                    "status": medication.status,
                    ...,
                }
        """
        filters_dict = dict(filters or {})
        if "limit" in filters_dict:
            raise ValueError(
                "'limit' is reserved by filter_search_tool; pass "
                "limit_default / limit_max / limit_description instead."
            )

        # Build the JSON Schema from filter specs plus the auto-added `limit`.
        properties: dict[str, dict[str, Any]] = {}
        for filter_name, spec in filters_dict.items():
            prop: dict[str, Any] = {"type": spec.type, "description": spec.description}
            if spec.format:
                prop["format"] = spec.format
            if spec.minimum is not None:
                prop["minimum"] = spec.minimum
            if spec.maximum is not None:
                prop["maximum"] = spec.maximum
            if spec.enum is not None:
                prop["enum"] = list(spec.enum)
            properties[filter_name] = prop
        properties["limit"] = {
            "type": "integer",
            "minimum": 1,
            "maximum": limit_max,
            "description": (
                limit_description
                or f"Max results. Defaults to {limit_default}; capped at {limit_max}."
            ),
        }

        input_schema: dict[str, Any] = {"type": "object", "properties": properties}

        def decorator(
            serializer: Callable[[Any], dict[str, Any]],
        ) -> Callable[[Any], dict[str, Any]]:
            def executor(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
                patient_id: str = ctx["patient_id"]

                queryset = queryset_factory(arguments, patient_id)

                for filter_name, spec in filters_dict.items():
                    if spec.apply is None:
                        continue
                    value = arguments.get(filter_name)
                    # Skip falsy values — matches the truthy-check pattern the
                    # SDK's hand-written tools used before this helper existed.
                    # Filters that need to distinguish False from None should
                    # use queryset_factory (apply=None) instead.
                    if not value:
                        continue
                    queryset = spec.apply(queryset, value)

                if select_related:
                    queryset = queryset.select_related(*select_related)
                if prefetch_related:
                    queryset = queryset.prefetch_related(*prefetch_related)
                if ordering:
                    queryset = queryset.order_by(*ordering)

                limit = min(max(int(arguments.get("limit", limit_default)), 1), limit_max)
                queryset = queryset[:limit]

                return [serializer(row) for row in queryset]

            metadata: dict[str, Any] = {"kind": "filter_search"}
            if model is not None:
                metadata["model"] = model
            if returns_description is not None:
                metadata["returns_description"] = returns_description
            self.register(
                {"name": name, "description": description, "input_schema": input_schema},
                executor,
                categories=categories,
                metadata=metadata,
            )
            return serializer

        return decorator

    def originate_command_tool(
        self,
        *,
        name: str,
        description: str,
        command_class: type,
        fields: dict[str, EffectField],
        note_resolver: Callable[[dict[str, Any]], str | None] = _note_id_from_ctx,
        no_note_error: str = (
            "No note available for this run; ask the clinician to open or "
            "create a note before requesting this command."
        ),
        pre_build: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None,
        categories: Iterable[str] = (),
        returns_description: str | None = None,
    ) -> None:
        """Register a tool that originates a Canvas Command on a note.

        The platform's analogue to :meth:`filter_search_tool` for write
        tools. Handles the boilerplate of: resolving the target note,
        validating it's available, constructing the Command with the
        model's arguments, calling ``.originate()`` to produce an Effect,
        appending it to ``ctx["effects"]``, and returning a confirmation
        dict.

        The author declares the Command class, the fields the model can
        pass, and (optionally) where to find the target note. The helper
        does the rest. ``.originate()`` is called — never ``.commit()`` —
        per the SDK's "originate but never commit" convention; the
        clinician reviews/edits/commits the draft in the chart UI.

        Args:
            name: Tool name as advertised to the model.
            description: Tool description as advertised to the model.
            command_class: The :class:`canvas_sdk.commands.*` Command
                subclass to instantiate.
            fields: Mapping of LLM-facing argument name to
                :class:`EffectField`. The helper synthesizes the JSON
                Schema from these and maps each argument to the
                corresponding Command field (using
                ``EffectField.command_field`` to rename where the LLM
                name and Command field differ).
            note_resolver: Callable returning the target note's UUID
                (a string) given ``ctx``. Defaults to
                :func:`_note_id_from_ctx` which reads ``ctx["note_id"]``
                — appropriate for agents triggered on a specific note.
                Pass a different resolver for chat-style agents that
                look up the patient's current open note.
            no_note_error: Error message returned to the model when
                ``note_resolver`` returns ``None``. The model surfaces
                this to the clinician (e.g., "open a note before
                requesting prescription drafts").
            pre_build: Optional ``(arguments, ctx) -> dict`` hook for
                custom logic before the Command is built. Return a dict
                of extra keyword arguments to pass to
                ``command_class(...)``. Typical use: normalize values
                (e.g., truncate strings), generate IDs, look up
                external codes. The hook's return value is *merged on
                top of* the helper's argument mapping — keys in the
                hook's return take precedence over the model's
                arguments.
            categories: Optional category tags for the tool. See
                :meth:`resolve_allowed`.
            returns_description: Optional free-text summary of the
                tool's return shape. Not used at runtime; consumed by
                the docs generator.

        Example::

            standard_tools.originate_command_tool(
                name="originate_plan",
                description="Stage a Plan command on the patient's current note...",
                command_class=PlanCommand,
                fields={
                    "narrative": EffectField(
                        type="string",
                        description="The Plan narrative as plain text.",
                        required=True,
                    ),
                },
                categories=("clinical_writes",),
            )
        """
        # Synthesize the JSON Schema from the fields dict.
        properties: dict[str, dict[str, Any]] = {}
        required: list[str] = []
        for field_name, spec in fields.items():
            prop: dict[str, Any] = {"type": spec.type, "description": spec.description}
            if spec.format:
                prop["format"] = spec.format
            if spec.minimum is not None:
                prop["minimum"] = spec.minimum
            if spec.maximum is not None:
                prop["maximum"] = spec.maximum
            if spec.enum is not None:
                prop["enum"] = list(spec.enum)
            if spec.items is not None:
                prop["items"] = spec.items
            if spec.min_items is not None:
                prop["minItems"] = spec.min_items
            if spec.max_items is not None:
                prop["maxItems"] = spec.max_items
            properties[field_name] = prop
            if spec.required:
                required.append(field_name)

        input_schema: dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            input_schema["required"] = required

        # Map LLM-facing arg name to Command field name (defaults to identity).
        command_field_map: dict[str, str] = {
            arg_name: (spec.command_field or arg_name) for arg_name, spec in fields.items()
        }

        def executor(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
            note_uuid = note_resolver(ctx)
            if not note_uuid:
                return {"ok": False, "error": no_note_error}

            # Build the Command's kwargs from the model's arguments, applying
            # any per-field rename via command_field. Falsy values (including
            # None / missing) are skipped — Commands have their own field
            # defaults and we don't want to override them with explicit Nones.
            command_kwargs: dict[str, Any] = {"note_uuid": note_uuid}
            for arg_name, target_field in command_field_map.items():
                value = arguments.get(arg_name)
                if value is None:
                    continue
                command_kwargs[target_field] = value

            # Optional pre_build hook for custom transformations.
            if pre_build is not None:
                extra = pre_build(arguments, ctx)
                if extra:
                    command_kwargs.update(extra)

            effects: list[Any] = ctx["effects"]
            command = command_class(**command_kwargs)
            effects.append(command.originate())

            # Canvas Command classes carry a Meta inner class with a `key`
            # (e.g., "plan", "prescribe"); fall back to the class name if
            # Meta.key isn't set so non-Command effect classes work too.
            meta_cls = getattr(command_class, "Meta", None)
            command_key = getattr(meta_cls, "key", None) if meta_cls else None
            return {
                "ok": True,
                "note_id": note_uuid,
                "command": command_key or command_class.__name__,
                "committed": False,
            }

        metadata: dict[str, Any] = {
            "kind": "originate_command",
            "command_class": command_class,
        }
        if returns_description is not None:
            metadata["returns_description"] = returns_description
        self.register(
            {"name": name, "description": description, "input_schema": input_schema},
            executor,
            categories=categories,
            metadata=metadata,
        )

    def add_effect_tool(
        self,
        *,
        name: str,
        description: str,
        effect_class: type,
        fields: dict[str, EffectField],
        inject_ctx: dict[str, str] | None = None,
        pre_build: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None,
        response_builder: Callable[[Any], dict[str, Any]] | None = None,
        categories: Iterable[str] = (),
        returns_description: str | None = None,
        effect_method: str = "apply",
    ) -> None:
        """Register a tool that stages a non-note-bound Effect.

        Companion to :meth:`originate_command_tool` for the "stage an
        Effect that isn't pinned to a specific note" pattern. Handles
        JSON-Schema synthesis, ctx-key injection (patient_id by default),
        Effect construction, ``.apply()`` invocation, accumulator append,
        and response shaping.

        Use this for effects like ``AddTask``, ``AddBannerAlert``,
        ``RemoveBannerAlert`` — anything where the agent is staging a
        platform-side action that's patient-scoped but doesn't land on
        a specific encounter note. For note-bound originate-command
        patterns, use :meth:`originate_command_tool` instead.

        Args:
            name: Tool name as advertised to the model.
            description: Tool description as advertised to the model.
            effect_class: The :class:`canvas_sdk.effects.*` Effect
                subclass to instantiate. The helper calls ``.apply()``
                on the constructed instance and appends the result to
                ``ctx["effects"]``.
            fields: Mapping of LLM-facing argument name to
                :class:`EffectField`. Same semantics as
                :meth:`originate_command_tool`'s ``fields`` — type,
                description, required, format/minimum/maximum, items/
                min_items/max_items for arrays, ``command_field`` for
                LLM-name → Effect-field rename.
            inject_ctx: Mapping of ``ctx_key`` → ``effect_kwarg_name``,
                used to auto-pass platform-supplied values into the
                Effect's constructor. Defaults to
                ``{"patient_id": "patient_id"}`` — most patient-bound
                effects need this. Set to ``{}`` to inject nothing;
                override to add other ctx keys (e.g., ``encounter_id``).
            pre_build: Optional ``(arguments, ctx) -> dict`` hook for
                custom logic before the Effect is built. Return a dict
                of extra/replacement kwargs. Typical use: generate UUIDs
                for client-side IDs, truncate strings to model-friendly
                lengths, look up external codes. Hook return values
                merge over (override) both the model's arguments and
                the ctx-injected fields.
            response_builder: Optional ``(effect) -> dict`` callable
                that produces the model-facing response. The default is
                ``{"ok": True}``. Use this to surface details that
                inform the next turn (e.g., a generated ``task_id``
                that the model can reference later).
            categories: Optional category tags for the tool. See
                :meth:`resolve_allowed`.
            returns_description: Optional free-text summary of the
                tool's return shape. Not used at runtime; consumed by
                the docs generator.
            effect_method: Name of the Effect class method to invoke
                to produce the wire-format ``Effect``. Defaults to
                ``"apply"`` — the convention used by ``_BaseEffect``
                subclasses (AddTask, AddBannerAlert, etc.). Set to
                ``"create"`` / ``"edit"`` / ``"send"`` for the Message
                effect family (``canvas_sdk.effects.note.message.Message``),
                which uses explicit verbs instead of a single ``.apply()``.

        Example::

            from uuid import uuid4
            from canvas_sdk.effects.task.task import AddTask

            standard_tools.add_effect_tool(
                name="create_task",
                description="Create a follow-up task for the patient...",
                effect_class=AddTask,
                fields={
                    "title": EffectField(type="string", description="...", required=True),
                },
                pre_build=lambda args, ctx: {
                    "id": str(uuid4()),
                    "title": args["title"].strip()[:200],
                },
                response_builder=lambda effect: {
                    "ok": True, "task_id": str(effect.id)
                },
                categories=("task_writes",),
            )
        """
        ctx_field_map: dict[str, str] = (
            {"patient_id": "patient_id"} if inject_ctx is None else dict(inject_ctx)
        )

        # Synthesize the JSON Schema from the fields dict.
        properties: dict[str, dict[str, Any]] = {}
        required: list[str] = []
        for field_name, spec in fields.items():
            prop: dict[str, Any] = {"type": spec.type, "description": spec.description}
            if spec.format:
                prop["format"] = spec.format
            if spec.minimum is not None:
                prop["minimum"] = spec.minimum
            if spec.maximum is not None:
                prop["maximum"] = spec.maximum
            if spec.enum is not None:
                prop["enum"] = list(spec.enum)
            if spec.items is not None:
                prop["items"] = spec.items
            if spec.min_items is not None:
                prop["minItems"] = spec.min_items
            if spec.max_items is not None:
                prop["maxItems"] = spec.max_items
            properties[field_name] = prop
            if spec.required:
                required.append(field_name)

        input_schema: dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            input_schema["required"] = required

        effect_field_map: dict[str, str] = {
            arg_name: (spec.command_field or arg_name) for arg_name, spec in fields.items()
        }

        def executor(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
            # Start with ctx-injected fields.
            effect_kwargs: dict[str, Any] = {}
            for ctx_key, target_field in ctx_field_map.items():
                value = ctx.get(ctx_key)
                if value is not None:
                    effect_kwargs[target_field] = value

            # Layer model-supplied arguments on top.
            for arg_name, target_field in effect_field_map.items():
                value = arguments.get(arg_name)
                if value is None:
                    continue
                effect_kwargs[target_field] = value

            # pre_build override last, so transformations (truncation,
            # generated UUIDs) take precedence.
            if pre_build is not None:
                extra = pre_build(arguments, ctx)
                if extra:
                    effect_kwargs.update(extra)

            effects: list[Any] = ctx["effects"]
            effect = effect_class(**effect_kwargs)
            # Most _BaseEffect subclasses expose ``.apply()``; the Message
            # effect family (canvas_sdk.effects.note.message.Message) uses
            # explicit method names (``.create()`` / ``.edit()`` / ``.send()``)
            # instead. ``effect_method`` defaults to "apply" so existing
            # callers are unaffected.
            effects.append(getattr(effect, effect_method)())

            if response_builder is not None:
                return response_builder(effect)
            return {"ok": True}

        metadata: dict[str, Any] = {
            "kind": "add_effect",
            "effect_class": effect_class,
        }
        if returns_description is not None:
            metadata["returns_description"] = returns_description
        self.register(
            {"name": name, "description": description, "input_schema": input_schema},
            executor,
            categories=categories,
            metadata=metadata,
        )

    def extend(self, other: "ToolRegistry") -> None:
        """Copy every tool from ``other`` into this registry.

        Mutations to ``self`` after the call don't affect ``other`` and vice
        versa — this is a shallow copy of definitions and an executor-ref copy
        of executors. Plugin code typically calls this once at module import
        time to adopt the SDK's :data:`standard_tools` catalog.

        Raises:
            ValueError: On name collisions between the two registries.
        """
        for definition in other._definitions:
            name = definition["name"]
            categories = other.categories_for(name)
            metadata = other.metadata_for(name)
            self.register(
                dict(definition),
                other._executors[name],
                categories=categories,
                metadata=metadata,
            )

    def scope(self, allowed: Iterable[str]) -> "ToolRegistry":
        """Return a *new* registry containing only the named tools.

        The platform's enforcement seam (doc §6.7). The plugin author
        registers their full tool surface in a module-level registry;
        the platform calls ``scope`` with the manifest's
        ``components.agents[].tools.allowed`` set and substitutes the
        scoped registry on ``agent.tools`` before ``run()`` fires. The
        agent then uses ``self.tools.definitions()`` /
        ``.execute(...)`` directly — the disallowed entries simply
        aren't reachable. Defense in depth: even if the agent tries to
        invoke a tool by name, the scoped registry's ``execute`` raises
        ``ValueError("Unknown tool: ...")`` because the entry was never
        registered into the scope.

        Names in ``allowed`` that aren't registered in this source
        registry are silently dropped (a manifest typo can't surface
        phantom tools to the model).

        The source registry is unaffected — ``scope`` is non-destructive.
        Multiple agents sharing a plugin-level registry can each receive
        their own scoped view.
        """
        allowed_set = set(allowed)
        scoped = ToolRegistry()
        for definition in self._definitions:
            name = definition["name"]
            if name in allowed_set:
                scoped.register(
                    dict(definition),
                    self._executors[name],
                    categories=self.categories_for(name),
                    metadata=self.metadata_for(name),
                )
        return scoped

    def resolve_allowed(
        self,
        allowed: Iterable[str],
        *,
        denied: Iterable[str] | None = None,
    ) -> frozenset[str]:
        """Expand ``@category`` references in an allowlist; apply optional ``denied``.

        Entries in ``allowed`` and ``denied`` come in two shapes:

        - A literal tool name (e.g., ``"find_medications"``) — included
          verbatim if the tool is registered on this registry. Unknown
          names are silently dropped (defense in depth: a manifest typo
          can't surface phantom tools to the model).
        - A ``@category`` reference (e.g., ``"@clinical_reads"``) —
          expanded to the names of every tool tagged with that category
          on this registry. Unknown categories resolve to nothing.

        ``denied`` is applied *after* ``allowed`` expansion; subtractions
        win over additions. Use it to opt into a category broadly and
        carve out specific tools or categories.

        Args:
            allowed: Iterable of literal tool names and ``@category``
                references to include.
            denied: Optional iterable in the same shape. Subtracted from
                the resolved set.

        Returns:
            The frozenset of resolved tool names — the platform passes
            this to :meth:`scope` to produce the agent's
            manifest-authorized tool surface.
        """
        result: set[str] = set()
        for entry in allowed:
            if entry.startswith("@"):
                result.update(self._categories.get(entry[1:], set()))
            elif entry in self._executors:
                result.add(entry)

        if denied:
            denied_set: set[str] = set()
            for entry in denied:
                if entry.startswith("@"):
                    denied_set.update(self._categories.get(entry[1:], set()))
                else:
                    denied_set.add(entry)
            result -= denied_set

        return frozenset(result)

    def definitions(self, *, allowed: Iterable[str] | None = None) -> list[dict[str, Any]]:
        """Tool list suitable for ``client.messages.create(tools=...)``.

        Args:
            allowed: Optional iterable of tool names to include. When supplied,
                only tools whose ``name`` appears in the iterable are returned;
                others are filtered out before the model ever sees them. Names
                in ``allowed`` that aren't registered are silently ignored
                (defense in depth — a manifest typo doesn't surface anything
                extra to the model). When ``None`` (the default), every
                registered tool is returned.
        """
        if allowed is None:
            return list(self._definitions)
        allowed_set = set(allowed)
        return [d for d in self._definitions if d["name"] in allowed_set]

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        ctx: dict[str, Any],
        allowed: Iterable[str] | None = None,
    ) -> Any:
        """Dispatch a model-issued tool call to the registered executor.

        Args:
            name: The tool's registered name (the ``"name"`` key from its
                JSON-Schema definition).
            arguments: The model's ``tool_use.input`` dict — values the model
                chose. Passed through to the executor as-is.
            ctx: Platform-supplied per-run context (``patient_id``, ``note_id``,
                the effects accumulator, etc.) the model never sees.
            allowed: If supplied, ``name`` must be in this iterable in addition
                to being registered — otherwise raises :class:`ToolNotAllowed`.
                Pass the same allowlist you passed to :meth:`definitions` so
                the model can't sneak past the catalog filter (e.g., by
                replaying a tool name it remembers from a previous turn that
                used a different allowlist).

        Raises:
            ValueError: If ``name`` is not a registered tool. The caller is
                expected to translate this into a ``tool_result`` with
                ``is_error=True`` rather than crashing the run.
            ToolNotAllowed: If ``allowed`` was supplied and ``name`` is not in it.
        """
        executor = self._executors.get(name)
        if executor is None:
            raise ValueError(f"Unknown tool: {name!r}")
        if allowed is not None and name not in set(allowed):
            raise ToolNotAllowed(f"Tool {name!r} is registered but not in the caller's allowed set")
        return executor(arguments, ctx=ctx)


__exports__ = ("EffectField", "FilterSpec", "ToolNotAllowed", "ToolRegistry")

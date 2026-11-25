"""SDK-provided questionnaire tools, registered on :data:`standard_tools`.

``get_questionnaire`` reads one of the questionnaires the chart's Questionnaire command
offers: its questions, each question's options, and the answers a question depends on.
``originate_questionnaire`` stages a draft Questionnaire command with the answers given on
the patient's open note, never committing it.
"""

from typing import Any

from django.db.models import Prefetch

from canvas_sdk.agents.standard_tools import _ORIGINATE_RETURNS, _is_uuid, standard_tools
from canvas_sdk.agents.tool_registry import EffectField
from canvas_sdk.commands import QuestionnaireCommand
from canvas_sdk.commands.commands.questionnaire import Answer, Selection
from canvas_sdk.v1.data import Question, Questionnaire, ResponseOption

# Each question type these tools answer, by its response option set's type: the name the
# model sees, and the key an answer to it takes.
_QUESTION_TYPES = {
    "TXT": ("text", "text"),
    "INT": ("integer", "integer"),
    "DATE": ("date", "date"),
    "SING": ("single_choice", "option_id"),
    "MULT": ("multiple_choice", "selections"),
}
_ANSWER_KEYS = tuple(answer_key for _, answer_key in _QUESTION_TYPES.values())


def _charting_questionnaires() -> Any:
    """The questionnaires the chart's Questionnaire command offers."""
    return Questionnaire.objects.filter(
        status="AC", use_case_in_charting="QUES", can_originate_in_charting=True
    )


def _find_questionnaire(questionnaire_id: str, name: str) -> Questionnaire:
    """The one charting questionnaire with this id, or else this name."""
    if questionnaire_id:
        found = (
            list(_charting_questionnaires().filter(id=questionnaire_id))
            if _is_uuid(questionnaire_id)
            else []
        )
        if not found:
            raise ValueError(f"No questionnaire the chart offers has id {questionnaire_id!r}.")
        return found[0]
    if not name:
        raise ValueError("Pass a questionnaire_id or a name.")
    found = list(_charting_questionnaires().filter(name__iexact=name))
    if not found:
        raise ValueError(f"No questionnaire the chart offers is named {name!r}.")
    if len(found) > 1:
        ids = ", ".join(str(questionnaire.id) for questionnaire in found)
        raise ValueError(f"Several questionnaires are named {name!r}; pass one id of: {ids}.")
    return found[0]


def _questions(questionnaire: Questionnaire) -> list[Question]:
    """The questionnaire's questions in the order the chart shows them."""
    return list(
        questionnaire.questions.select_related("response_option_set")
        .prefetch_related(
            Prefetch(
                "response_option_set__options",
                queryset=ResponseOption.objects.order_by("ordering"),
            ),
            "dependent_conditions",
        )
        .order_by("dbid")
    )


def _question_type(question: Question) -> tuple[str, str]:
    """The question's type name and answer key, or an error for a type no answer sets."""
    response_type = question.response_option_set.type if question.response_option_set else None
    if response_type not in _QUESTION_TYPES:
        raise ValueError(
            f"Question {question.dbid} ({question.name!r}) has type {response_type}, which "
            "these tools cannot answer."
        )
    return _QUESTION_TYPES[response_type]


def _serialize_question(question: Question) -> dict[str, Any]:
    """One question as get_questionnaire returns it."""
    conditions = question.dependent_conditions.all()
    return {
        "id": question.dbid,
        "text": question.name,
        "code": question.code,
        "type": _question_type(question)[0],
        "acknowledge_only": question.acknowledge_only,
        "options": [
            {"id": option.dbid, "name": option.name, "code": option.code, "value": option.value}
            for option in (
                question.response_option_set.options.all() if question.response_option_set else []
            )
        ],
        "enabled_when": {
            "behavior": question.enable_behavior or "all",
            "conditions": [
                {
                    "question_id": condition.dependent_on_id,
                    "operator": condition.operator,
                    "option_id": condition.answer_option_id,
                    "value": condition.answer_value,
                }
                for condition in conditions
            ],
        }
        if conditions
        else None,
    }


@standard_tools.tool(
    name="get_questionnaire",
    description=(
        "Read one questionnaire the chart's Questionnaire command offers, by "
        "`questionnaire_id` or by exact `name`. Returns its questions in order, each with "
        "`id`, `text`, `type` (text, integer, date, single_choice, multiple_choice), its "
        "`options`, and `enabled_when`: the answers to other questions it applies after "
        "(null when it always applies). Read it before `originate_questionnaire`. "
        "Practice-level config, not patient-scoped."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "questionnaire_id": {"type": "string", "description": "The questionnaire's id."},
            "name": {"type": "string", "description": "The questionnaire's exact name."},
        },
    },
    categories=("config_reads",),
    returns_description=(
        "`{id, name, questions: [{id, text, code, type, acknowledge_only, options: [{id, "
        "name, code, value}], enabled_when: {behavior: 'all'|'any', conditions: "
        "[{question_id, operator, option_id, value}]} | null}]}`."
    ),
    progress_label="Reading the questionnaire",
)
def _get_questionnaire(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """The questionnaire's questions, options, and branching."""
    questionnaire = _find_questionnaire(
        str(arguments.get("questionnaire_id") or "").strip(),
        str(arguments.get("name") or "").strip(),
    )
    return {
        "id": str(questionnaire.id),
        "name": questionnaire.name,
        "questions": [_serialize_question(question) for question in _questions(questionnaire)],
    }


def _answer_matches(condition: Any, answer: dict[str, Any]) -> bool:
    """Whether the answer is the option or the value the condition names."""
    if condition.answer_option_id is not None:
        chosen = [answer.get("option_id")]
        chosen += [selection.get("option_id") for selection in answer.get("selections") or []]
        return condition.answer_option_id in chosen
    given = next((answer[key] for key in ("text", "integer", "date") if key in answer), None)
    return given is not None and str(given) == condition.answer_value


def _condition_met(condition: Any, answer: dict[str, Any] | None) -> bool:
    """Whether one enablement condition holds, given the answer to the question it names."""
    if condition.operator == "exists":
        return answer is not None
    if condition.operator == "not_exists":
        return answer is None
    # An unanswered question neither equals nor differs from the condition's answer.
    if answer is None:
        return False
    matches = _answer_matches(condition, answer)
    return matches if condition.operator == "=" else not matches


def _applies(question: Question, answers: dict[int, dict[str, Any]]) -> bool:
    """Whether the question's enablement conditions hold for these answers."""
    conditions = question.dependent_conditions.all()
    if not conditions:
        return True
    met = [
        _condition_met(condition, answers.get(condition.dependent_on_id))
        for condition in conditions
    ]
    return any(met) if question.enable_behavior == "any" else all(met)


def _command_answer(question_id: int, answer_key: str, answer: dict[str, Any]) -> Answer:
    """The command's answer for one of the model's answers."""
    if answer_key == "selections":
        return Answer(
            question_id=question_id,
            response=[
                Selection(option_id=selection["option_id"], comment=selection.get("comment", ""))
                for selection in answer["selections"]
            ],
        )
    return Answer(question_id=question_id, response=answer[answer_key])


def _questionnaire_pre_build(arguments: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """Check each answer against its question's type and branching, then build the answers."""
    questionnaire = _find_questionnaire(str(arguments.get("questionnaire_id") or "").strip(), "")
    questions = {question.dbid: question for question in _questions(questionnaire)}

    given: dict[int, dict[str, Any]] = {}
    for answer in arguments.get("answers") or []:
        question = questions.get(answer.get("question_id"))
        if question is None:
            raise ValueError(
                f"{answer.get('question_id')!r} is not a question in this questionnaire; "
                "use the ids get_questionnaire returns."
            )
        if question.dbid in given:
            raise ValueError(f"Question {question.dbid} is answered more than once.")
        answer_key = _question_type(question)[1]
        if [key for key in _ANSWER_KEYS if key in answer] != [answer_key]:
            raise ValueError(
                f"Answer question {question.dbid} ({question.name!r}) with `{answer_key}` "
                "and nothing else."
            )
        given[question.dbid] = answer

    for question_id in given:
        if not _applies(questions[question_id], given):
            raise ValueError(
                f"Question {question_id} ({questions[question_id].name!r}) does not apply "
                "given the other answers; leave it out."
            )

    return {
        "questionnaire_id": str(questionnaire.id),
        "answers": [
            _command_answer(question_id, _question_type(questions[question_id])[1], answer)
            for question_id, answer in given.items()
        ],
    }


_ANSWER_ITEM: dict[str, Any] = {
    "type": "object",
    "properties": {
        "question_id": {"type": "integer", "description": "The question's id."},
        "text": {"type": "string", "description": "For a text question."},
        "integer": {"type": "integer", "description": "For an integer question."},
        "date": {"type": "string", "format": "date", "description": "For a date question."},
        "option_id": {
            "type": "integer",
            "description": "For a single_choice question, the chosen option's id.",
        },
        "selections": {
            "type": "array",
            "description": "For a multiple_choice question, each chosen option.",
            "items": {
                "type": "object",
                "properties": {
                    "option_id": {"type": "integer"},
                    "comment": {"type": "string", "description": "What qualifies the choice."},
                },
                "required": ["option_id"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["question_id"],
    "additionalProperties": False,
}


standard_tools.originate_command_tool(
    name="originate_questionnaire",
    description=(
        "Stage a draft Questionnaire on the patient's open note with the answers given. "
        "NEVER commits. Read the questionnaire with `get_questionnaire` first. Answer each "
        "question with the one key its type takes: `text`, `integer`, `date`, `option_id`, "
        "or `selections`. Answer only what the patient or clinician said; leave out a "
        "question that was not answered or that does not apply given the other answers."
    ),
    command_class=QuestionnaireCommand,
    fields={
        "questionnaire_id": EffectField(
            type="string",
            description="The questionnaire's `id` from get_questionnaire.",
            required=True,
            pre_build_only=True,
        ),
        "answers": EffectField(
            type="array",
            description="One answer per answered question.",
            items=_ANSWER_ITEM,
            pre_build_only=True,
        ),
    },
    pre_build=_questionnaire_pre_build,
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.set_progress_labels({"originate_questionnaire": "Drafting the questionnaire"})


__exports__ = ()

"""Validation helpers for diagram definitions.

A definition file can contain either one diagram object or:
    {"diagrams": [diagram, ...]}
A scenario file may also be generated from a use_case_scenario definition.
"""

from __future__ import annotations

from typing import Any

DIAGRAM_TYPES = {
    "use_case",
    "class",
    "sequence",
    "activity",
    "state",
    "use_case_scenario",
}
FORMATS = {"png", "svg", "pdf", "eps", "txt", "atxt"}
RELATION_TYPES = {
    "association",
    "inheritance",
    "composition",
    "aggregation",
    "dependency",
}
SEQ_PARTICIPANT_TYPES = {"actor", "boundary", "control", "entity", "participant"}
ACTIVITY_KINDS = {
    "start",
    "stop",
    "action",
    "if",
    "elseif",
    "else",
    "endif",
    "fork",
    "fork_branch",
    "fork_end",
    "while",
    "endwhile",
    "repeat",
    "repeat_while",
    "note",
    "detach",
}


class DefinitionError(ValueError):
    """Raised when a diagram definition is invalid."""


def require_mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DefinitionError(f"{context} must be an object")
    return value


def require_list(value: Any, context: str, *, allow_empty: bool = True) -> list[Any]:
    if not isinstance(value, list):
        raise DefinitionError(f"{context} must be an array")
    if not allow_empty and not value:
        raise DefinitionError(f"{context} must not be empty")
    return value


def require_nonempty_str(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DefinitionError(f"{context} must be a non-empty string")
    return value.strip()


def require_unique_ids(items: list[Any], context: str) -> list[str]:
    ids: list[str] = []
    for index, item in enumerate(items):
        mapping = require_mapping(item, f"{context}[{index}]")
        item_id = require_nonempty_str(mapping.get("id"), f"{context}[{index}].id")
        if item_id in ids:
            raise DefinitionError(f"Duplicate id '{item_id}' in {context}")
        ids.append(item_id)
    return ids


def validate_enum(value: Any, allowed: set[str], context: str) -> str:
    if value not in allowed:
        options = ", ".join(sorted(allowed))
        raise DefinitionError(f"{context} must be one of: {options}")
    return str(value)


def validate_definition(raw: Any) -> list[dict[str, Any]]:
    """Validate one definition or a definitions container and return list."""
    if isinstance(raw, list):
        definitions = raw
    else:
        root = require_mapping(raw, "definition file")
        if "diagrams" in root:
            definitions = require_list(root["diagrams"], "diagrams", allow_empty=False)
        else:
            definitions = [root]

    checked: list[dict[str, Any]] = []
    ids: set[str] = set()
    for index, item in enumerate(definitions):
        diagram = require_mapping(item, f"diagrams[{index}]")
        diagram_id = require_nonempty_str(diagram.get("id"), f"diagrams[{index}].id")
        if diagram_id in ids:
            raise DefinitionError(f"Duplicate diagram id '{diagram_id}'")
        ids.add(diagram_id)
        require_nonempty_str(diagram.get("title"), f"diagram '{diagram_id}'.title")
        diagram_type = validate_enum(
            diagram.get("type"), DIAGRAM_TYPES, f"diagram '{diagram_id}'.type"
        )
        data = require_mapping(diagram.get("data"), f"diagram '{diagram_id}'.data")
        validator_name = f"validate_{diagram_type}"
        globals()[validator_name](data, diagram_id)
        output_format = diagram.get("format", "png")
        validate_enum(output_format, FORMATS, f"diagram '{diagram_id}'.format")
        checked.append({**diagram, "id": diagram_id, "type": diagram_type, "data": data})
    return checked


def validate_use_case(data: dict[str, Any], diagram_id: str) -> None:
    actors = require_list(data.get("actors"), f"'{diagram_id}'.actors", allow_empty=False)
    use_cases = require_list(
        data.get("useCases"), f"'{diagram_id}'.useCases", allow_empty=False
    )
    validate_unique_ids(actors, f"'{diagram_id}'.actors")
    validate_unique_ids(use_cases, f"'{diagram_id}'.useCases")
    for field in ("associations", "includes", "extends"):
        for index, relation in enumerate(require_list(data.get(field), f"'{diagram_id}'.{field}")):
            relation_map = require_mapping(relation, f"'{diagram_id}'.{field}[{index}]")
            require_nonempty_str(relation_map.get("from"), f"'{diagram_id}'.{field}[{index}].from")
            require_nonempty_str(relation_map.get("to"), f"'{diagram_id}'.{field}[{index}].to")
    known_ids = {x["id"] for x in actors} | {x["id"] for x in use_cases}
    check_relations(data, known_ids, diagram_id)


def validate_unique_ids(items: list[Any], context: str) -> list[str]:
    ids = require_unique_ids(items, context)
    if len(ids) != len(items):
        raise DefinitionError(f"Duplicate ids in {context}")
    return ids


def check_relations(data: dict[str, Any], known_ids: set[str], diagram_id: str) -> None:
    for field in ("associations", "includes", "extends"):
        for index, relation in enumerate(data.get(field, [])):
            relation_map = require_mapping(relation, f"'{diagram_id}'.{field}[{index}]")
            for endpoint in ("from", "to"):
                endpoint_id = require_nonempty_str(
                    relation_map.get(endpoint), f"'{diagram_id}'.{field}[{index}].{endpoint}"
                )
                if endpoint_id not in known_ids:
                    raise DefinitionError(
                        f"Unknown id '{endpoint_id}' in '{diagram_id}'.{field}[{index}]"
                    )


def validate_class(data: dict[str, Any], diagram_id: str) -> None:
    classes = require_list(data.get("classes"), f"'{diagram_id}'.classes", allow_empty=False)
    class_ids = validate_unique_ids(classes, f"'{diagram_id}'.classes")
    for index, class_item in enumerate(classes):
        require_nonempty_str(class_item.get("name"), f"'{diagram_id}'.classes[{index}].name")
        for member_field in ("attributes", "methods", "notes"):
            for member_index, member in enumerate(
                require_list(class_item.get(member_field) or [], f"'{diagram_id}'.classes[{index}].{member_field}")
            ):
                require_nonempty_str(member, f"member {member_index}")
    for index, relation in enumerate(
        require_list(data.get("relations") or [], f"'{diagram_id}'.relations")
    ):
        relation_map = require_mapping(relation, f"'{diagram_id}'.relations[{index}]")
        source = require_nonempty_str(relation_map.get("from"), f"relation {index}.from")
        target = require_nonempty_str(relation_map.get("to"), f"relation {index}.to")
        validate_enum(relation_map.get("type"), RELATION_TYPES, f"relation {index}.type")
        if source not in class_ids or target not in class_ids:
            raise DefinitionError(f"Unknown class id in relation {index}")


def validate_sequence(data: dict[str, Any], diagram_id: str) -> None:
    participants = require_list(
        data.get("participants"), f"'{diagram_id}'.participants", allow_empty=False
    )
    participant_ids = validate_unique_ids(participants, f"'{diagram_id}'.participants")
    for index, participant in enumerate(participants):
        require_nonempty_str(participant.get("label"), f"participant {index}.label")
        validate_enum(
            participant.get("type", "participant"),
            SEQ_PARTICIPANT_TYPES,
            f"participant {index}.type",
        )
    for index, message in enumerate(
        require_list(data.get("messages"), f"'{diagram_id}'.messages", allow_empty=False)
    ):
        message_map = require_mapping(message, f"'{diagram_id}'.messages[{index}]")
        source = require_nonempty_str(message_map.get("from"), f"message {index}.from")
        target = require_nonempty_str(message_map.get("to"), f"message {index}.to")
        require_nonempty_str(message_map.get("label"), f"message {index}.label")
        if source not in participant_ids or target not in participant_ids:
            raise DefinitionError(f"Unknown participant in message {index}")


def validate_activity(data: dict[str, Any], diagram_id: str) -> None:
    statements = require_list(
        data.get("statements"), f"'{diagram_id}'.statements", allow_empty=False
    )
    for index, statement in enumerate(statements):
        statement_map = require_mapping(statement, f"'{diagram_id}'.statements[{index}]")
        kind = validate_enum(statement_map.get("kind"), ACTIVITY_KINDS, f"statement {index}.kind")
        if kind in {"action", "if", "elseif", "while", "repeat_while", "note"}:
            require_nonempty_str(statement_map.get("label"), f"statement {index}.label")


def validate_state(data: dict[str, Any], diagram_id: str) -> None:
    states = require_list(data.get("states"), f"'{diagram_id}'.states", allow_empty=False)
    state_ids = validate_unique_ids(states, f"'{diagram_id}'.states")
    for index, state in enumerate(states):
        require_nonempty_str(state.get("label"), f"state {index}.label")
    for index, transition in enumerate(
        require_list(data.get("transitions"), f"'{diagram_id}'.transitions", allow_empty=False)
    ):
        transition_map = require_mapping(transition, f"'{diagram_id}'.transitions[{index}]")
        source = require_nonempty_str(transition_map.get("from"), f"transition {index}.from")
        target = require_nonempty_str(transition_map.get("to"), f"transition {index}.to")
        require_nonempty_str(transition_map.get("event"), f"transition {index}.event")
        if source not in state_ids and source != "*":
            raise DefinitionError(f"Unknown source state in transition {index}")
        if target not in state_ids and target != "*":
            raise DefinitionError(f"Unknown target state in transition {index}")


def validate_use_case_scenario(data: dict[str, Any], diagram_id: str) -> None:
    required_fields = ["useCase", "actor", "preconditions", "mainFlow", "postconditions"]
    for field in required_fields:
        if field not in data:
            raise DefinitionError(f"scenario '{diagram_id}' is missing '{field}'")
    require_nonempty_str(data.get("useCase"), f"scenario '{diagram_id}'.useCase")
    require_nonempty_str(data.get("actor"), f"scenario '{diagram_id}'.actor")
    require_list(data.get("preconditions"), f"scenario '{diagram_id}'.preconditions", allow_empty=False)
    require_list(data.get("mainFlow"), f"scenario '{diagram_id}'.mainFlow", allow_empty=False)
    require_list(data.get("postconditions"), f"scenario '{diagram_id}'.postconditions", allow_empty=False)
    for index, step in enumerate(data["mainFlow"]):
        require_nonempty_str(step, f"mainFlow[{index}]")
    for index, flow in enumerate(
        require_list(data.get("alternativeFlows"), f"scenario '{diagram_id}'.alternativeFlows")
    ):
        flow_map = require_mapping(flow, f"alternativeFlows[{index}]")
        require_nonempty_str(flow_map.get("name"), f"alternativeFlows[{index}].name")
        require_list(flow_map.get("steps"), f"alternativeFlows[{index}].steps", allow_empty=False)
        for step_index, step in enumerate(flow_map["steps"]):
            require_nonempty_str(step, f"alternativeFlows[{index}].steps[{step_index}]")


# Keep names explicitly available for dynamic lookup.
validate_use_case_scenario.__name__ = "validate_use_case_scenario"

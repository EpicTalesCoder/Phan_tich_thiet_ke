"""Turn validated diagram definitions into PlantUML or Markdown sources."""

from __future__ import annotations

import re
from typing import Any


def _safe_label(value: str) -> str:
    """Make a label safe for one-line PlantUML/Markdown usage."""
    return re.sub(r"\s+", " ", str(value)).replace("\n", " ").strip()


def _quote_label(value: str) -> str:
    return '"' + _safe_label(value).replace('"', "'") + '"'


def generate_plantuml(diagram: dict[str, Any]) -> str:
    diagram_type = diagram["type"]
    data = diagram["data"]
    if diagram_type == "use_case":
        return generate_use_case(diagram["title"], data)
    if diagram_type == "class":
        return generate_class(diagram["title"], data)
    if diagram_type == "sequence":
        return generate_sequence(diagram["title"], data)
    if diagram_type == "activity":
        return generate_activity(diagram["title"], data)
    if diagram_type == "state":
        return generate_state(diagram["title"], data)
    raise ValueError(f"Diagram type '{diagram_type}' has no PlantUML generator")


def generate_use_case(title: str, data: dict[str, Any]) -> str:
    lines = [
        "@startuml",
        # Smetana layout ships inside plantuml.jar, so use case diagrams render
        # without a Graphviz installation.
        "!pragma layout smetana",
        f"title {_quote_label(title)}",
        "left to right direction",
        "skinparam packageStyle rectangle",
        "skinparam shadowing false",
        "",
    ]

    system = data.get("system")
    if system:
        lines.append(f"rectangle {_quote_label(system)} {{")

    for use_case in data["useCases"]:
        label = _quote_label(use_case.get("label", use_case["id"]))
        lines.append(f"  usecase {label} as {use_case['id']}")

    if system:
        lines.append("}")
    lines.append("")

    for actor in data["actors"]:
        label = _quote_label(actor.get("label", actor["id"]))
        kind = actor.get("kind", "actor")
        lines.append(f"{kind} {label} as {actor['id']}")
    lines.append("")

    for relation in data.get("associations", []):
        lines.append(f"{relation['from']} -- {relation['to']}")
    for relation in data.get("includes", []):
        label = _safe_label(relation.get("label", "include"))
        lines.append(f"{relation['from']} ..> {relation['to']} : {label}")
    for relation in data.get("extends", []):
        label = _safe_label(relation.get("label", "extend"))
        lines.append(f"{relation['from']} ..> {relation['to']} : {label}")

    for note in data.get("notes", []):
        lines.append(f"note right of {note['target']} : {_safe_label(note['text'])}")

    lines.extend(["@enduml", ""])
    return "\n".join(lines)


def generate_class(title: str, data: dict[str, Any]) -> str:
    lines = [
        "@startuml",
        # Smetana layout ships inside plantuml.jar, so class diagrams render
        # without a Graphviz installation.
        "!pragma layout smetana",
        f"title {_quote_label(title)}",
        "skinparam classAttributeIconSize 0",
        "skinparam shadowing false",
        "",
    ]
    relation_syntax = {
        "association": "--",
        "inheritance": "--|>",
        "composition": "*--",
        "aggregation": "o--",
        "dependency": "..>",
    }
    for class_item in data["classes"]:
        class_id = class_item["id"]
        name = _quote_label(class_item["name"])
        stereotype = class_item.get("stereotype")
        declaration = f"class {name}"
        if class_id != class_item["name"]:
            # One class with a display name, referenced by its id elsewhere.
            declaration += f" as {class_id}"
        if stereotype:
            declaration += f" <<{stereotype}>>"
        lines.append(declaration)
        lines.append("{")
        for attribute in class_item.get("attributes", []):
            lines.append(f"  {_safe_label(attribute)}")
        for method in class_item.get("methods", []):
            method_text = _safe_label(method)
            if "(" in method_text and not method_text.endswith("()") and "(" in method_text:
                # Keep authors free to write either complete signatures or short names.
                pass
            elif "(" not in method_text:
                method_text += "()"
            lines.append(f"  +{method_text}")
        lines.append("}")

    lines.append("")
    for relation in data["relations"]:
        source = relation["from"]
        target = relation["to"]
        syntax = relation_syntax[relation["type"]]
        from_multiplicity = relation.get("multiplicityFrom")
        to_multiplicity = relation.get("multiplicityTo")
        label = relation.get("label")
        parts = [source]
        if from_multiplicity:
            parts.append(_quote_label(from_multiplicity))
        parts.append(syntax)
        if to_multiplicity:
            parts.append(_quote_label(to_multiplicity))
        parts.append(target)
        line = " ".join(parts)
        if label:
            line += f" : {_safe_label(label)}"
        lines.append(line)

    for note in data.get("notes", []):
        lines.append(f"note \"{_safe_label(note['text'])}\" as {note['id']}")
    lines.extend(["@enduml", ""])
    return "\n".join(lines)


def generate_sequence(title: str, data: dict[str, Any]) -> str:
    lines = [
        "@startuml",
        f"title {_quote_label(title)}",
        "autonumber",
        "skinparam responseMessageBelowArrow true",
        "skinparam shadowing false",
        "",
    ]
    for participant in data["participants"]:
        kind = participant.get("type", "participant")
        label = _quote_label(participant.get("label", participant["id"]))
        lines.append(f"{kind} {label} as {participant['id']}")
    lines.append("")
    for message in data["messages"]:
        source = message["from"]
        target = message["to"]
        label = _safe_label(message["label"])
        kind = message.get("kind", "sync")
        if kind == "return":
            arrow = "-->"
        elif kind == "async":
            arrow = "->>"
        elif kind == "create":
            arrow = "->>"
        else:
            arrow = "->"
        lines.append(f"{source} {arrow} {target} : {label}")
    for note in data.get("notes", []):
        if note.get("over"):
            participants = " and ".join(note["over"])
            lines.append(f"note over {participants} : {_safe_label(note['text'])}")
    lines.extend(["@enduml", ""])
    return "\n".join(lines)


def generate_activity(title: str, data: dict[str, Any]) -> str:
    lines = [
        "@startuml",
        f"title {_quote_label(title)}",
        "start" if not _starts_elsewhere(data["statements"]) else "skinparam shadowing false",
        "skinparam shadowing false",
    ]
    current_lane = None
    for statement in data["statements"]:
        kind = statement["kind"]
        lane = statement.get("lane")
        if lane and lane != current_lane:
            lines.append(f"|{_safe_label(lane)}|")
            current_lane = lane
        if kind == "start":
            lines.append("start")
        elif kind == "stop":
            lines.append("stop")
        elif kind == "action":
            lines.append(f":{_safe_label(statement['label'])};")
        elif kind == "if":
            lines.append(f"if ({_safe_label(statement['label'])}) then (Đúng)")
        elif kind == "elseif":
            lines.append(f"elseif ({_safe_label(statement['label'])}) then (Đúng)")
        elif kind == "else":
            extra = statement.get("label")
            lines.append(f"else ({_safe_label(extra) if extra else 'Sai'})")
        elif kind in {"endif", "fork_end", "endwhile"}:
            lines.append(kind)
        elif kind == "fork":
            lines.append("fork")
        elif kind == "fork_branch":
            lines.append("fork again")
        elif kind == "while":
            lines.append(f"while ({_safe_label(statement['label'])}) is (Đúng)")
        elif kind == "repeat":
            lines.append("repeat")
        elif kind == "repeat_while":
            lines.append(f"repeat while ({_safe_label(statement['label'])}) is (Đúng)")
        elif kind == "note":
            lines.append(f"note right : {_safe_label(statement['label'])}")
        elif kind == "detach":
            lines.append("detach")
    lines.extend(["@enduml", ""])
    return "\n".join(lines)


def _starts_elsewhere(statements: list[dict[str, Any]]) -> bool:
    return bool(statements) and statements[0].get("kind") == "start"


def generate_state(title: str, data: dict[str, Any]) -> str:
    lines = [
        "@startuml",
        # Smetana layout ships inside plantuml.jar, so state diagrams render
        # without a Graphviz installation.
        "!pragma layout smetana",
        f"title {_quote_label(title)}",
        "skinparam shadowing false",
        "",
    ]
    for state in data["states"]:
        lines.append(f"state {_quote_label(state['label'])} as {state['id']}")
    lines.append("")
    for transition in data["transitions"]:
        source = transition["from"]
        target = transition["to"]
        if source == "*":
            source = "[*]"
        if target == "*":
            target = "[*]"
        event = _safe_label(transition["event"])
        guard = transition.get("guard")
        line = f"{source} --> {target} : {event}"
        if guard:
            line += f" [{_safe_label(guard)}]"
        lines.append(line)
    lines.extend(["@enduml", ""])
    return "\n".join(lines)


def generate_scenario_markdown(scenario: dict[str, Any]) -> str:
    lines = [
        f"# Kịch bản: {scenario['useCase']}",
        "",
        f"- **Mã chức năng:** {scenario.get('id', '—')}",
        f"- **Tác nhân chính:** {scenario['actor']}",
        "- **Điều kiện trước:**",
    ]
    lines.extend(f"  - {item}" for item in scenario["preconditions"])
    lines.extend(["", "## Luồng sự kiện chính", ""])
    lines.append("| Bước | Hành động |")
    lines.append("|---:|---|")
    for index, step in enumerate(scenario["mainFlow"], start=1):
        lines.append(f"| {index} | {_safe_label(step)} |")
    lines.extend(["", "**Điều kiện sau:**", ""])
    lines.extend(f"- {item}" for item in scenario["postconditions"])

    alternative_flows = scenario.get("alternativeFlows", [])
    if alternative_flows:
        lines.extend(["", "## Luồng thay thế / ngoại lệ", ""])
        for flow in alternative_flows:
            lines.append(f"### {flow['name']}", )
            lines.append("")
            for index, step in enumerate(flow["steps"], start=1):
                lines.append(f"{index}. {_safe_label(step)}")
            lines.append("")
    lines.append("")
    return "\n".join(lines)

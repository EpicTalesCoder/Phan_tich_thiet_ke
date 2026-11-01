# AI tool manual: QLBH Diagram Tools

## Purpose
This is an automatic UML diagram generator for the QLBH supermarket-system exam. It converts JSON definitions into PlantUML/Markdown sources and can render PNG/SVG/PDF with PlantUML.

## How an AI tool should call it
Run all commands from project root:

```bash
qldbh_diagram_tools/bin/qldbh-diagrams validate qldbh_diagram_tools/definitions/exam_diagrams.json
qldbh_diagram_tools/bin/qldbh-diagrams generate qldbh_diagram_tools/definitions/exam_diagrams.json --out-dir qldbh_diagram_tools/output
qldbh_diagram_tools/bin/qldbh-diagrams render qldbh_diagram_tools/definitions/exam_diagrams.json --out-dir qldbh_diagram_tools/output
```

## Create a custom diagram
1. Copy one diagram object from `definitions/exam_diagrams.json`.
2. Change `id`, `title`, and `data`.
3. Save to `definitions/custom.json`.
4. Validate and render with the commands above.

## Supported diagram types
- `use_case`: actors, use cases, system boundary, include/extend, associations.
- `class`: entity/boundary/control classes, attributes, methods, association/inheritance/composition/aggregation/dependency.
- `sequence`: actor/boundary/control/entity participants and messages.
- `activity`: swimlanes, actions, conditions, repeat, notes.
- `state`: states and transitions.
- `use_case_scenario`: Markdown use-case scenario table and alternative flows.

## Error behavior
- Invalid input returns exit code `2`.
- Missing Java/JAR returns exit code `2`.
- PlantUML syntax/render errors return exit code `2`.

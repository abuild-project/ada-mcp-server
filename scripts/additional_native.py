#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Correlate each probe call with independent native request/result evidence."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from additional_oracles import require_equal

JSON = dict[str, Any]
Pair = tuple[str, JSON, Any]
SignatureCheck = Callable[[list[JSON], Path, int, int, JSON], None]
SYMBOL_KINDS = (
    "file",
    "module",
    "namespace",
    "package",
    "class",
    "method",
    "property",
    "field",
    "constructor",
    "enum",
    "interface",
    "function",
    "variable",
    "constant",
    "string",
    "number",
    "boolean",
    "array",
    "object",
    "key",
    "null",
    "enumMember",
    "struct",
    "event",
    "operator",
    "typeParameter",
)
COMPLETION_KINDS = (
    "Text",
    "Method",
    "Function",
    "Constructor",
    "Field",
    "Variable",
    "Class",
    "Interface",
    "Module",
    "Property",
    "Unit",
    "Value",
    "Enum",
    "Keyword",
    "Snippet",
    "Color",
    "File",
    "Reference",
    "Folder",
    "EnumMember",
    "Constant",
    "Struct",
    "Event",
    "Operator",
    "TypeParameter",
)


def _require_native_position(value: Any) -> None:
    if (
        not isinstance(value, dict)
        or not {"line", "character"} <= value.keys()
        or any(
            type(value[key]) is not int or not 0 <= value[key] <= 2_147_483_647
            for key in ("line", "character")
        )
    ):
        raise AssertionError(
            "native coordinates must be exact integers from zero through 2147483647"
        )


def _require_native_range(value: Any) -> None:
    if not isinstance(value, dict) or not {"start", "end"} <= value.keys():
        raise AssertionError("native coordinates require both range endpoints")
    for key in ("start", "end"):
        _require_native_position(value[key])


def require_native_coordinates(value: Any) -> None:
    """Visit standard coordinate containers, leaving opaque metadata/arguments untouched."""
    if isinstance(value, list):
        for child in value:
            require_native_coordinates(child)
        return
    if not isinstance(value, dict):
        return
    if "start" in value or "end" in value:
        _require_native_range(value)
        return
    if {"line", "character"} <= value.keys():
        _require_native_position(value)
        return
    if "position" in value:
        _require_native_position(value["position"])
    for key in (
        "range",
        "selectionRange",
        "targetRange",
        "targetSelectionRange",
        "originSelectionRange",
        "insert",
        "replace",
    ):
        if key in value:
            _require_native_range(value[key])
    for extent in value.get("fromRanges", []):
        _require_native_range(extent)
    for key in (
        "params",
        "result",
        "items",
        "children",
        "item",
        "to",
        "from",
        "location",
        "edit",
        "edits",
        "textEdit",
        "additionalTextEdits",
        "documentChanges",
        "itemDefaults",
        "editRange",
        "context",
        "diagnostics",
        "relatedInformation",
    ):
        if key in value:
            require_native_coordinates(value[key])
    for edits in value.get("changes", {}).values():
        require_native_coordinates(edits)
    command = value.get("command")
    if isinstance(command, dict):
        require_native_coordinates(command)
    elif isinstance(command, str):
        argument_key = {
            "als-named-parameters": "where",
            "als-refactor-extract-subprogram": "section_to_extract_sloc",
            "als-refactor-extract-variable": "section_to_extract_sloc",
        }.get(command)
        if argument_key is not None:
            for argument in value.get("arguments", []):
                if isinstance(argument, dict) and argument_key in argument:
                    require_native_coordinates(argument[argument_key])


def native_pairs(events: list[JSON]) -> list[Pair]:
    """Require ordered complete exchanges, with no orphan, duplicate or error rows."""
    if len(events) % 2:
        raise AssertionError("native per-call evidence requires complete request/result pairs")
    pairs = []
    identifiers = set()
    for request, response in zip(events[::2], events[1::2]):
        ident = request.get("id")
        if (
            request.get("event") != "request"
            or response.get("event") != "result"
            or type(ident) is not int
            or ident <= 0
            or ident in identifiers
            or type(response.get("id")) is not int
            or response.get("id") != ident
            or response.get("method") != request.get("method")
            or not isinstance(request.get("params"), dict)
            or "result" not in response
        ):
            raise AssertionError(
                "native per-call evidence requires unique successful matching pairs"
            )
        identifiers.add(ident)
        require_native_coordinates(request["params"])
        require_native_coordinates(response["result"])
        pairs.append((request["method"], request["params"], response["result"]))
    return pairs


def _file(uri: str) -> str:
    parsed = urlsplit(uri)
    if parsed.scheme != "file" or parsed.netloc or parsed.query or parsed.fragment:
        raise AssertionError("native fixture locations must be local file URIs")
    return unquote(parsed.path)


def _documentation(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        value = value["value"]
    if not isinstance(value, str):
        raise AssertionError("native fixture documentation must contain text")
    return value


def _kind(value: int, names: tuple[str, ...]) -> str:
    if type(value) is not int or not 1 <= value <= len(names):
        raise AssertionError("native fixture kind must be a valid protocol enumeration")
    return names[value - 1]


def _symbol(item: JSON) -> JSON:
    if "location" in item:
        location = item["location"]
        start = location["range"]["start"]
        return {
            "name": item["name"],
            "kind": _kind(item["kind"], SYMBOL_KINDS),
            "file": _file(location["uri"]),
            "line": start["line"] + 1,
            "column": start["character"] + 1,
            "containerName": item.get("containerName", ""),
        }
    extent = item["range"]
    selection: JSON = item["selectionRange"] if "selectionRange" in item else extent
    start = selection["start"]
    result = {
        "name": item["name"],
        "kind": _kind(item["kind"], SYMBOL_KINDS),
        "line": start["line"] + 1,
        "column": start["character"] + 1,
        "range": {"start": extent["start"]["line"] + 1, "end": extent["end"]["line"] + 1},
    }
    if "detail" in item:
        result["detail"] = item["detail"]
    if item.get("children"):
        result["children"] = [_symbol(child) for child in item["children"]]
    return result


def _edge(item: JSON) -> JSON:
    start = item["range"]["start"]
    return {
        "name": item["name"],
        "kind": item["kind"],
        "file": _file(item["uri"]),
        "line": start["line"] + 1,
        "column": start["character"] + 1,
    }


def require_call_native(
    events: list[JSON],
    tool: str,
    arguments: JSON,
    result: JSON,
    root: Path,
    signature_check: SignatureCheck,
) -> None:
    """Check all native paths before acceptance, with explicit native-free exemptions."""
    pairs = native_pairs(events)
    local = (
        tool in {"ada_dependency_graph", "ada_alire_info", "ada_build"}
        or (tool == "ada_get_spec" and not {"line", "column"} <= arguments.keys())
        or (tool == "ada_rename_symbol" and arguments.get("new_name") == "Invalid__Name")
    )
    if local:
        require_equal(pairs, [], "native-free local probe path")
        return
    expected: list[tuple[str, JSON]] = []
    projected: JSON
    if tool == "ada_project_info":
        cold = bool(pairs and pairs[0][0] == "initialize")
        if cold:
            require_equal(pairs[0][1]["rootUri"], root.as_uri(), "native project root")
            require_equal(
                pairs[0][1]["initializationOptions"],
                {"projectFile": str(root / "additional.gpr")},
                "native project selection",
            )
            pairs = pairs[1:]
        commands: tuple[str, ...] = ("als-project-view-information", "als-mains")
        reload = not cold and arguments.get("refresh", False) is True
        if reload:
            commands = ("als-reload-project", *commands)
        expected = [
            ("workspace/executeCommand", {"command": command, "arguments": []})
            for command in commands
        ]
        require_equal([(m, p) for m, p, _ in pairs], expected, "native project requests")
        if reload:
            require_equal(pairs[0][2], None, "native project reload result")
        view, mains = pairs[-2][2], pairs[-1][2]
        selected = [
            entry["project"]
            for entry in view["projects"]
            if entry["project"]["id"] == view["tree"]["root-project"]["id"]
        ]
        if len(selected) != 1:
            raise AssertionError("native project view must identify exactly one root")
        project = selected[0]
        projected = {
            "complete": True,
            "indexing_complete": result.get("indexing_complete"),
            "project_file": project["file-name"],
            "project_name": project["name"],
            "source_dirs": project["source-directories"],
            "object_dir": project["object-directory"],
            "exec_dir": project["executable-directory"],
            "main_units": [Path(main).name for main in mains or []],
        }
        if type(result.get("indexing_complete")) is not bool:
            raise AssertionError("project indexing_complete must be a Boolean snapshot")
    else:
        file = Path(arguments["file"])
        document = {"textDocument": {"uri": file.as_uri()}}
        position = {
            "line": arguments.get("line", 1) - 1,
            "character": arguments.get("column", 1) - 1,
        }
        located = {**document, "position": position}
        methods = {
            "ada_document_symbols": "textDocument/documentSymbol",
            "ada_completions": "textDocument/completion",
            "ada_signature_help": "textDocument/signatureHelp",
            "ada_code_actions": "textDocument/codeAction",
            "ada_rename_symbol": "textDocument/prepareRename",
            "ada_format_file": "textDocument/formatting",
            "ada_get_spec": "textDocument/declaration",
            "ada_call_hierarchy": "textDocument/prepareCallHierarchy",
        }
        method = methods[tool]
        if not pairs:
            raise AssertionError(f"native per-call evidence is missing for {tool}")
        if pairs[0][0] != method:
            raise AssertionError(f"native per-call evidence must start with {method}")
        native = pairs[0][2]
        shapes = {
            "ada_document_symbols": (list,),
            "ada_completions": (list, dict),
            "ada_signature_help": (dict,),
            "ada_code_actions": (list,),
            "ada_rename_symbol": (dict,),
            "ada_format_file": (list,),
            "ada_get_spec": (list, dict),
            "ada_call_hierarchy": (list,),
        }
        if native is not None and type(native) not in shapes[tool]:
            raise AssertionError(f"native reply has an invalid protocol shape for {tool}")
        if (
            tool == "ada_completions"
            and isinstance(native, dict)
            and (
                not isinstance(native.get("items"), list)
                or type(native.get("isIncomplete")) is not bool
            )
        ):
            raise AssertionError("native completion list requires items and isIncomplete")
        if tool == "ada_rename_symbol" and native == {}:
            raise AssertionError("native rename preparation must be null or select a token")
        if tool == "ada_document_symbols":
            expected = [(method, document)]
            projected = {"symbols": [_symbol(item) for item in native or []]}
        elif tool == "ada_completions":
            trigger = arguments.get("trigger_character")
            context = (
                {"triggerKind": 2, "triggerCharacter": trigger} if trigger else {"triggerKind": 1}
            )
            expected = [(method, {**located, "context": context})]
            items = native.get("items", []) if isinstance(native, dict) else native or []
            items = items[: arguments.get("limit", 50)]
            projected = {
                "completions": [
                    {
                        "label": item["label"],
                        "kind": _kind(item["kind"], COMPLETION_KINDS),
                        "detail": item.get("detail", ""),
                        "documentation": _documentation(item.get("documentation")),
                        "insert_text": item.get("insertText", item["label"]),
                        "sort_text": item.get("sortText", ""),
                    }
                    for item in items
                ],
                "count": len(items),
                "is_incomplete": native.get("isIncomplete", False)
                if isinstance(native, dict)
                else False,
            }
        elif tool == "ada_signature_help":
            expected = [(method, located)]
            if native is not None and (
                not isinstance(native, dict) or not isinstance(native.get("signatures"), list)
            ):
                raise AssertionError("native signature reply requires its signatures array")
            signatures = native.get("signatures", []) if native else []
            if signatures:
                signature_check(events, file, arguments["line"], arguments["column"], result)
                projected = {
                    "found": True,
                    "active_signature": result["active_signature"],
                    "active_parameter": result["active_parameter"],
                    "signatures": [
                        {
                            "label": sig["label"],
                            "documentation": _documentation(sig.get("documentation")),
                            "parameters": [
                                {
                                    "label": param["label"],
                                    "documentation": _documentation(param.get("documentation")),
                                }
                                for param in sig.get("parameters", [])
                            ],
                        }
                        for sig in signatures
                    ],
                }
            else:
                if native and any(
                    type(native[key]) is not int or not 0 <= native[key] <= 2_147_483_647
                    for key in ("activeSignature", "activeParameter")
                    if key in native
                ):
                    raise AssertionError("native empty signature indices must be valid uintegers")
                projected = {
                    "found": False,
                    "signatures": [],
                    "active_signature": 0,
                    "active_parameter": 0,
                }
        elif tool == "ada_code_actions":
            start = {
                "line": arguments["start_line"] - 1,
                "character": arguments["start_column"] - 1,
            }
            end_line = arguments.get("end_line")
            end_column = arguments.get("end_column")
            if end_line is None:
                end_line = arguments["start_line"]
            if end_column is None:
                end_column = arguments["start_column"]
            end = {"line": end_line - 1, "character": end_column - 1}
            expected = [
                (
                    method,
                    {
                        **document,
                        "range": {"start": start, "end": end},
                        "context": {"diagnostics": arguments.get("diagnostics", [])},
                    },
                )
            ]
            actions = []
            for action in native or []:
                summary = {
                    "title": action["title"],
                    "kind": action.get("kind", ""),
                    "is_preferred": action.get("isPreferred", False),
                    "has_edit": "edit" in action,
                    "files_affected": 0,
                }
                if "edit" in action:
                    summary["files_affected"] = len(action["edit"].get("changes", {})) or len(
                        action["edit"].get("documentChanges", [])
                    )
                if "command" in action:
                    command = action["command"]
                    summary["command"] = (
                        command
                        if isinstance(command, str)
                        else command.get("title", command.get("command", ""))
                    )
                actions.append(summary)
            projected = {"actions": actions, "count": len(actions)}
        elif tool == "ada_format_file":
            expected = [
                (
                    method,
                    {
                        **document,
                        "options": {
                            "tabSize": arguments.get("tab_size", 3),
                            "insertSpaces": arguments.get("insert_spaces", True),
                        },
                    },
                )
            ]
            edits = [
                {
                    "start_line": edit["range"]["start"]["line"] + 1,
                    "start_column": edit["range"]["start"]["character"] + 1,
                    "end_line": edit["range"]["end"]["line"] + 1,
                    "end_column": edit["range"]["end"]["character"] + 1,
                    "new_text": edit["newText"],
                }
                for edit in native or []
            ]
            projected = {
                "formatted": native is not None,
                "file": str(file),
                "edits": edits,
                "changes": len(edits),
            }
        elif tool == "ada_get_spec":
            expected = [(method, located)]
            if not native:
                raise AssertionError(
                    "semantic spec requires a native declaration, not filename fallback"
                )
            location = native[0] if isinstance(native, list) else native
            target = Path(_file(location["uri"]))
            if not target.resolve().is_relative_to(root.resolve()):
                raise AssertionError("native semantic spec target must stay in the owned fixture")
            start = location["range"]["start"]
            projected = {
                "found": True,
                "spec_file": str(target),
                "line": start["line"] + 1,
                "column": start["character"] + 1,
                "preview": target.read_text().splitlines()[start["line"]].strip(),
            }
        elif tool == "ada_call_hierarchy":
            expected = [(method, located)]
            if not native:
                projected = {"found": False, "outgoing_calls": [], "incoming_calls": []}
            else:
                item = native[0] if isinstance(native, list) else native
                projected = {"found": True, "symbol": item["name"]}
                for direction, endpoint in (("outgoing", "to"), ("incoming", "from")):
                    values = []
                    if arguments.get("direction", "outgoing") in (direction, "both"):
                        expected.append(("callHierarchy/" + direction + "Calls", {"item": item}))
                        index = len(expected) - 1
                        if index >= len(pairs):
                            raise AssertionError("native hierarchy direction exchange is missing")
                        require_equal(
                            pairs[index][:2], expected[-1], "native hierarchy direction request"
                        )
                        values = [_edge(call[endpoint]) for call in pairs[index][2] or []]
                    projected[direction + "_calls"] = values
                    projected[direction + "_count"] = len(values)
        else:
            expected = [(method, located)]
            if not native:
                projected = {
                    "success": False,
                    "error": "Cannot rename symbol at this location",
                    "changes": [],
                    "total_changes": 0,
                }
            else:
                expected.append(
                    ("textDocument/rename", {**located, "newName": arguments["new_name"]})
                )
                if len(pairs) != 2:
                    raise AssertionError("native rename requires prepare and edit exchanges")
                token = native.get("placeholder")
                if token is None:
                    start, end = native["start"], native["end"]
                    if start["line"] != end["line"]:
                        raise AssertionError("fixture rename prepare range must select one token")
                    token = file.read_text().splitlines()[start["line"]][
                        start["character"] : end["character"]
                    ]
                require_equal(result.get("old_name"), token, "native rename prepare token fidelity")
                workspace_edit = pairs[1][2]
                rename_edits: list[tuple[str, list[JSON]]] = list(
                    workspace_edit.get("changes", {}).items()
                )
                for change in workspace_edit.get("documentChanges", []):
                    if set(change) != {"textDocument", "edits"}:
                        raise AssertionError(
                            "native rename preview cannot contain resource operations"
                        )
                    rename_edits.append((change["textDocument"]["uri"], change["edits"]))
                changes = [
                    {
                        "file": _file(uri),
                        "line": edit["range"]["start"]["line"] + 1,
                        "column": edit["range"]["start"]["character"] + 1,
                        "old_text": token,
                        "new_text": edit["newText"],
                    }
                    for uri, entries in rename_edits
                    for edit in entries
                ]
                if not changes or arguments.get("preview") is not True:
                    raise AssertionError(
                        "native positive rename requires nonempty explicit preview"
                    )
                projected = {
                    "success": True,
                    "old_name": token,
                    "new_name": arguments["new_name"],
                    "changes": changes,
                    "total_changes": len(changes),
                    "files_affected": len({entry["file"] for entry in changes}),
                    "applied": False,
                }
        require_equal([(m, p) for m, p, _ in pairs], expected, "native per-call request plan")
    require_equal(result, projected, "native/MCP result fidelity for " + tool)

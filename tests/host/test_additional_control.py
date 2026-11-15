"""Exercise strict live oracles and mocked runner guards, never live ALS proof."""

import copy
import shutil

import additional_oracles as oracle
import pytest
import real_additional as real


@pytest.fixture
def root(tmp_path):
    target = tmp_path / "fixture"
    shutil.copytree(real.FIXTURE, target)
    return target


def completions(changed=False):
    members = (
        [
            (
                "Merge",
                "function Merge (Left : Natural; Right : Natural; Extra : Natural) return Natural",
                5,
                2,
            ),
            ("Advance", "procedure Advance (Item : in out Natural)", 4, 1),
        ]
        if changed
        else [
            ("Combine", "function Combine (Left : Integer; Right : Integer) return Integer", 3, 1),
            ("Increment", "procedure Increment (Item : in out Integer)", 2, 2),
        ]
    )
    return {
        "completions": [
            {
                "label": name,
                "kind": "Function",
                "detail": f"Probe.{name}\n\n{declaration}",
                "documentation": f"at probe.ads ({line}:4)",
                "insert_text": name,
                "sort_text": f"25&0000{order}{name}",
            }
            for name, declaration, line, order in members
        ],
        "count": 2,
        "is_incomplete": False,
    }


def rename_result(root, new="Renamed_Counter", changed=False, cross=False):
    main, spec, body = (root / "src" / name for name in ("main.adb", "probe.ads", "probe.adb"))
    positions = (
        [(spec, 2, 14), (body, 2, 14), (body, 5, 8), (main, 6, 10)]
        if cross
        else [(main, 5, 4), (main, 7, 4), (main, 8, 19), (main, 9, 19)]
        if changed
        else [(main, 3, 4), (main, 5, 4), (main, 6, 21)]
    )
    old = "Increment" if cross else "Counter"
    return {
        "success": True,
        "old_name": old,
        "new_name": new,
        "changes": [
            {"file": str(file), "line": line, "column": column, "old_text": old, "new_text": new}
            for file, line, column in positions
        ],
        "total_changes": len(positions),
        "files_affected": 3 if cross else 1,
        "applied": False,
    }


def format_result(root):
    return {
        "formatted": True,
        "file": str(root / "formatting/uneven.adb"),
        "changes": 1,
        "edits": [
            {
                "start_line": 3,
                "start_column": 1,
                "end_line": 4,
                "end_column": 1,
                "new_text": "   null;\n",
            }
        ],
    }


def manifest_result(root, changed=False):
    # Literal fixture facts, independent of the production TOML parser.
    return {
        "is_alire_project": True,
        "name": "additional_probe",
        "version": "2.0.0" if changed else "1.2.3-dev",
        "description": "Exact metadata for the additional tool probe",
        "authors": ["Fixture Author"],
        "maintainers": ["Fixture Maintainer <fixture@example.invalid>"],
        "licenses": "MIT",
        "website": "https://example.invalid/additional-probe",
        "tags": ["fixture", "regression"],
        "dependencies": [{"name": "fixture_dependency", "version": "=4.2"}]
        if changed
        else [
            {"name": "fixture_dependency", "version": "^2.0"},
            {"name": "another_dependency", "version": "~3.1"},
        ],
        "build_profiles": {"*": "validation"},
        "gpr_externals": {"MODE": ["debug", "release"]},
        "gpr_set_externals": {"MODE": "release" if changed else "debug"},
        "executables": ["main"],
        "project_files": ["additional.gpr"],
        "alire_file": str(root / "manifest/alire.toml"),
    }


@pytest.mark.parametrize(
    "kind", ["empty", "wrong", "duplicate", "extra", "count", "boolean-count", "kind", "coordinate"]
)
def test_hierarchy_oracle_rejects_corruption(root, kind):
    spec = str(root / "src/probe.ads")
    edge = {"name": "Increment", "kind": 12, "file": spec, "line": 2, "column": 14}
    result = {
        "found": True,
        "symbol": "Main",
        "outgoing_calls": [edge],
        "incoming_calls": [],
        "outgoing_count": 1,
        "incoming_count": 0,
    }
    expected = {("Increment", 12, spec, 2, 14)}
    oracle.require_hierarchy(result, "Main", expected, set())
    if kind == "empty":
        result["outgoing_calls"] = []
    elif kind == "wrong":
        edge["name"] = "Unrelated"
    elif kind == "duplicate":
        result["outgoing_calls"] *= 2
    elif kind == "extra":
        result["incoming_calls"] = [copy.deepcopy(edge)]
    elif kind == "count":
        result["outgoing_count"] = 7
    elif kind == "boolean-count":
        result["outgoing_count"] = True
    elif kind == "kind":
        edge["kind"] = 13
    else:
        edge["column"] = 4
    with pytest.raises(AssertionError):
        oracle.require_hierarchy(result, "Main", expected, set())


@pytest.mark.parametrize(
    "field",
    [
        "label",
        "kind",
        "detail",
        "documentation",
        "insert_text",
        "count",
        "is_incomplete",
        "duplicate",
        "empty",
    ],
)
def test_completion_oracle_rejects_wrong_or_stale_members(field):
    result = completions()
    oracle.require_completions(result, False)
    if field in {"count", "is_incomplete"}:
        result[field] = 3 if field == "count" else True
    elif field == "duplicate":
        result["completions"][1] = copy.deepcopy(result["completions"][0])
    elif field == "empty":
        result["completions"] = []
    else:
        result["completions"][0][field] = "Unrelated"
    with pytest.raises(AssertionError):
        oracle.require_completions(result, False)
    with pytest.raises(AssertionError):
        oracle.require_completions(completions(), True)


@pytest.mark.parametrize(
    "field", ["active_parameter", "active_signature", "label", "parameters", "empty"]
)
def test_signature_oracle_rejects_native_wrong_selection_and_formals(field):
    result = {
        "found": True,
        "signatures": [
            {
                "label": "function Combine (Left : Integer; Right : Integer) return Integer",
                "documentation": "",
                "parameters": [
                    {"label": "Left", "documentation": ""},
                    {"label": "Right", "documentation": ""},
                ],
            }
        ],
        "active_signature": 0,
        "active_parameter": 1,
    }
    oracle.require_signature(result, False, 1)
    if field in {"active_parameter", "active_signature"}:
        result[field] = 0 if field == "active_parameter" else 1
    elif field == "empty":
        result["signatures"] = []
    elif field == "label":
        result["signatures"][0]["label"] = "function Other return Integer"
    else:
        result["signatures"][0]["parameters"].reverse()
    with pytest.raises(AssertionError):
        oracle.require_signature(result, False, 1)


@pytest.mark.parametrize(
    "kind",
    ["empty", "duplicate", "unrelated", "old-position", "wrong-text", "count", "files", "applied"],
)
def test_rename_oracle_rejects_bad_and_stale_preview_sets(root, kind):
    result = rename_result(root)
    expected = {
        (str(root / "src/main.adb"), line, column) for line, column in ((3, 4), (5, 4), (6, 21))
    }
    oracle.require_rename(result, "Counter", "Renamed_Counter", expected)
    if kind == "empty":
        result["changes"] = []
    elif kind == "duplicate":
        result["changes"][1] = copy.deepcopy(result["changes"][0])
    elif kind == "unrelated":
        result["changes"][0]["file"] = str(root / "src/unrelated.adb")
    elif kind == "old-position":
        result["changes"][0]["line"] = 5
    elif kind == "wrong-text":
        result["changes"][0]["new_text"] = "WRONG"
    elif kind == "count":
        result["total_changes"] = 2
    elif kind == "files":
        result["files_affected"] = 3
    else:
        result["applied"] = True
    with pytest.raises(AssertionError):
        oracle.require_rename(result, "Counter", "Renamed_Counter", expected)


@pytest.mark.parametrize(
    "kind",
    [
        "empty",
        "negative",
        "past-end",
        "reversed",
        "overlap",
        "no-op",
        "wrong-text",
        "file",
        "count",
        "boolean-position",
    ],
)
def test_formatting_oracle_rejects_invalid_edit_proposals(root, kind):
    result = format_result(root)
    file = root / "formatting/uneven.adb"
    assert (
        oracle.require_formatting(
            result, file, "procedure Uneven is\nbegin\n   null;\nend Uneven;\n"
        )
        == oracle.FORMATTED_UNEVEN
    )
    edit = result["edits"][0]
    if kind == "empty":
        result["edits"] = []
    elif kind == "negative":
        edit["start_column"] = -1
    elif kind == "past-end":
        edit["end_line"] = 99
    elif kind == "reversed":
        edit["start_line"], edit["end_line"] = 4, 3
    elif kind == "overlap":
        result["edits"] *= 2
        result["changes"] = 2
    elif kind == "no-op":
        edit["new_text"] = "null;\n"
    elif kind == "wrong-text":
        edit["new_text"] = "   WRONG;\n"
    elif kind == "file":
        result["file"] = str(root / "src/main.adb")
    elif kind == "count":
        result["changes"] = 9
    else:
        edit["start_column"] = True
    with pytest.raises(AssertionError):
        oracle.require_formatting(result, file, oracle.FORMATTED_UNEVEN)


@pytest.mark.parametrize(
    "field",
    [
        "name",
        "version",
        "description",
        "authors",
        "maintainers",
        "licenses",
        "website",
        "tags",
        "dependencies",
        "build_profiles",
        "gpr_externals",
        "gpr_set_externals",
        "executables",
        "project_files",
        "alire_file",
        "is_alire_project",
    ],
)
def test_manifest_oracle_checks_every_exposed_field(root, field):
    result = manifest_result(root)
    oracle.require_manifest(result, root)
    result[field] = "WRONG"
    with pytest.raises(AssertionError):
        oracle.require_manifest(result, root)
    with pytest.raises(AssertionError):
        oracle.require_manifest(manifest_result(root), root, True)


@pytest.mark.parametrize(
    "kind", ["empty", "count", "wrong-package", "missing-import", "extra-import", "wrong-file"]
)
def test_dependency_oracle_rejects_incomplete_or_unrelated_graphs(root, kind):
    result = {
        "dependencies": [
            {"package": "Main", "file": str(root / "src/main.adb"), "depends_on": ["Probe"]}
        ],
        "package_count": 3,
    }
    oracle.require_dependencies(result, root, 3, ["Probe"])
    if kind == "empty":
        result["dependencies"] = []
    elif kind == "count":
        result["package_count"] = 4
    elif kind == "wrong-package":
        result["dependencies"][0]["package"] = "Unrelated"
    elif kind == "missing-import":
        result["dependencies"][0]["depends_on"] = []
    elif kind == "extra-import":
        result["dependencies"][0]["depends_on"].append("Extra")
    else:
        result["dependencies"][0]["file"] = str(root / "src/probe.adb")
    with pytest.raises(AssertionError):
        oracle.require_dependencies(result, root, 3, ["Probe"])


@pytest.mark.parametrize("field", ["spec_file", "line", "column", "preview", "found"])
def test_spec_oracle_rejects_wrong_targets_and_fresh_preview_at_stale_location(root, field):
    spec = root / "src/probe.ads"
    result = {
        "found": True,
        "spec_file": str(spec),
        "line": 2,
        "column": 14,
        "preview": "procedure Increment (Item : in out Integer);",
    }
    oracle.require_spec(result, spec, 2, 14, result["preview"])
    result[field] = {
        "spec_file": str(root / "src/unrelated.adb"),
        "line": 1,
        "column": 4,
        "preview": "package Probe is",
        "found": False,
    }[field]
    with pytest.raises(AssertionError):
        oracle.require_spec(result, spec, 2, 14, "procedure Increment (Item : in out Integer);")


@pytest.mark.parametrize("kind", ["empty", "title", "kind", "count", "duplicate", "execute"])
def test_action_oracle_rejects_wrong_discovery_metadata(kind):
    result = {
        "actions": [
            {
                "title": title,
                "kind": action_kind,
                "is_preferred": False,
                "has_edit": False,
                "files_affected": 0,
                "command": "",
            }
            for title, action_kind in (
                ("Name parameters in the call", "refactor.rewrite"),
                ("Extract Procedure", "refactor.extract"),
                ("Extract Function", "refactor.extract"),
            )
        ],
        "count": 3,
    }
    oracle.require_actions(result, "call")
    if kind == "empty":
        result["actions"] = []
    elif kind in {"title", "kind"}:
        result["actions"][0][kind] = "Other"
    elif kind == "count":
        result["count"] = 2
    elif kind == "duplicate":
        result["actions"][1] = copy.deepcopy(result["actions"][0])
    else:
        result["actions"][0]["executed"] = True
    with pytest.raises(AssertionError):
        oracle.require_actions(result, "call")


@pytest.mark.parametrize(
    "field",
    [
        "project_file",
        "project_name",
        "source_dirs",
        "object_dir",
        "exec_dir",
        "main_units",
        "complete",
    ],
)
def test_project_oracle_rejects_missing_wrong_or_extra_view_fields(root, field):
    result = {
        "complete": True,
        "project_file": str(root / "additional.gpr"),
        "project_name": "Additional",
        "source_dirs": [str(root / "src"), str(root / "formatting")],
        "object_dir": str(root / "obj") + "/",
        "exec_dir": str(root / "bin"),
        "main_units": ["main.adb"],
    }
    oracle.require_project(result, root)
    del result[field]
    with pytest.raises((AssertionError, TypeError)):
        oracle.require_project(result, root)
    result[field] = "WRONG"
    with pytest.raises((AssertionError, TypeError)):
        oracle.require_project(result, root)


@pytest.mark.parametrize(
    "kind", ["status", "file", "line", "column", "message", "count", "empty", "output"]
)
def test_build_oracle_rejects_wrong_compiler_evidence(root, kind):
    main = root / "src/main.adb"
    main.write_bytes((root / "states/main-error.adb").read_bytes())
    result = {
        "gpr_file": str(root / "additional.gpr"),
        "success": False,
        "exit_code": 4,
        "errors": [
            {"file": "main.adb", "line": 3, "column": 25, "severity": "error", "message": message}
            for message in ('expected type "Standard.Integer"', "found a string type")
        ],
        "error_count": 2,
        "warnings": [],
        "warning_count": 0,
        "hints": [],
        "output": "actual compiler error text",
    }
    oracle.require_build(result, root, False)
    if kind == "status":
        result["exit_code"] = 0
    elif kind in {"file", "line", "column", "message"}:
        result["errors"][0][kind] = {
            "file": "unrelated.adb",
            "line": 4,
            "column": 1,
            "message": "unrelated compiler error",
        }[kind]
    elif kind == "count":
        result["error_count"] = 1
    elif kind == "empty":
        result["errors"] = []
    else:
        result["output"] = ""
    with pytest.raises(AssertionError):
        oracle.require_build(result, root, False)


def test_successful_build_requires_owned_executable(root):
    result = {
        "gpr_file": str(root / "additional.gpr"),
        "success": True,
        "exit_code": 0,
        "errors": [],
        "error_count": 0,
        "warnings": [],
        "warning_count": 0,
        "hints": [],
        "output": "",
    }
    with pytest.raises(AssertionError, match="owned executable"):
        oracle.require_build(result, root, True)
    executable = root / "bin/main"
    executable.parent.mkdir()
    executable.write_bytes(b"\x7fELFmock fixture, not a compiler result")
    executable.chmod(0o700)
    oracle.require_build(result, root, True)
    executable.write_text("not ELF\n")
    with pytest.raises(AssertionError, match="owned executable"):
        oracle.require_build(result, root, True)


@pytest.mark.parametrize(
    "kind",
    [
        "missing-request",
        "missing-reply",
        "extra-reply",
        "wrong-method",
        "wrong-view",
        "capability",
        "prepared-rename",
        "action-execution",
    ],
)
def test_native_trace_oracle_rejects_incomplete_or_wrong_capability_evidence(tmp_path, kind):
    from real_additional import require_trace

    root = tmp_path / "fixture"
    events = [
        {
            "event": "request",
            "id": 1,
            "method": "initialize",
            "params": {
                "rootUri": root.as_uri(),
                "initializationOptions": {"projectFile": str(root / "additional.gpr")},
            },
        },
        {
            "event": "result",
            "id": 1,
            "method": "initialize",
            "result": {
                "capabilities": {
                    "callHierarchyProvider": True,
                    "codeActionProvider": True,
                    "declarationProvider": True,
                    "documentFormattingProvider": True,
                    "completionProvider": {},
                    "signatureHelpProvider": {},
                    "renameProvider": {"prepareProvider": True},
                }
            },
        },
    ]
    require_trace(events, root)
    if kind == "missing-request":
        events.pop(0)
    elif kind == "missing-reply":
        events.pop()
    elif kind == "extra-reply":
        events.append(copy.deepcopy(events[-1]))
    elif kind == "wrong-method":
        events[-1]["method"] = "other-method"
    elif kind == "wrong-view":
        events[0]["params"]["rootUri"] = (root / "other").as_uri()
    elif kind == "capability":
        events[-1]["result"]["capabilities"]["callHierarchyProvider"] = False
    elif kind == "prepared-rename":
        events[-1]["result"]["capabilities"]["renameProvider"]["prepareProvider"] = False
    else:
        events.extend(
            [
                {
                    "event": "request",
                    "id": 2,
                    "method": "workspace/executeCommand",
                    "params": {"command": "als-named-parameters"},
                },
                {"event": "result", "id": 2, "method": "workspace/executeCommand", "result": None},
            ]
        )
    with pytest.raises(AssertionError):
        require_trace(events, root)

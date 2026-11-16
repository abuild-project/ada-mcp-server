"""Keep LSP effective selection independent from the production conversion."""

import copy

import pytest
import real_additional as real


def native_events(file, payload):
    """Supply one unchanged request and its native reply at the known cursor."""
    return [
        {
            "event": "request",
            "id": 1,
            "method": "textDocument/signatureHelp",
            "params": {
                "textDocument": {"uri": file.as_uri()},
                "position": {"line": 4, "character": 32},
            },
        },
        {"event": "result", "id": 1, "method": "textDocument/signatureHelp", "result": payload},
    ]


def known_native():
    """Exact original raw fields; declaration/formals come from the fixture source."""
    return {
        "signatures": [
            {
                "label": "function Combine (Left : Integer; Right : Integer) return Integer",
                "documentation": "",
                "parameters": [{"label": "Left"}, {"label": "Right"}],
                "activeParameter": 0,
            }
        ],
        "activeSignature": 0,
        "activeParameter": 0,
    }


def known_mcp(parameter=0):
    """The fixed source has two ordered formals, with Right at index one."""
    return {
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
        "active_parameter": parameter,
    }


@pytest.mark.parametrize(
    ("top_fields", "per_fields", "expected_signature", "expected_parameter"),
    [
        ({"activeParameter": 0}, [{"activeParameter": 1}], 0, 1),
        ({"activeParameter": 1}, [{"activeParameter": 0}], 0, 0),
        ({}, [{"activeParameter": 2}], 0, 2),
        ({"activeParameter": 1}, [{}], 0, 1),
        ({}, [{}], 0, 0),
        (
            {"activeSignature": 1, "activeParameter": 0},
            [{"activeParameter": 0}, {"activeParameter": 2}],
            1,
            2,
        ),
        ({"activeSignature": 9, "activeParameter": 0}, [{"activeParameter": 1}], 0, 1),
        ({"activeParameter": 9}, [{}], 0, 0),
    ],
    ids=[
        "per-one-top-zero",
        "per-zero-top-one",
        "no-top",
        "top-fallback",
        "default",
        "selected-second",
        "signature-default",
        "parameter-default",
    ],
)
def test_native_oracle_accepts_effective_lsp_selection(
    tmp_path, top_fields, per_fields, expected_signature, expected_parameter
):
    file = tmp_path / "main.adb"
    payload = {
        "signatures": [
            {
                "label": f"Overload_{index}",
                "parameters": [{"label": name} for name in ("Left", "Right", "Extra")],
                **fields,
            }
            for index, fields in enumerate(per_fields)
        ],
        **top_fields,
    }
    real.require_native_signature(
        native_events(file, payload),
        file,
        5,
        33,
        {"active_signature": expected_signature, "active_parameter": expected_parameter},
    )


def test_correct_effective_native_with_wrong_mcp_rejects_even_at_known_context(tmp_path):
    root = tmp_path / "fixture"
    file = root / "src/main.adb"
    payload = known_native()
    payload["signatures"][0]["activeParameter"] = 1
    with pytest.raises(
        AssertionError, match="MCP signature indices must equal effective native indices"
    ):
        real.require_known_positional_blocker(
            known_mcp(),
            native_events(file, payload),
            root,
            "positional-initial-1",
            file,
            5,
            33,
            False,
            1,
        )


def test_wrong_native_cannot_be_hidden_by_semantically_correct_mcp(tmp_path):
    file = tmp_path / "main.adb"
    with pytest.raises(
        AssertionError, match="MCP signature indices must equal effective native indices"
    ):
        real.require_native_signature(
            native_events(file, known_native()), file, 5, 33, known_mcp(1)
        )


@pytest.mark.parametrize(
    "variation",
    [
        "different-top",
        "missing-top",
        "missing-per",
        "missing-selected",
        "extra-field",
        "missing-label",
        "wrong-formals",
        "other-selected",
    ],
)
def test_known_blocker_rejects_unevidenced_raw_envelope(tmp_path, variation):
    root = tmp_path / "fixture"
    file = root / "src/main.adb"
    payload, result = known_native(), known_mcp()
    real.require_known_positional_blocker(
        result, native_events(file, payload), root, "positional-initial-1", file, 5, 33, False, 1
    )
    if variation == "different-top":
        payload["activeParameter"] = 1
    elif variation == "missing-top":
        del payload["activeParameter"]
    elif variation == "missing-per":
        del payload["signatures"][0]["activeParameter"]
    elif variation == "missing-selected":
        del payload["activeSignature"]
    elif variation == "extra-field":
        payload["new_native_field"] = True
    elif variation == "missing-label":
        del payload["signatures"][0]["label"]
    elif variation == "wrong-formals":
        payload["signatures"][0]["parameters"].reverse()
    else:
        payload["signatures"].append(copy.deepcopy(payload["signatures"][0]))
        payload["activeSignature"] = 1
        result["active_signature"] = 1
    with pytest.raises(AssertionError, match="original native defect envelope"):
        real.require_known_positional_blocker(
            result,
            native_events(file, payload),
            root,
            "positional-initial-1",
            file,
            5,
            33,
            False,
            1,
        )


@pytest.mark.parametrize("field", ["selected", "top", "per"])
@pytest.mark.parametrize("value", [None, False, True, "1", 1.0, -1])
def test_native_oracle_rejects_malformed_raw_indices_before_classification(tmp_path, field, value):
    file = tmp_path / "main.adb"
    payload = known_native()
    if field == "selected":
        payload["activeSignature"] = value
    elif field == "top":
        payload["activeParameter"] = value
    else:
        payload["signatures"][0]["activeParameter"] = value
    with pytest.raises(AssertionError):
        real.require_native_signature(native_events(file, payload), file, 5, 33, known_mcp())


def test_per_signature_out_of_range_is_unaccepted_without_invented_clamping(tmp_path):
    file = tmp_path / "main.adb"
    payload = known_native()
    payload["signatures"][0]["activeParameter"] = 9
    with pytest.raises(
        AssertionError, match="per-signature parameter outside its list remains unaccepted"
    ):
        real.require_native_signature(native_events(file, payload), file, 5, 33, known_mcp(9))


@pytest.mark.parametrize(
    "kind",
    [
        "active",
        "top-fallback",
        "top-overridden",
        "per-empty",
        "per-missing-parameters",
        "unselected-per",
    ],
)
@pytest.mark.parametrize("value", [2147483647, 2147483648])
def test_native_oracle_checks_complete_uinteger_domain_before_defaults(tmp_path, kind, value):
    payload = known_native()
    if kind == "active":
        payload["activeSignature"] = value
    elif kind == "top-fallback":
        del payload["signatures"][0]["activeParameter"]
        payload["activeParameter"] = value
    elif kind == "top-overridden":
        payload["activeParameter"] = value
    elif kind in {"per-empty", "per-missing-parameters"}:
        payload["signatures"][0]["activeParameter"] = value
        if kind == "per-empty":
            payload["signatures"][0]["parameters"] = []
        else:
            del payload["signatures"][0]["parameters"]
    else:
        payload["signatures"].append(copy.deepcopy(payload["signatures"][0]))
        payload["signatures"][1]["activeParameter"] = value
    file = tmp_path / "main.adb"
    parameter = value if kind.startswith("per-") else 0
    result = {"active_signature": 0, "active_parameter": parameter}
    if value == 2147483647:
        real.require_native_signature(native_events(file, payload), file, 5, 33, result)
    else:
        with pytest.raises(AssertionError):
            real.require_native_signature(native_events(file, payload), file, 5, 33, result)

"""Reject an always-clean diagnostic corruption before claiming real coverage."""

import copy

import pytest
import real_diagnostics


def clean():
    return {"complete": True, "scope": "file", "errorCount": 0, "totalCount": 0, "diagnostics": []}


def test_always_empty_publication_fails_both_malformed_states(tmp_path):
    source = tmp_path / "main.adb"
    for text, expect_errors in [
        (real_diagnostics.BROKEN, True),
        (real_diagnostics.REPAIRED, False),
        (real_diagnostics.BROKEN, True),
    ]:
        source.write_text(text)
        if expect_errors:
            with pytest.raises(AssertionError, match="nonempty syntax errors"):
                real_diagnostics.require_state(clean(), source, expect_errors=True)
        else:
            real_diagnostics.require_state(clean(), source, expect_errors=False)


def error_result(source):
    source.write_text(real_diagnostics.BROKEN)
    column = source.read_text().splitlines()[1].index(";") + 1
    return {
        "complete": True,
        "scope": "file",
        "errorCount": 1,
        "totalCount": 1,
        "diagnostics": [
            {
                "file": str(source),
                "line": 2,
                "column": column,
                "endLine": 2,
                "endColumn": column + 1,
                "severity": "error",
                "message": "Unexpected token ;",
            }
        ],
    }


def test_error_oracle_accepts_source_bound_message_and_rejects_stale_locations(tmp_path):
    source = tmp_path / "main.adb"
    result = error_result(source)
    real_diagnostics.require_state(result, source, expect_errors=True)
    wrong = copy.deepcopy(result)
    wrong["diagnostics"][0]["file"] = str(tmp_path / "other.adb")
    with pytest.raises(AssertionError, match="source semicolon"):
        real_diagnostics.require_state(wrong, source, expect_errors=True)
    source.write_text(real_diagnostics.REPAIRED)
    with pytest.raises(AssertionError, match="must clear"):
        real_diagnostics.require_state(result, source, expect_errors=False)


@pytest.mark.parametrize("changes", [{"complete": False}, {"scope": "workspace"}])
def test_incomplete_or_unscoped_cache_is_not_a_valid_control(tmp_path, changes):
    source = tmp_path / "main.adb"
    result = error_result(source)
    result.update(changes)
    with pytest.raises(AssertionError, match="complete file publication"):
        real_diagnostics.require_state(result, source, expect_errors=True)

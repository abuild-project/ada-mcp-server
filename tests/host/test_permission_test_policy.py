"""Check permission-test policy without changing the process identity."""

from types import SimpleNamespace

import pytest

from tests.host import test_additional_inspection as inspection


@pytest.mark.parametrize(
    ("uid", "required", "outcome"),
    [
        pytest.param(0, False, pytest.skip.Exception, id="root-local-skip"),
        pytest.param(0, True, pytest.fail.Exception, id="root-required-error"),
        pytest.param(1000, False, None, id="nonroot-local"),
        pytest.param(1000, True, None, id="nonroot-required"),
    ],
)
def test_permission_precondition(monkeypatch, uid, required, outcome):
    environment = {"ADA_MCP_REQUIRE_PERMISSION_TESTS": "1"} if required else {}
    monkeypatch.setattr(inspection, "os", SimpleNamespace(geteuid=lambda: uid, environ=environment))
    if outcome is None:
        assert inspection._require_nonroot_permissions() is None
    else:
        with pytest.raises(outcome, match="real nonroot identity"):
            inspection._require_nonroot_permissions()

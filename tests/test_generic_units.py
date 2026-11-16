"""Generic formals do not own the compilation unit's context imports."""

from pathlib import Path

import pytest

from ada_mcp.tools.project import handle_dependency_graph


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "declaration",
    [
        "generic\n   with -- formal, not the owner\n"
        "     function Less (Left, Right : Integer) return Boolean;\n"
        "package Owner is end Owner;\n",
        "generic\n   with procedure Touch (Value : Integer);\npackage Owner is end Owner;\n",
        "generic\n   with package Values is new Generic_Seed (<>);\npackage Owner is end Owner;\n",
        "generic\n   type Callback_Function is access function return Boolean;\n"
        "   type Protected_Predicate is access protected function return Boolean;\n"
        "package Owner is end Owner;\n",
        "generic\n   type Item is private;\nprocedure Owner (Value : Item);\n",
        "generic\n   type Item is private;\nfunction Owner return Item;\n",
        "procedure Owner is begin null; end Owner;\n",
    ],
    ids=[
        "formal-function-with-comment",
        "formal-procedure",
        "formal-package",
        "formal-access-profiles",
        "generic-procedure",
        "generic-function",
        "ordinary-procedure-body",
    ],
)
async def test_context_imports_belong_to_actual_unit(tmp_path, declaration):
    source = tmp_path / "owner.ads"
    source.write_text("with Ada.Text_IO;\nwith Generic_Seed;\n" + declaration)
    before = source.read_bytes()
    assert await handle_dependency_graph(str(source)) == {
        "dependencies": [
            {
                "package": "Owner",
                "file": str(source),
                "depends_on": ["Ada.Text_IO", "Generic_Seed"],
            }
        ],
        "package_count": 1,
    }
    assert source.read_bytes() == before


@pytest.mark.asyncio
async def test_generic_fixture_file_and_directory_owners():
    project = Path(__file__).parent / "fixtures" / "generic_project"
    source = project / "src" / "generic_probe.ads"
    before = {path: path.read_bytes() for path in project.rglob("*") if path.is_file()}
    expected = {
        "dependencies": [
            {
                "package": "Generic_Probe",
                "file": str(source),
                "depends_on": ["Ada.Text_IO", "Generic_Seed"],
            }
        ],
        "package_count": 1,
    }
    assert await handle_dependency_graph(str(source)) == expected
    assert await handle_dependency_graph(str(project / "src")) == {
        **expected,
        "package_count": 2,
    }
    assert {path: path.read_bytes() for path in before} == before

"""Exercise documentation checks through an owned minimal repository tree."""

import check_docs
import pytest


@pytest.fixture
def documents(tmp_path):
    for name in ("README.md", "AGENTS.md", "ROADMAP.md"):
        (tmp_path / name).write_text("# Maintained document\n")
    (tmp_path / "CHANGELOG.md").write_text("# Version 0.0.1\n")
    (tmp_path / "pyproject.toml").write_text(
        '[project.urls]\nHomepage = "https://github.com/abuild-project/ada-mcp-server"\n'
    )
    version = tmp_path / "src/ada_mcp/_version.py"
    version.parent.mkdir(parents=True)
    version.write_text('VERSION = "0.0.1"\n')
    records = tmp_path / "doc/change-records"
    records.mkdir(parents=True)
    (records / "bootstrap.md").write_text("# Bootstrap\n")
    (records / "reading.md").write_text("# Reading\n")
    (records / "README.md").write_text(
        "# Change records\n\n"
        "- [Bootstrap distribution](bootstrap.md)\n"
        "- [Bounded reading-tool regressions](reading.md)\n"
    )
    return tmp_path


def test_integrated_document_check_accepts_sorted_change_records(documents):
    check_docs.check_documents(documents)


def test_integrated_document_check_rejects_swapped_change_records(documents):
    index = documents / "doc/change-records/README.md"
    lines = index.read_text().splitlines(keepends=True)
    lines[-2:] = reversed(lines[-2:])
    index.write_text("".join(lines))
    with pytest.raises(ValueError, match="change-record index must be sorted by title"):
        check_docs.check_documents(documents)


def test_sorted_index_does_not_hide_a_broken_document_link(documents):
    (documents / "doc/change-records/bootstrap.md").unlink()
    with pytest.raises(ValueError, match="broken local documentation link"):
        check_docs.check_documents(documents)

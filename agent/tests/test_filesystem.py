import pytest
from kodra.engine.filesystem import FileSystemEngine
from kodra.security.policy import SecurityViolation


def test_file_create_read_modify_delete(tmp_path):
    fs = FileSystemEngine(tmp_path)

    # 1. Create file
    created = fs.create_file("sub/test.txt", "initial content")
    assert created.exists()
    assert fs.read_file("sub/test.txt") == "initial content"

    # 2. Modify file
    fs.modify_file("sub/test.txt", "updated content")
    assert fs.read_file("sub/test.txt") == "updated content"

    # 3. Diff
    diff = fs.get_diff("sub/test.txt", "new line\nupdated content")
    assert "+new line" in diff

    # 4. Delete file
    deleted = fs.delete_file("sub/test.txt")
    assert deleted is True
    assert not fs.file_exists("sub/test.txt")


def test_out_of_boundary_rejection(tmp_path):
    fs = FileSystemEngine(tmp_path)
    with pytest.raises(SecurityViolation):
        fs.create_file("../outside.txt", "bad")

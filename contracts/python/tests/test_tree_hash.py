from knowledge_workbench_contracts.tree_hash import compute_tree_hash


def test_tree_hash_is_deterministic(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    assert compute_tree_hash(tmp_path) == compute_tree_hash(tmp_path)


def test_tree_hash_changes_when_content_changes(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    h1 = compute_tree_hash(tmp_path)
    (tmp_path / "a.txt").write_text("goodbye")
    assert compute_tree_hash(tmp_path) != h1


def test_tree_hash_changes_when_a_file_is_added(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    h1 = compute_tree_hash(tmp_path)
    (tmp_path / "b.txt").write_text("world")
    assert compute_tree_hash(tmp_path) != h1


def test_tree_hash_is_insensitive_to_write_order(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    (tmp_path / "b.txt").write_text("world")
    h1 = compute_tree_hash(tmp_path)

    other = tmp_path.parent / "other_tree"
    other.mkdir()
    (other / "b.txt").write_text("world")
    (other / "a.txt").write_text("hello")
    h2 = compute_tree_hash(other)

    assert h1 == h2

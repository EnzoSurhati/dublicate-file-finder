"""Use temporary folders so tests don't touch personal files."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from duplicate_finder import find_duplicates


class DuplicateFinderTests(unittest.TestCase):
    def test_finds_nested_matches_but_not_same_size_different_contents(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "nested").mkdir()
            (root / "a.txt").write_bytes(b"hello")
            (root / "nested" / "b.txt").write_bytes(b"hello")
            (root / "different.txt").write_bytes(b"world")
            groups, warnings = find_duplicates(root)
            self.assertEqual(groups, [(5, sorted([root / "a.txt", root / "nested" / "b.txt"]))])
            self.assertEqual(warnings, [])

    def test_empty_files_count_as_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "a").touch()
            (root / "b").touch()
            groups, warnings = find_duplicates(root)
            self.assertEqual(len(groups), 1)
            self.assertEqual(groups[0][0], 0)
            self.assertFalse(warnings)

    def test_empty_folder_has_no_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(find_duplicates(Path(folder)), ([], []))

    def test_skips_symbolic_links(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "real.txt").write_text("hello")
            try:
                (root / "link.txt").symlink_to(root / "real.txt")
                (root / "loop").symlink_to(root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links aren't available on this system")
            self.assertEqual(find_duplicates(root), ([], []))

    def test_read_errors_are_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "a").write_bytes(b"hi")
            (root / "b").write_bytes(b"hi")
            with patch("duplicate_finder.file_hash", side_effect=PermissionError("access denied")):
                groups, warnings = find_duplicates(root)
            self.assertEqual(groups, [])
            self.assertEqual(len(warnings), 2)
            self.assertIn("access denied", warnings[0])


if __name__ == "__main__":
    unittest.main()

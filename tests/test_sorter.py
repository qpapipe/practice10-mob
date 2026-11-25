import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sorter import classify_file, build_plan, execute_plan

class SorterTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(classify_file(Path("notes.PDF")), "docs")
        self.assertEqual(classify_file(Path("photo.png")), "images")
        self.assertEqual(classify_file(Path("table.csv")), "tables")
        self.assertEqual(classify_file(Path("script.py")), "code")
        self.assertEqual(classify_file(Path("unknown.xyz")), "other")

    def test_empty_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(build_plan(Path(temp)), [])

    def test_plan_does_not_move_files(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "notes.txt"
            source.write_text("hello", encoding="utf-8")
            plan = build_plan(folder)
            self.assertEqual(len(plan), 1)
            self.assertTrue(source.exists())
            self.assertEqual(plan[0][1].parent.name, "docs")

    def test_execute_moves_file_and_creates_log(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "image.jpg"
            source.write_text("demo", encoding="utf-8")
            plan = build_plan(folder)
            results = execute_plan(plan, folder)
            self.assertEqual(results[0][1], "перемещён")
            self.assertTrue((folder / "images" / "image.jpg").exists())
            self.assertTrue((folder / "log.csv").exists())

    def test_invalid_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing"
            with self.assertRaises(ValueError):
                build_plan(missing)

if __name__ == "__main__":
    unittest.main()

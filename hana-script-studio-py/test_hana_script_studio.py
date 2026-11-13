"""Tests for the non-GUI part of hana_script_studio.py. Run: python -m unittest"""
import os
import tempfile
import unittest

from hana_script_studio import (ScriptDocument, ScriptEntry, ScriptLibrary, Settings,
                                find_modification_section)

SCRIPT = ("/* header */\n\n/* Modification section */\nSELECT\n  1 A\nFROM DUMMY\n"
          "/* Internal section (do not modify below this point) */\nSELECT 2;")


class SectionTests(unittest.TestCase):
    def test_range_between_modification_and_internal(self):
        self.assertEqual(find_modification_section(SCRIPT), (2, 5))

    def test_case_insensitive(self):
        self.assertEqual(find_modification_section(SCRIPT.upper()), (2, 5))

    def test_runs_to_end_without_internal_section(self):
        self.assertEqual(find_modification_section("a\n/* Modification section */\nb\nc"), (1, 3))

    def test_none_without_section(self):
        self.assertIsNone(find_modification_section(""))
        self.assertIsNone(find_modification_section("SELECT 1 FROM DUMMY"))


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def write(self, name, content, mode="w", **kw):
        path = os.path.join(self.dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode, **kw) as f:
            f.write(content)
        return path


class DocumentTests(TempDirCase):
    def test_edit_reset_save(self):
        path = self.write("a.txt", "original")
        doc = ScriptDocument(path)
        doc.text = "changed"
        self.assertTrue(doc.is_modified)
        self.assertEqual(open(path).read(), "original")  # disk untouched until save
        self.assertEqual(doc.reset(), "original")
        self.assertFalse(doc.is_modified)
        doc.text = "saved"
        doc.save()
        self.assertEqual(open(path).read(), "saved")
        self.assertFalse(doc.is_modified)

    def test_crlf_and_encoding_are_preserved(self):
        path = self.write("w.txt", b"line1\r\nline2 \xe9\r\n", mode="wb")  # cp1252 byte
        doc = ScriptDocument(path)
        self.assertEqual(doc.text, "line1\nline2 \u00e9\n")
        doc.text += "x"
        doc.save()
        self.assertEqual(open(path, "rb").read(), b"line1\r\nline2 \xe9\r\nx")


class BomTests(TempDirCase):
    def test_bom_is_kept_only_if_present(self):
        with_bom = self.write("a.txt", b"\xef\xbb\xbfabc", mode="wb")
        without = self.write("b.txt", b"abc", mode="wb")
        for path, expected in ((with_bom, b"\xef\xbb\xbfabcd"), (without, b"abcd")):
            doc = ScriptDocument(path)
            self.assertEqual(doc.text, "abc")
            doc.text += "d"
            doc.save()
            self.assertEqual(open(path, "rb").read(), expected)


class LibraryTests(TempDirCase):
    def test_load_and_search(self):
        self.write("HANA_Memory_Overview_2.00.040+.txt", "SELECT * FROM M_HOST_RESOURCE_UTILIZATION")
        self.write("sub/HANA_Locks_Overview.sql", "blocking transactions")
        self.write("readme.md", "memory")
        lib = ScriptLibrary.load(self.dir)
        self.assertEqual(len(lib.entries), 2)
        self.assertEqual(len(lib.search("")), 2)
        self.assertEqual(len(lib.search("MEMORY", name_only=True)), 1)
        self.assertEqual(len(lib.search("blocking")), 1)
        self.assertEqual(len(lib.search("blocking", name_only=True)), 0)
        self.assertEqual(len(lib.search("locks blocking")), 1)  # words may match name or content

    def test_entry_name_parts(self):
        e = ScriptEntry(os.path.join(self.dir, "sub", "HANA_Memory_Overview_2.00.040+.txt"), self.dir)
        self.assertEqual((e.prefix, e.base_name, e.version, e.folder), ("HANA_", "Memory_Overview", "2.00.040+", "sub"))


class SettingsTests(TempDirCase):
    def test_roundtrip_and_defaults(self):
        path = os.path.join(self.dir, "x", "settings.json")
        self.assertEqual(Settings.load(path), Settings())
        Settings(last_folder="C:/s", theme="dark", name_only=True).save(path)
        self.assertEqual(Settings.load(path), Settings("C:/s", "dark", True))

    def test_corrupt_file_gives_defaults(self):
        path = self.write("s.json", "{not json")
        self.assertEqual(Settings.load(path), Settings())


if __name__ == "__main__":
    unittest.main()

"""Tests for the non-GUI part of hana_script_studio.py. Run: python -m unittest"""
import os
import tempfile
import unittest

from hana_script_studio import (ScriptDocument, ScriptEntry, ScriptLibrary, Settings,
                                find_modification_section, match_spans)

# Shape of the real SAP scripts: the marker sits on the first parameter line and the
# section ends right before the first FROM.
SAP_SCRIPT = """SELECT
  *
FROM
( SELECT
    '%' HOST,                          /* Modification section */
    '%' PORT,
    'X' ONLY_MAIN,
    'PARAMETER, LAYER' AGGREGATE_BY    /* HOST, PORT or comma separated combinations */
  FROM
    DUMMY
) BI,
  M_CONFIGURATION_PARAMETER_VALUES P"""


class SectionTests(unittest.TestCase):
    def test_sap_script_ends_before_first_from(self):
        # marker on line 5 (index 4), last parameter on line 8 (index 7), FROM on index 8
        self.assertEqual(find_modification_section(SAP_SCRIPT), (4, 7))

    def test_from_before_the_marker_is_ignored(self):
        text = "SELECT 1\nFROM T\n/* Modification section */\nA,\nB\nFROM DUMMY"
        self.assertEqual(find_modification_section(text), (2, 4))

    def test_from_in_comment_or_string_does_not_end_section(self):
        text = ("/* Modification section */\n"
                "'from here' X,      /* starting from */\n"
                "-- from nowhere\n"
                "/* multi\n from line */ Y\n"
                "FROM DUMMY")
        self.assertEqual(find_modification_section(text), (0, 4))

    def test_from_on_the_same_line_as_last_parameter(self):
        text = "/* Modification section */\nA,\nB FROM DUMMY\nx"
        self.assertEqual(find_modification_section(text), (0, 2))

    def test_case_insensitive_and_crlf_free(self):
        self.assertEqual(find_modification_section("/* MODIFICATION SECTION */\n1 A\nfrom dummy"), (0, 1))

    def test_no_from_gives_only_marker_line(self):
        self.assertEqual(find_modification_section("a\n/* Modification section */\nb\nc"), (1, 1))

    def test_none_without_marker(self):
        self.assertIsNone(find_modification_section(""))
        self.assertIsNone(find_modification_section("SELECT 1 FROM DUMMY"))


class MatchSpanTests(unittest.TestCase):
    def test_spans_are_case_insensitive_and_merged(self):
        self.assertEqual(match_spans("HANA_Memory_Overview.txt", "memory over"), [(5, 11), (12, 16)])
        self.assertEqual(match_spans("memory_memory", "mem memory"), [(0, 6), (7, 13)])
        self.assertEqual(match_spans("abc", ""), [])


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


def read_file(path, mode="r"):
    with open(path, mode) as f:
        return f.read()


class DocumentTests(TempDirCase):
    def test_edit_reset_save(self):
        path = self.write("a.txt", "original")
        doc = ScriptDocument(path)
        doc.text = "changed"
        self.assertTrue(doc.is_modified)
        self.assertEqual(read_file(path), "original")  # disk untouched until save
        self.assertEqual(doc.reset(), "original")
        self.assertFalse(doc.is_modified)
        doc.text = "saved"
        doc.save()
        self.assertEqual(read_file(path), "saved")
        self.assertFalse(doc.is_modified)

    def test_crlf_and_encoding_are_preserved(self):
        path = self.write("w.txt", b"line1\r\nline2 \xe9\r\n", mode="wb")  # cp1252 byte
        doc = ScriptDocument(path)
        self.assertEqual(doc.text, "line1\nline2 \u00e9\n")
        doc.text += "x"
        doc.save()
        self.assertEqual(read_file(path, "rb"), b"line1\r\nline2 \xe9\r\nx")

    def test_bom_is_kept_only_if_present(self):
        with_bom = self.write("a.txt", b"\xef\xbb\xbfabc", mode="wb")
        without = self.write("b.txt", b"abc", mode="wb")
        for path, expected in ((with_bom, b"\xef\xbb\xbfabcd"), (without, b"abcd")):
            doc = ScriptDocument(path)
            self.assertEqual(doc.text, "abc")
            doc.text += "d"
            doc.save()
            self.assertEqual(read_file(path, "rb"), expected)


class LibraryTests(TempDirCase):
    def test_load_and_search_by_file_name_only(self):
        self.write("HANA_Memory_Overview_2.00.040+.txt", "SELECT memory FROM T")
        self.write("sub/HANA_Locks_Overview.sql", "blocking memory transactions")
        self.write("HANA_Disks.txt", "memory")
        self.write("readme.md", "memory")
        lib = ScriptLibrary.load(self.dir)
        self.assertEqual(len(lib.entries), 3)
        self.assertEqual(len(lib.search("")), 3)
        self.assertEqual([e.file_name for e in lib.search("MEMORY")], ["HANA_Memory_Overview_2.00.040+.txt"])
        self.assertEqual(len(lib.search("overview")), 2)
        self.assertEqual(len(lib.search("memory overview")), 1)  # every word must be in the name
        self.assertEqual(len(lib.search("blocking")), 0)  # content is not searched

    def test_entry_name_parts(self):
        e = ScriptEntry(os.path.join(self.dir, "sub", "HANA_Memory_Overview_2.00.040+.txt"), self.dir)
        self.assertEqual((e.prefix, e.base_name, e.version, e.folder), ("HANA_", "Memory_Overview", "2.00.040+", "sub"))


class SettingsTests(TempDirCase):
    def test_roundtrip_and_defaults(self):
        path = os.path.join(self.dir, "x", "settings.json")
        self.assertEqual(Settings.load(path), Settings())
        Settings(last_folder="C:/s", theme="dark").save(path)
        self.assertEqual(Settings.load(path), Settings("C:/s", "dark"))

    def test_old_keys_are_ignored_and_corrupt_file_gives_defaults(self):
        old = self.write("old.json", '{"last_folder": "C:/s", "name_only": true}')
        self.assertEqual(Settings.load(old), Settings(last_folder="C:/s"))
        self.assertEqual(Settings.load(self.write("s.json", "{not json")), Settings())


if __name__ == "__main__":
    unittest.main()

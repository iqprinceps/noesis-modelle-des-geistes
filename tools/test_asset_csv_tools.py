#!/usr/bin/env python3
"""Regression tests for the Pineal asset CSV preflight tools."""
from __future__ import annotations

import csv
import io
import pathlib
import tempfile
import unittest

from normalize_asset_csv import normalize_text
from validate_asset_csv import validate


class NormalizeAssetCsvTests(unittest.TestCase):
    def test_preserves_adjacent_source_and_download_urls(self) -> None:
        text = (
            "asset_id,source_page,download_url,status\n"
            "A1,https://example.test/article,https://example.test/article.pdf,VERIFIED\n"
        )
        normalized = normalize_text(text)
        self.assertEqual(
            list(csv.reader(io.StringIO(normalized))),
            list(csv.reader(io.StringIO(text))),
        )

    def test_refuses_ambiguous_unquoted_url_comma(self) -> None:
        text = "asset_id,source_url\nA1,https://example.test/File:a,b.jpg\n"
        with self.assertRaisesRegex(ValueError, "expected 2 fields"):
            normalize_text(text)


class ValidateAssetCsvTests(unittest.TestCase):
    def _validate_text(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir) / "manifest.csv"
            path.write_text(text, encoding="utf-8")
            return validate(path)

    def test_allows_descriptive_rights_and_known_machine_shape(self) -> None:
        errors = self._validate_text(
            "asset_id,rights_status,status\n"
            "A1,Verify exact Commons licence,ACQUIRE_VERIFY\n"
        )
        self.assertEqual(errors, [])

    def test_rejects_duplicate_id_and_non_machine_status(self) -> None:
        errors = self._validate_text(
            "asset_id,status\n"
            "A1,VERIFIED\n"
            "A1,Needs review\n"
        )
        self.assertTrue(any("duplicate asset_id" in error for error in errors))
        self.assertTrue(any("invalid machine status" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

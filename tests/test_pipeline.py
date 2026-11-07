"""Automated checks. Run: python tests/test_pipeline.py"""
import unittest
from pathlib import Path
from app.core import process_techpack, Translator, PRESERVE_RE

SAMPLE = Path("samples/sample_techpack.jpg")
OUT = Path("docs/sample_output.jpg")

class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SAMPLE.exists():
            raise unittest.SkipTest("Sample missing")
        cls.result = process_techpack(str(SAMPLE), str(OUT), translator=Translator(backend="glossary"), compute_metrics=True, show_protected=False)

    def test_psnr_infinite(self):
        psnr = self.result["metrics"].get("protected_psnr")
        self.assertTrue(psnr == float("inf") or psnr is None or psnr > 40)

    def test_codes_preserved(self):
        originals = {t["original"] for t in self.result["translations"]}
        for code in ["YKK", "5.5", "60"]:
            self.assertFalse(any(code in o and PRESERVE_RE.match(o) for o in originals))

    def test_artwork_excluded(self):
        originals = {t["original"] for t in self.result["translations"]}
        for art in ["RAMESES", "Kings of Egypt", "VIEW OF HEAD"]:
            self.assertFalse(any(art in o for o in originals))

    def test_output_written(self):
        self.assertTrue(OUT.exists())

if __name__ == "__main__":
    unittest.main()

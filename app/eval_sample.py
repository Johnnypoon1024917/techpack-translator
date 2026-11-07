"""
Reproducible check on the sample tech pack.
Run: python -m app.eval_sample
"""
from pathlib import Path
from collections import Counter
from app.core import process_techpack, Translator

def main():
    sample = Path("samples/sample_techpack.jpg")
    out = Path("docs/sample_output.jpg")
    if not sample.exists():
        print("Sample not found:", sample)
        return

    result = process_techpack(
        str(sample),
        str(out),
        translator=Translator(backend="glossary"),
        compute_metrics=True,
        show_protected=True,
    )

    print("=== Sample evaluation ===")
    print(f"Translated boxes : {result['translated']}")
    print(f"Flagged boxes    : {len(result['flagged'])}")
    print(f"Protected PSNR   : {result['metrics'].get('protected_psnr')}")
    print(f"Protected bbox   : {result['protected_bbox']}")
    print(f"Output written   : {out.exists()}")
    print()
    print("Example translations (first 15):")
    for t in result["translations"][:15]:
        print(f"  {t['original']!r:30} -> {t['translated']}")
    print()
    print("Flag reasons:")
    reasons = Counter(f.get("reason", "?") for f in result["flagged"])
    for r, n in reasons.most_common():
        print(f"  {r}: {n}")

if __name__ == "__main__":
    main()

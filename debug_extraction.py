"""
Debug script — run this BEFORE the app to diagnose extraction issues.
Place in project root (DocPilot/) and run: python debug_extraction.py
"""

import os
import sys
import platform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fix tesseract on Windows
if platform.system() == "Windows":
    try:
        import unstructured_pytesseract
        unstructured_pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )
    except ImportError:
        pass

from unstructured.partition.pdf import partition_pdf

# ---- CONFIG ----
IMAGE_OUT = "./raw_elements"
os.makedirs(IMAGE_OUT, exist_ok=True)

# ---- STEP 0: Find the PDF ----
print("\n=== Files in uploads/ ===")
if not os.path.exists("./uploads"):
    print("  ❌ uploads/ folder does not exist")
    sys.exit(1)

files = os.listdir("./uploads")
if not files:
    print("  ❌ uploads/ is empty — upload the PDF via the app first, then re-run this script")
    sys.exit(1)

for f in files:
    print(f"  {f}")

# Auto-pick the first PDF found
pdf_files = [f for f in files if f.lower().endswith(".pdf")]
if not pdf_files:
    print("  ❌ No PDF files found in uploads/")
    sys.exit(1)

PDF_PATH = os.path.join("./uploads", pdf_files[0])
print(f"\n  ✅ Using: {PDF_PATH}")
print(f"  File size: {os.path.getsize(PDF_PATH) / 1024:.1f} KB")

# ---- STEP 1: Try each strategy ----
for strategy in ["fast", "auto"]:
    print(f"\n=== Trying strategy='{strategy}' ===")
    try:
        raw_elements = partition_pdf(
            filename=PDF_PATH,
            strategy=strategy,
            extract_images_in_pdf=True,
            extract_image_block_output_dir=IMAGE_OUT
        )
        print(f"  Elements extracted: {len(raw_elements)}")

        if len(raw_elements) > 0:
            # Show unique class names and counts
            names = {}
            for el in raw_elements:
                n = type(el).__name__
                names[n] = names.get(n, 0) + 1

            print("  Class names found:")
            for name, count in sorted(names.items(), key=lambda x: -x[1]):
                print(f"    {name}: {count}")

            # Show first 3 elements with content
            print("  First 3 elements:")
            for el in raw_elements[:3]:
                print(f"    [{type(el).__name__}] {str(el)[:120]}")

            # Count what current TEXT_NAMES captures
            TEXT_NAMES = {"Text", "NarrativeText", "ListItem", "FigureCaption"}
            texts, tables, skipped = [], [], []
            for el in raw_elements:
                n = type(el).__name__
                if n in TEXT_NAMES:
                    texts.append(str(el))
                elif n == "Table":
                    tables.append(str(el))
                else:
                    skipped.append(n)

            print(f"\n  With TEXT_NAMES = {TEXT_NAMES}:")
            print(f"    texts captured  : {len(texts)}")
            print(f"    tables captured : {len(tables)}")
            print(f"    skipped types   : {set(skipped)}")

            if len(texts) == 0:
                print("\n  ❌ ZERO texts matched — class names in PDF don't match TEXT_NAMES")
                print("     Fix: add the names above to TEXT_NAMES in pdf_processor.py")
            else:
                print(f"\n  ✅ Text extraction working. First text preview:")
                print(f"     {texts[0][:200]}")

            break  # stop at first working strategy

        else:
            print(f"  ❌ strategy='{strategy}' returned 0 elements, trying next...")

    except Exception as e:
        print(f"  ❌ strategy='{strategy}' threw error: {type(e).__name__}: {e}")

print("\n=== Done ===")
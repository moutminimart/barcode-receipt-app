import streamlit as st
from PIL import Image
import easyocr
from pyzbar.pyzbar import decode
from rapidfuzz import fuzz
import pandas as pd
import re

st.title("📦 Barcode + Receipt Matcher (V2)")

reader = easyocr.Reader(['th','en'])

# Upload
product_images = st.file_uploader("Upload Product Images", accept_multiple_files=True)
receipt_image = st.file_uploader("Upload Receipt Image")

# --- Barcode ---
def extract_barcodes(image):
    decoded = decode(image)
    return [d.data.decode("utf-8") for d in decoded]

# --- OCR ---
import numpy as np

def extract_text(image):
    img = Image.open(image)
    img = np.array(img)
    
    results = reader.readtext(img)
    return "\n".join([r[1] for r in results])

# --- Parse receipt ---
def parse_receipt(text):
    items = []
    lines = text.split("\n")

    for line in lines:
        match = re.search(r'(.+?)\s+(\d+)\s+([\d\.]+)', line)
        if match:
            items.append({
                "name": match.group(1).strip(),
                "qty": int(match.group(2)),
                "price": float(match.group(3))
            })
    return items

# --- Matching ---
def match_products(barcodes, items):
    results = []

    for bc in barcodes:
        best = None
        best_score = 0

        for item in items:
            score = fuzz.partial_ratio(bc, item["name"])

            if score > best_score:
                best = item
                best_score = score

        results.append({
            "barcode": bc,
            "matched_item": best["name"] if best else "Not found",
            "qty": best["qty"] if best else "-",
            "price": best["price"] if best else "-",
            "confidence": best_score
        })

    return results

# --- MAIN ---
if st.button("🚀 Process"):
    if not product_images or not receipt_image:
        st.warning("Please upload all images")
    else:
        all_barcodes = []

        st.subheader("📦 Detected Barcodes")
        for file in product_images:
            img = Image.open(file)
            barcodes = extract_barcodes(img)

            for b in barcodes:
                st.write(b)
                all_barcodes.append(b)

        st.subheader("🧾 Reading Receipt...")
        receipt_text = extract_text(receipt_image)

        items = parse_receipt(receipt_text)

        st.subheader("🧾 Parsed Receipt Items")
        st.write(items)

        matched = match_products(all_barcodes, items)

        st.subheader("🔗 Matching Result")
        df = pd.DataFrame(matched)
        st.dataframe(df)

        st.success("Done ✅")

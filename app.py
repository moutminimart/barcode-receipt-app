import streamlit as st
from PIL import Image
import pytesseract
from pyzbar.pyzbar import decode

st.title("📦 Barcode + Receipt Matcher")

# Upload files
product_images = st.file_uploader("Upload Product Images", accept_multiple_files=True)
receipt_image = st.file_uploader("Upload Receipt Image")

def read_barcode(image):
    decoded = decode(image)
    return [d.data.decode("utf-8") for d in decoded]

def read_receipt(image):
    return pytesseract.image_to_string(image)

if st.button("Process"):
    if not product_images or not receipt_image:
        st.warning("Please upload all images")
    else:
        st.subheader("📦 Products")
        product_data = []

        for file in product_images:
            img = Image.open(file)
            barcodes = read_barcode(img)

            for b in barcodes:
                st.write(f"Barcode: {b}")
                product_data.append(b)

        st.subheader("🧾 Receipt Text")
        receipt_text = read_receipt(Image.open(receipt_image))
        st.text(receipt_text)

        st.success("Processing complete (basic version)")

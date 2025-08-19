import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from PIL import Image

# Register Gujarati font (works for Unicode)
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

st.title("🪔 Navratri Pass Generator")

# Upload Template
template_file = st.file_uploader("Upload PDF Template (with 6 passes)", type=["pdf"])

if template_file:
    st.success("Template uploaded ✅")

    photos, numbers, names = [], [], []
    st.subheader("Enter Pass Details")

    for i in range(6):
        st.markdown(f"### Pass {i+1}")
        photos.append(st.file_uploader(f"Photo for Pass {i+1}", type=["jpg","png"], key=f"p{i}"))
        num = st.number_input(f"Pass Number (0–9999) for Pass {i+1}", min_value=0, max_value=9999, value=i)
        numbers.append(f"{num:04d}")
        names.append(st.text_input(f"Athlete Name (Gujarati) for Pass {i+1}", key=f"n{i}"))

    if st.button("🎉 Generate Passes"):
        reader = PdfReader(template_file)
        template_page = reader.pages[0]

        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)

        # Dummy coordinates (we’ll fix later)
        photo_coords = [(60, 630), (300, 630), (540, 630),
                        (60, 300), (300, 300), (540, 300)]
        num_coords   = [(60, 600), (300, 600), (540, 600),
                        (60, 270), (300, 270), (540, 270)]
        name_coords  = [(60, 580), (300, 580), (540, 580),
                        (60, 250), (300, 250), (540, 250)]

        for i in range(6):
            if photos[i]:
                img = Image.open(photos[i])
                img = img.resize((100,100))
                can.drawImage(ImageReader(img), *photo_coords[i], 100, 100)

            can.setFillColorRGB(0,1,0)  # Green for number
            can.setFont("Helvetica-Bold", 14)
            can.drawString(*num_coords[i], numbers[i])

            can.setFillColorRGB(0,0,1)  # Blue for name
            can.setFont("STSong-Light", 14)
            can.drawString(*name_coords[i], names[i])

        can.save()
        packet.seek(0)
        overlay_pdf = PdfReader(packet)

        writer = PdfWriter()
        page = template_page
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        st.download_button("📥 Download Passes", output.getvalue(), "Navratri_Passes.pdf")

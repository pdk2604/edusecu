import hashlib
import qrcode
from PIL import Image
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfReader, PdfWriter

# 1. Générer le hash SHA-256 du fichier
def get_file_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

# 2. Uploader le fichier en ligne (via transfer.sh)
def upload_file(file_path):
    with open(file_path, "rb") as f:
        response = requests.put(f"https://transfer.sh/{file_path.split('/')[-1]}", data=f)
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise Exception("Échec de l'upload du fichier")

# 3. Générer un QR code (à partir d'un lien)
def generate_qr_code(link, output_path="qrcode.png"):
    qr = qrcode.make(link)
    qr.save(output_path)
    return output_path

# 4. Insérer QR comme filigrane sur une image
def add_qr_watermark(image_path, qr_path, output_path="output.png"):
    base_img = Image.open(image_path).convert("RGBA")
    qr_img = Image.open(qr_path).convert("RGBA")

    qr_img = qr_img.resize((150, 150))
    position = (base_img.width - qr_img.width - 10, base_img.height - qr_img.height - 10)
    base_img.paste(qr_img, position, qr_img)

    base_img.save(output_path)
    return output_path

# 5. Insérer QR comme filigrane dans un PDF
def add_qr_watermark_to_pdf(pdf_path, qr_path, output_path="output.pdf"):
    watermark_path = "temp_watermark.pdf"
    c = canvas.Canvas(watermark_path, pagesize=A4)
    c.drawImage(qr_path, 400, 50, width=150, height=150)
    c.save()

    pdf = PdfReader(open(pdf_path, "rb"))
    watermark = PdfReader(open(watermark_path, "rb"))
    writer = PdfWriter()

    for page in pdf.pages:
        page.merge_page(watermark.pages[0])
        writer.add_page(page)

    with open(output_path, "wb") as f_out:
        writer.write(f_out)

    return output_path

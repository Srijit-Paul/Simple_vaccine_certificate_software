from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import qrcode
import json
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import textwrap
class CertificateManager:
    def __init__(self, credentials_path, folder_id):
        self.SCOPES = ["https://www.googleapis.com/auth/drive.file"]
        self.folder_id = folder_id
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=self.SCOPES
        )
        self.drive_service = build("drive", "v3", credentials=self.credentials)

    def generate_pdf_certificate(self, certificate_data, qr_image_path, pdf_filename):
        """Generate a PDF certificate with a layout matching the provided format."""
        c = canvas.Canvas(pdf_filename, pagesize=A4)
        width, height = A4

        # Helper function for drawing lines
        def draw_line(y_position):
            c.line(50, y_position, width-50, y_position)

        # Set up default font
        c.setFont("Helvetica-Bold", 16)
        
        # Header - Print Report
        c.drawString(50, height-50, "Print Report")
        draw_line(height-60)
        
        # Patient Information Section
        c.setFont("Helvetica", 12)
        y = height-90
        
        # First row
        c.drawString(50, y, f"Patient Name: {certificate_data.get('Full Name', '')}")
        c.drawString(400, y, f"Age: {certificate_data.get('Age', '')}Y")
        
        # Second row
        y -= 25
        c.drawString(50, y, f"Invoice No: {certificate_data.get('Certificate ID', '')}")
        c.drawString(300, y, f"Invoice Date: {certificate_data.get('Date', '')}")
        c.drawString(500, y, f"Gender: {certificate_data.get('Gender', '')}")
        
        # Third row
        y -= 25
        c.drawString(50, y, f"Referred By: {certificate_data.get('Referred By', '')}")
        
        # Title
        y -= 40
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Vaccination Certificate of " + certificate_data.get('Vaccine Name', ''))
        
        # Additional Information
        y -= 30
        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Facility: {certificate_data.get('Facility', '')}")
        c.drawString(300, y, f"Mode: {certificate_data.get('Mode', '')}")
        
        y -= 25
        c.drawString(50, y, f"Case ID: {certificate_data.get('Certificate ID', '')}")
        c.drawString(300, y, f"Mobile: {certificate_data.get('Mobile', '')}")
        
        y -= 25
        c.drawString(50, y, f"Passport: {certificate_data.get('Passport', '')}")
        c.drawString(300, y, f"NID No: {certificate_data.get('NID', '')}")
        
        y -= 25
        c.drawString(50, y, f"Address: {certificate_data.get('Address', '')}")
        
        # Vaccine Information Table
        y -= 50
        c.setFont("Helvetica-Bold", 12)
        table_headers = ["Name of Vaccine", "Number of Dose", "Given date", "Batch NO", "Exp. Date", "Mfg Date", "Mfg By"]
        x_positions = [50, 200, 300, 400, 470, 540, 610]
        
        # Draw headers
        for header, x in zip(table_headers, x_positions):
            c.drawString(x, y, header)
        
        # Draw table data
        y -= 25
        c.setFont("Helvetica", 10)
        c.drawString(50, y, certificate_data.get('Vaccine Name', ''))
        c.drawString(200, y, certificate_data.get('Dose Information', ''))
        c.drawString(300, y, certificate_data.get('Date', ''))
        c.drawString(400, y, certificate_data.get('Batch', ''))
        c.drawString(470, y, certificate_data.get('Exp Date', ''))
        c.drawString(540, y, certificate_data.get('Mfg Date', ''))
        c.drawString(610, y, certificate_data.get('Manufacturer', ''))
        
        # Draw lines around table
        draw_line(y+35)  # Top line
        draw_line(y-5)   # Bottom line
        
        # To Whom It May Concern section
        y -= 50
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "To Whom It May Concern")
        
        y -= 25
        c.setFont("Helvetica", 11)
        concern_text = (
            f"This is to certify that {certificate_data.get('Full Name', '')}, "
            f"Date of Birth: {certificate_data.get('DOB', '')}, {certificate_data.get('Nationality', 'Bangladesh')} citizen, "
            f"Passport No: {certificate_data.get('Passport', '')} has been vaccinated with {certificate_data.get('Vaccine Name', '')}. "
            "We wish them all the best for their future endeavors."
        )
        
        # Word wrap the concern text
        text_object = c.beginText(50, y)
        text_object.setFont("Helvetica", 11)
        wrapped_text = "\n".join(textwrap.wrap(concern_text, width=90))
        for line in wrapped_text.split('\n'):
            text_object.textLine(line)
        c.drawText(text_object)
        
        # Footer text
        y = 50
        c.setFont("Helvetica", 8)
        footer_text = (
            "This report has been issued electronically. Any party that relies on the result of this report "
            "should first check its authenticity by contacting the issuing authority. "
            "The authority is not responsible for any misuse of this report or its contents."
        )
        text_object = c.beginText(50, y)
        wrapped_text = "\n".join(textwrap.wrap(footer_text, width=100))
        for line in wrapped_text.split('\n'):
            text_object.textLine(line)
        c.drawText(text_object)
        
        # Add QR code on the right side
        qr_size = 100
        c.drawImage(qr_image_path, width-150, 50, width=qr_size, height=qr_size)
        
        c.save()

    def upload_to_drive(self, file_path, file_name):
        """Upload file to Google Drive and return public link."""
        file_metadata = {
            "name": file_name,
            "mimeType": "application/pdf",
            "parents": [self.folder_id]
        }

        media = MediaFileUpload(file_path, mimetype="application/pdf")
        file = self.drive_service.files().create(
            body=file_metadata, 
            media_body=media,
            fields="id"
        ).execute()

        file_id = file.get("id")

        # Make file public
        permission = {"role": "reader", "type": "anyone"}
        self.drive_service.permissions().create(
            fileId=file_id, 
            body=permission
        ).execute()

        return f"https://drive.google.com/file/d/{file_id}/view"

    def generate_qr_code(self, data, output_path):
        """Generate QR code from data and save to output path."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image.save(output_path)
        return output_path

    def process_certificate(self, certificate_data):
        """Process certificate data and generate all necessary files."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        cert_id = certificate_data.get('Certificate ID', 'unknown')
        
        # Create output directory if it doesn't exist
        output_dir = "certificates"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate file paths
        pdf_filename = f"{output_dir}/Vaccine_Certificate_{cert_id}_{timestamp}.pdf"
        temp_qr_path = f"{output_dir}/temp_qr_{cert_id}_{timestamp}.png"
        
        # First generate a temporary QR code with certificate data
        self.generate_qr_code(json.dumps(certificate_data), temp_qr_path)
        
        # Generate the initial PDF
        self.generate_pdf_certificate(certificate_data, temp_qr_path, pdf_filename)
        
        # Upload to Drive
        drive_link = self.upload_to_drive(pdf_filename, os.path.basename(pdf_filename))
        
        # Update certificate data with drive link
        certificate_data['drive_link'] = drive_link
        
        # Generate final QR code with drive link
        final_qr_path = f"{output_dir}/qr_{cert_id}_{timestamp}.png"
        self.generate_qr_code(drive_link, final_qr_path)
        
        # Generate final PDF with the drive-link QR code
        final_pdf_path = pdf_filename  # Overwrite the original PDF
        self.generate_pdf_certificate(certificate_data, final_qr_path, final_pdf_path)
        
        # Clean up temporary QR code
        os.remove(temp_qr_path)
        
        return {
            'pdf_path': final_pdf_path,
            'qr_path': final_qr_path,
            'drive_link': drive_link
        }
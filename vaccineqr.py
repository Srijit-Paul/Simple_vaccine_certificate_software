import tkinter as tk
from tkinter import messagebox, filedialog
import json
import qrcode
from PIL import Image, ImageTk
import cv2
from pyzbar.pyzbar import decode
import threading
import os
import datetime

# Import ReportLab for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# Global list to store generated certificates (if you want to keep track in memory)
generated_certificates = []  # each element is a dict containing certificate data and pdf filename

class VaccineCertApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vaccine Certification Application")
        self.geometry("700x700")
        self.resizable(False, False)
        
        # Create navigation and two main frames (Generate and Scan)
        self.create_widgets()
    
    def create_widgets(self):
        # Navigation buttons to switch between modes
        nav_frame = tk.Frame(self)
        nav_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.btn_generate_tab = tk.Button(nav_frame, text="Generate Certificate", command=self.show_generate)
        self.btn_generate_tab.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.btn_scan_tab = tk.Button(nav_frame, text="Scan Certificate", command=self.show_scan)
        self.btn_scan_tab.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Create frames for each mode
        self.frame_generate = tk.Frame(self)
        self.frame_scan = tk.Frame(self)
        
        self.create_generate_frame()
        self.create_scan_frame()
        
        # Start with the generation frame visible
        self.frame_generate.pack(fill=tk.BOTH, expand=True)
    
    def create_generate_frame(self):
        header = tk.Label(self.frame_generate, text="Enter Certificate Details", font=("Arial", 18))
        header.pack(pady=10)
        
        # Create entries for certificate details
        self.entries = {}
        fields = [
            "Full Name", 
            "Certificate ID", 
            "Vaccine Name", 
            "Dose Information", 
            "Date (YYYY-MM-DD)"
        ]
        for field in fields:
            row = tk.Frame(self.frame_generate)
            row.pack(pady=5, padx=10, fill=tk.X)
            label = tk.Label(row, text=field + ":", width=20, anchor="w", font=("Arial", 12))
            label.pack(side=tk.LEFT)
            entry = tk.Entry(row, width=40, font=("Arial", 12))
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.entries[field] = entry
        
        self.btn_generate_qr = tk.Button(self.frame_generate, text="Generate Certificate", command=self.generate_certificate, font=("Arial", 12))
        self.btn_generate_qr.pack(pady=10)
        
        # Label to display the generated QR code image
        self.label_qr = tk.Label(self.frame_generate)
        self.label_qr.pack(pady=10)
    
    def create_scan_frame(self):
        header = tk.Label(self.frame_scan, text="Scan Certificate QR Code", font=("Arial", 18))
        header.pack(pady=10)
        
        self.btn_start_scan = tk.Button(self.frame_scan, text="Start Scanning", command=self.start_scanning, font=("Arial", 12))
        self.btn_start_scan.pack(pady=10)
        
        # Text widget to show the decoded certificate details
        self.text_scan_result = tk.Text(self.frame_scan, height=10, width=80, font=("Arial", 12))
        self.text_scan_result.pack(pady=10)
    
    def show_generate(self):
        self.frame_scan.pack_forget()
        self.frame_generate.pack(fill=tk.BOTH, expand=True)
    
    def show_scan(self):
        self.frame_generate.pack_forget()
        self.frame_scan.pack(fill=tk.BOTH, expand=True)
    
    def generate_certificate(self):
        # Gather certificate data from the input fields
        certificate = {
            "Full Name": self.entries["Full Name"].get(),
            "Certificate ID": self.entries["Certificate ID"].get(),
            "Vaccine Name": self.entries["Vaccine Name"].get(),
            "Dose Information": self.entries["Dose Information"].get(),
            "Date": self.entries["Date (YYYY-MM-DD)"].get()
        }
        
        # Validate that all fields are filled
        if not all(certificate.values()):
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        
        # Convert certificate data to JSON string to store in the QR code
        data_json = json.dumps(certificate)
        
        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,  # adjust if needed
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(data_json)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save temporary QR image file
        temp_qr_filename = "temp_qr.png"
        qr_img.save(temp_qr_filename)
        
        # Resize the image for display in the GUI
        qr_image = Image.open(temp_qr_filename)
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.ANTIALIAS  # fallback for older Pillow versions
        qr_image = qr_image.resize((250, 250), resample)
        self.qr_photo = ImageTk.PhotoImage(qr_image)
        self.label_qr.config(image=self.qr_photo)
        
        # Generate a professional PDF certificate containing the details and QR code.
        # The PDF file name includes a timestamp.
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"Vaccine_Certificate_{certificate['Certificate ID']}_{timestamp}.pdf"
        self.generate_pdf_certificate(certificate, temp_qr_filename, pdf_filename)
        
        # Save the certificate in our in-memory array (if needed)
        generated_certificates.append({
            "data": certificate,
            "pdf": pdf_filename
        })
        
        messagebox.showinfo("Certificate Generated", f"Certificate PDF generated and saved as:\n{pdf_filename}")
    
    def generate_pdf_certificate(self, certificate, qr_image_filename, pdf_filename):
        """
        Generates a PDF certificate using ReportLab.
          - certificate: a dict containing certificate data.
          - qr_image_filename: path to the QR code image.
          - pdf_filename: the output PDF file name.
        """
        # Create a canvas for an A4 size page
        c = canvas.Canvas(pdf_filename, pagesize=A4)
        width, height = A4  # A4 page size
        
        # Draw a header
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 50, "Vaccine Certificate")
        
        # Draw certificate details
        c.setFont("Helvetica", 14)
        start_y = height - 100
        line_gap = 25
        for i, (key, value) in enumerate(certificate.items()):
            text = f"{key}: {value}"
            c.drawString(50, start_y - i * line_gap, text)
        
        # Insert the QR code image on the right side
        # (Place it at x=width-200, y position calculated so that it fits)
        qr_size = 150  # size in points (1 point = 1/72 inch)
        c.drawImage(qr_image_filename, width - 200, start_y - qr_size, width=qr_size, height=qr_size)
        
        # Add a footer if desired
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(width/2, 30, "This certificate is generated by Vaccine Certification App")
        
        c.showPage()
        c.save()
    
    def start_scanning(self):
        # Run scanning in a separate thread so that the GUI remains responsive
        threading.Thread(target=self.scan_qr, daemon=True).start()
    
    def scan_qr(self):
        cap = cv2.VideoCapture(0)  # open the default webcam
        found = False
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            # Decode any QR code in the frame
            for barcode in decode(frame):
                qr_data = barcode.data.decode("utf-8")
                try:
                    certificate = json.loads(qr_data)
                    # Prepare a string for display
                    result_text = "Certificate Details:\n"
                    for key, value in certificate.items():
                        result_text += f"{key}: {value}\n"
                    
                    # Display in the text widget on the scan frame
                    self.text_scan_result.delete(1.0, tk.END)
                    self.text_scan_result.insert(tk.END, result_text)
                    
                    # Save a PDF certificate for the scanned data
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    pdf_filename = f"Scanned_Certificate_{certificate.get('Certificate ID','unknown')}_{timestamp}.pdf"
                    
                    # First, generate a temporary QR code image for the scanned data (so that the PDF contains it)
                    temp_qr_filename = "temp_scanned_qr.png"
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4
                    )
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_img.save(temp_qr_filename)
                    
                    self.generate_pdf_certificate(certificate, temp_qr_filename, pdf_filename)
                    
                    # Let the user know the PDF has been saved.
                    messagebox.showinfo("Certificate Scanned", f"Certificate PDF generated and saved as:\n{pdf_filename}")
                    
                    found = True
                    break
                except Exception as e:
                    self.text_scan_result.delete(1.0, tk.END)
                    self.text_scan_result.insert(tk.END, "Error decoding QR code: " + str(e))
            # Show the webcam feed in an OpenCV window
            cv2.imshow("QR Scanner - Press 'q' to stop", frame)
            if found or cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = VaccineCertApp()
    app.mainloop()

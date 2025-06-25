import tkinter as tk
from tkinter import ttk, messagebox
import json
import cv2
from pyzbar.pyzbar import decode
import threading
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import os
from certificate_manager import CertificateManager

class VaccineCertApp(tk.Tk):
    def __init__(self, cert_manager):
        super().__init__()
        self.cert_manager = cert_manager
        self.title("Vaccine Certification System")
        self.geometry("800x800")
        self.configure(bg='#f0f0f0')
        
        # Predefined vaccines list
        self.vaccine_list = [
            "Quadrivalent Neisseria Meningitis Meningococal",
            "COVID-19 Vaccine",
            "Influenza Vaccine",
            "Hepatitis B Vaccine",
            "Yellow Fever Vaccine",
            "Other (Please Specify)"
        ]
        
        # Create and pack the main container
        self.main_container = tk.Frame(self, bg='#f0f0f0')
        self.main_container.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Style constants
        btn_style = {'font': ('Arial', 12), 'bg': '#4a90e2', 'fg': 'white', 
                    'padx': 20, 'pady': 10, 'bd': 0}
        label_style = {'font': ('Arial', 12), 'bg': '#f0f0f0'}
        entry_style = {'font': ('Arial', 12), 'bd': 1, 'relief': tk.SOLID}
        
        # Navigation buttons
        nav_frame = tk.Frame(self.main_container, bg='#f0f0f0')
        nav_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.btn_generate_tab = tk.Button(nav_frame, text="Generate Certificate",
                                        command=self.show_generate, **btn_style)
        self.btn_generate_tab.pack(side=tk.LEFT, expand=True, padx=5)
        
        self.btn_scan_tab = tk.Button(nav_frame, text="Scan Certificate",
                                    command=self.show_scan, **btn_style)
        self.btn_scan_tab.pack(side=tk.LEFT, expand=True, padx=5)
        
        # Create main frames
        self.frame_generate = tk.Frame(self.main_container, bg='#f0f0f0')
        self.frame_scan = tk.Frame(self.main_container, bg='#f0f0f0')
        
        self.create_generate_frame()
        self.create_scan_frame()
        
        # Start with generate frame
        self.show_generate()

    def create_generate_frame(self):
        # Header
        tk.Label(self.frame_generate, text="Certificate Details",
                font=('Arial', 18, 'bold'), bg='#f0f0f0').pack(pady=(0, 20))
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(self.frame_generate, bg='#f0f0f0')
        scrollbar = tk.Scrollbar(self.frame_generate, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Entry fields
        self.entries = {}
        
        # Personal Information Section
        tk.Label(scrollable_frame, text="Personal Information", font=('Arial', 14, 'bold'), 
                bg='#f0f0f0').grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky='w')
        
        current_row = 1
        
        # Basic Info Fields
        basic_fields = [
            ("Full Name", "entry"),
            ("Age", "entry"),
            ("Gender", "combobox", ["Male", "Female", "Other"]),
            ("Certificate ID", "entry"),
            ("Mobile", "entry"),
            ("Passport", "entry"),
            ("NID", "entry"),
            ("Address", "entry"),
            ("Nationality", "entry"),
            ("Referred By", "entry"),
            ("Facility", "entry"),
            ("Mode", "combobox", ["Umrah", "Hajj", "Travel", "Other"])
        ]
        
        for field_info in basic_fields:
            field = field_info[0]
            field_type = field_info[1]
            
            frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
            frame.grid(row=current_row, column=0, pady=5, padx=10, sticky="w")
            
            tk.Label(frame, text=field + ":", width=15, 
                    anchor="w", font=('Arial', 11), bg='#f0f0f0').pack(side=tk.LEFT)
            
            if field_type == "entry":
                widget = tk.Entry(frame, width=25, font=('Arial', 11))
            elif field_type == "combobox":
                widget = ttk.Combobox(frame, values=field_info[2], width=22, font=('Arial', 11))
                widget.set(field_info[2][0])
            
            widget.pack(side=tk.LEFT, padx=5)
            self.entries[field] = widget
            current_row += 1
        
        # Vaccine Information Section
        tk.Label(scrollable_frame, text="Vaccine Information", font=('Arial', 14, 'bold'), 
                bg='#f0f0f0').grid(row=current_row, column=0, columnspan=2, pady=(20, 10), sticky='w')
        current_row += 1
        
        # Vaccine selection frame
        vaccine_frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
        vaccine_frame.grid(row=current_row, column=0, pady=5, padx=10, sticky="w")
        
        tk.Label(vaccine_frame, text="Vaccine Name:", width=15,
                anchor="w", font=('Arial', 11), bg='#f0f0f0').pack(side=tk.LEFT)
        
        # Combo box for vaccine selection
        self.vaccine_combo = ttk.Combobox(vaccine_frame, values=self.vaccine_list, width=22, font=('Arial', 11))
        self.vaccine_combo.pack(side=tk.LEFT, padx=5)
        self.vaccine_combo.bind('<<ComboboxSelected>>', self.on_vaccine_select)
        
        # Additional entry for custom vaccine name
        self.custom_vaccine_entry = tk.Entry(vaccine_frame, width=25, font=('Arial', 11))
        self.entries["Vaccine Name"] = self.vaccine_combo
        current_row += 1
        
        # Date fields with calendar widgets
        date_fields = [
            ("Date Given", "date"),
            ("Manufacturing Date", "date"),
            ("Expiry Date", "date")
        ]
        
        for field, field_type in date_fields:
            frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
            frame.grid(row=current_row, column=0, pady=5, padx=10, sticky="w")
            
            tk.Label(frame, text=field + ":", width=15,
                    anchor="w", font=('Arial', 11), bg='#f0f0f0').pack(side=tk.LEFT)
            
            cal = DateEntry(frame, width=22, background='darkblue',
                          foreground='white', borderwidth=2, font=('Arial', 11))
            cal.pack(side=tk.LEFT, padx=5)
            self.entries[field] = cal
            current_row += 1
        
        # Additional vaccine fields
        additional_fields = [
            ("Dose Information", "entry"),
            ("Batch Number", "entry"),
            ("Manufacturer", "entry")
        ]
        
        for field, field_type in additional_fields:
            frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
            frame.grid(row=current_row, column=0, pady=5, padx=10, sticky="w")
            
            tk.Label(frame, text=field + ":", width=15,
                    anchor="w", font=('Arial', 11), bg='#f0f0f0').pack(side=tk.LEFT)
            
            widget = tk.Entry(frame, width=25, font=('Arial', 11))
            widget.pack(side=tk.LEFT, padx=5)
            self.entries[field] = widget
            current_row += 1
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Generate button
        btn_frame = tk.Frame(self.frame_generate, bg='#f0f0f0')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Generate Certificate",
                 command=self.generate_certificate,
                 font=('Arial', 12),
                 bg='#4a90e2',
                 fg='white',
                 padx=20,
                 pady=10).pack()
        
        # QR Code display
        self.label_qr = tk.Label(self.frame_generate, bg='#f0f0f0')
        self.label_qr.pack(pady=10)
    
    def create_scan_frame(self):
        tk.Label(self.frame_scan, text="Scan QR Code",
                font=('Arial', 18, 'bold'), bg='#f0f0f0').pack(pady=(0, 20))
        
        tk.Button(self.frame_scan, text="Start Scanning",
                 command=self.start_scanning,
                 font=('Arial', 12),
                 bg='#4a90e2',
                 fg='white',
                 padx=20,
                 pady=10).pack(pady=10)
        
        self.text_scan_result = tk.Text(self.frame_scan, height=10, width=60,
                                      font=('Arial', 12), bd=1, relief=tk.SOLID)
        self.text_scan_result.pack(pady=10)
    
    def on_vaccine_select(self, event=None):
        if self.vaccine_combo.get() == "Other (Please Specify)":
            self.custom_vaccine_entry.pack(side=tk.LEFT, padx=5)
        else:
            self.custom_vaccine_entry.pack_forget()
    
    def show_generate(self):
        self.frame_scan.pack_forget()
        self.frame_generate.pack(fill=tk.BOTH, expand=True)
    
    def show_scan(self):
        self.frame_generate.pack_forget()
        self.frame_scan.pack(fill=tk.BOTH, expand=True)
    
    def generate_certificate(self):
        # Collect certificate data
        certificate = {}
        for field, widget in self.entries.items():
            if isinstance(widget, DateEntry):
                certificate[field] = widget.get_date().strftime('%Y-%m-%d')
            elif isinstance(widget, ttk.Combobox):
                if field == "Vaccine Name" and widget.get() == "Other (Please Specify)":
                    certificate[field] = self.custom_vaccine_entry.get()
                else:
                    certificate[field] = widget.get()
            else:
                certificate[field] = widget.get()
        
        # Validate inputs
        if not all(certificate.values()):
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        
        try:
            # Process certificate using the manager
            result = self.cert_manager.process_certificate(certificate)
            
            # Display QR code in GUI
            qr_image = Image.open(result['qr_path'])
            qr_image = qr_image.resize((250, 250), Image.Resampling.LANCZOS)
            self.qr_photo = ImageTk.PhotoImage(qr_image)
            self.label_qr.config(image=self.qr_photo)
            
            # Show success message with drive link
            message = f"Certificate generated successfully!\n\nLocal PDF: {result['pdf_path']}\nDrive Link: {result['drive_link']}"
            messagebox.showinfo("Success", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate certificate: {str(e)}")
    
    def start_scanning(self):
        threading.Thread(target=self.scan_qr, daemon=True).start()
    
    def scan_qr(self):
        cap = cv2.VideoCapture(0)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                for barcode in decode(frame):
                    qr_data = barcode.data.decode("utf-8")
                    
                    # Check if it's a drive link or certificate data
                    if qr_data.startswith("https://drive.google.com"):
                        result_text = f"Drive Link Found:\n{qr_data}"
                    else:
                        try:
                            cert_data = json.loads(qr_data)
                            result_text = "Certificate Details:\n" + \
                                        "\n".join(f"{k}: {v}" for k, v in cert_data.items())
                        except json.JSONDecodeError:
                            result_text = f"Raw QR Data:\n{qr_data}"
                    
                    self.text_scan_result.delete(1.0, tk.END)
                    self.text_scan_result.insert(tk.END, result_text)
                    
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                
                cv2.imshow("QR Scanner - Press 'q' to stop", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        finally:
            cap.release()
            cv2.destroyAllWindows()
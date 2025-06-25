import os
from gui_app import VaccineCertApp
from certificate_manager import CertificateManager

def main():
    # Configuration
    CREDENTIALS_PATH = r""  # Update this path
    FOLDER_ID = ""  # Update this ID
    
    # Initialize certificate manager
    cert_manager = CertificateManager(CREDENTIALS_PATH, FOLDER_ID)
    
    # Create and run GUI application
    app = VaccineCertApp(cert_manager)
    app.mainloop()

if __name__ == "__main__":
    main()
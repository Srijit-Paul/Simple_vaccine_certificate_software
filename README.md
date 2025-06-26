# Vaccine Certificate QR Code System

This project is a Python-based application for generating, scanning, and managing digital vaccine certificates with QR codes. It features a graphical user interface (GUI) for data entry and certificate generation, PDF export, QR code creation, and Google Drive integration for sharing certificates.

## Features

- Generate professional vaccine certificate PDFs with embedded QR codes.
- Scan QR codes to verify or retrieve certificate data.
- Upload certificates to Google Drive and generate public sharing links.
- User-friendly GUI for both certificate creation and scanning.
- Supports multiple vaccines and customizable certificate fields.

## Project Structure

- [`main.py`](main.py): Entry point for launching the application.
- [`gui_app.py`](gui_app.py): Main GUI application logic.
- [`certificate_manager.py`](certificate_manager.py): Handles certificate PDF generation, QR code creation, and Google Drive upload.
- [`vaccineqr.py`](vaccineqr.py): Alternative simple GUI for QR code generation and scanning.
- [`servicefile.py`](servicefile.py): Example script for uploading files to Google Drive and generating QR codes.
- `certificates/`: Folder where generated certificates and QR codes are saved.
- `vaccinehomeautomation-xxxx.json`: Google API service account credentials (required for Drive upload).

## Requirements

- Python 3.7+
- Packages: `tkinter`, `qrcode`, `Pillow`, `opencv-python`, `pyzbar`, `reportlab`, `google-api-python-client`, `google-auth`, `tkcalendar`

Install dependencies with:
```sh
pip install qrcode[pil] Pillow opencv-python pyzbar reportlab google-api-python-client google-auth tkcalendar
```

## Setup

1. Place your Google service account JSON credentials in the project directory.
2. Update the `CREDENTIALS_PATH` and `FOLDER_ID` in [`main.py`](main.py) with your credentials file path and Google Drive folder ID.
3. Run the application:
   ```sh
   python main.py
   ```

## Usage

- **Generate Certificate:** Fill in the required details and click "Generate Certificate". The PDF and QR code will be created and uploaded to Google Drive.
- **Scan Certificate:** Use the "Scan Certificate" tab to scan QR codes from certificates and view their details.

## License

This project is for educational and demonstration purposes.

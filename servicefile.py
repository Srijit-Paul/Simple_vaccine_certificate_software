import qrcode
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Load Google Drive API credentials
SERVICE_ACCOUNT_FILE = r""  # Replace with your JSON file path
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Authenticate with Google Drive API
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Initialize Google Drive API service
drive_service = build("drive", "v3", credentials=credentials)

# Define the folder ID (updated with your folder ID)
folder_id = ""  # Replace with your folder ID

# Define file metadata with the parent folder
file_metadata = {
    "name": "vaccination_certificate.pdf",
    "mimeType": "application/pdf",
    "parents": [folder_id],  # Add the folder ID here
}

# Define file to upload
file_path = r""  # Replace with actual file path
media = MediaFileUpload(file_path, mimetype="application/pdf")

# Upload file
file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

# Get File ID
file_id = file.get("id")
print("File Uploaded Successfully. File ID:", file_id)

# Set file permissions to public
permission = {"role": "reader", "type": "anyone"}
drive_service.permissions().create(fileId=file_id, body=permission).execute()

# Generate public link
file_link = f"https://drive.google.com/file/d/{file_id}/view"
print("Public Link:", file_link)

# Generate QR code for the file link
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(file_link)
qr.make(fit=True)

# Create an image from the QR code
img = qr.make_image(fill='black', back_color='white')

# Save the QR code image
img.save("vaccination_certificate_qr.png")

print("QR code generated and saved as 'vaccination_certificate_qr.png'.")
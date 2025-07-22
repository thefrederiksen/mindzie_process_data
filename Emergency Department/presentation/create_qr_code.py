import qrcode
import os

# GitHub repository URL
url = "https://github.com/thefrederiksen/mindzie_process_data"

# Create QR code instance
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# Add data to QR code
qr.add_data(url)
qr.make(fit=True)

# Create image from QR code
img = qr.make_image(fill_color="black", back_color="white")

# Save to presentation directory
output_path = "presentation/github_qr_code.png"
img.save(output_path)

print(f"QR code saved to: {output_path}")
print(f"URL encoded: {url}") 
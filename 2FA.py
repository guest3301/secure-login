import pyotp
import smtplib
import getpass
from email.mime.text import MIMEText

# Function to generate a TOTP secret
def generate_totp_secret():
    return pyotp.random_base32()

# Function to generate a TOTP URI for QR code (optional)
def generate_totp_uri(secret, email):
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="MyApp")

# Function to send OTP via email
def send_otp_email(email, otp):
    sender_email = "your_email@example.com"  # Replace with your email
    sender_password = getpass.getpass("Enter your email password: ")  # Securely input password
    subject = "Your 2FA One-Time Password"
    body = f"Your One-Time Password (OTP) is: {otp}"

    # Create email message
    message = MIMEText(body)
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject

    try:
        # Send email using SMTP
        with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Replace with your SMTP server
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        print("OTP sent successfully!")
    except Exception as e:
        print(f"Failed to send OTP: {e}")

# Function to verify OTP
def verify_otp(secret, user_otp):
    totp = pyotp.TOTP(secret)
    return totp.verify(user_otp)

# Main program
def main():
    # Step 1: User registration (generate TOTP secret)
    user_email = input("Enter your email: ")
    totp_secret = generate_totp_secret()
    print("Your TOTP secret has been generated. Please store it securely.")

    # Step 2: Simulate sending OTP via email
    totp = pyotp.TOTP(totp_secret)
    current_otp = totp.now()
    print(f"DEBUG: Current OTP (for testing): {current_otp}")  # For debugging purposes
    send_otp_email(user_email, current_otp)

    # Step 3: User enters OTP for verification
    user_otp = input("Enter the OTP you received: ")
    if verify_otp(totp_secret, user_otp):
        print("OTP verified successfully! Access granted.")
    else:
        print("Invalid OTP. Access denied.")

if _name_ == "_main_":
    main()
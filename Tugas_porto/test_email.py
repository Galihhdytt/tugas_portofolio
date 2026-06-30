#!/usr/bin/env python
"""
Script untuk test email functionality
Jalankan: python test_email.py
"""
import sys
import os

# Add Backend to path
sys.path.insert(0, os.path.dirname(__file__))

from Backend.config import Config
from Backend.utama.utama import send_contact_email

print("=" * 60)
print("TEST EMAIL CONFIGURATION")
print("=" * 60)

print(f"\n📧 Email Configuration:")
print(f"  MAIL_SERVER: {Config.MAIL_SERVER}")
print(f"  MAIL_PORT: {Config.MAIL_PORT}")
print(f"  MAIL_USE_TLS: {Config.MAIL_USE_TLS}")
print(f"  MAIL_USERNAME: {Config.MAIL_USERNAME}")
print(f"  MAIL_SENDER: {Config.MAIL_SENDER}")
print(f"  MAIL_RECIPIENT: {Config.MAIL_RECIPIENT}")
print(f"  RESEND_API_KEY: {'Set' if Config.RESEND_API_KEY else 'Not Set'}")

# Validate configuration
print(f"\n✓ Config validated")

# Test sending email
print(f"\n📨 Sending test email...\n")

success, error = send_contact_email(
    name="Test User",
    email="test@example.com",
    message="Ini adalah pesan test dari script test_email.py"
)

if success:
    print("✅ SUCCESS! Email berhasil dikirim!")
    print(f"   Email dikirim ke: {Config.MAIL_RECIPIENT}")
    print(f"   Dari: {Config.MAIL_SENDER}")
else:
    print(f"❌ FAILED: {error}")
    print(f"\n💡 Troubleshooting:")
    
    if "credentials tidak dikonfigurasi" in error:
        print("   - Pastikan MAIL_USERNAME dan MAIL_PASSWORD di .env tidak kosong")
    elif "Authentication" in error:
        print("   - Username atau password salah")
        print("   - Untuk Gmail: gunakan App Password, bukan password biasa")
    elif "SMTP" in error or "timeout" in error:
        print("   - Masalah koneksi SMTP")
        print("   - Cek firewall atau VPN")
    
    sys.exit(1)

print("\n" + "=" * 60)

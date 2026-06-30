# Panduan Setup Email - "Hubungi Saya"

## Masalah
Fitur "Hubungi Saya" (contact form) tidak bisa mengirim email karena email credentials belum dikonfigurasi.

## Solusi: Ada 2 Opsi

### Opsi 1: Menggunakan Resend API (Recommended ✅)
**Keuntungan:** Lebih mudah setup, tidak perlu App Password

1. **Buka https://resend.com**
   - Daftar akun gratis
   - Verify email Anda

2. **Dapatkan API Key**
   - Buka dashboard Resend
   - Pergi ke menu "API Keys"
   - Copy API Key yang sudah ada atau buat baru
   - Format: `re_xxxxx...`

3. **Update file `.env`**
   ```
   RESEND_API_KEY=re_your_actual_key_here
   MAIL_SENDER=your_email@gmail.com
   MAIL_RECIPIENT=galihhdytt@gmail.com
   ```

4. **Kosongkan SMTP credentials (opsional tapi recommended)**
   ```
   MAIL_USERNAME=
   MAIL_PASSWORD=
   ```

5. **Restart aplikasi**
   - Stop server (Ctrl+C)
   - Jalankan ulang: `python app.py`

---

### Opsi 2: Menggunakan Gmail SMTP (Backup)
**Keuntungan:** Tidak perlu API key pihak ketiga

1. **Aktifkan 2-Step Verification di Gmail**
   - Buka https://myaccount.google.com/security
   - Scroll ke "How you sign in to Google"
   - Aktifkan "2-Step Verification"

2. **Buat App Password**
   - Kembali ke https://myaccount.google.com/security
   - Cari "App passwords" (hanya muncul jika 2FA aktif)
   - Pilih app: "Mail"
   - Pilih device: "Windows Computer"
   - Copy password yang diberikan (16 karakter, ada spasi)

3. **Update file `.env`**
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx
   MAIL_SENDER=your_email@gmail.com
   MAIL_RECIPIENT=galihhdytt@gmail.com
   ```

4. **Jangan lupa**
   - Pastikan `MAIL_USERNAME` dan `MAIL_PASSWORD` **tidak kosong**
   - Copy-paste password persis seperti di Google (dengan spasi)

5. **Restart aplikasi**

---

## Testing

### Test via Browser
1. Buka http://localhost:5000
2. Scroll ke bagian "Hubungi Saya"
3. Isi form dan klik "Kirim Pesan"
4. Cek pesan error yang lebih detail sekarang

### Test via API
```bash
curl -X POST http://localhost:5000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "message": "Testing email system"
  }'
```

### Cek Konfigurasi
```bash
curl http://localhost:5000/api/mail-help
```

---

## Troubleshooting

### Error: "Email credentials tidak dikonfigurasi"
- Pastikan `.env` file ada di folder `Backend/`
- Pastikan `MAIL_USERNAME` dan `MAIL_PASSWORD` tidak kosong ATAU `RESEND_API_KEY` ada

### Error: "SMTP Authentication Failed"
- Verify password benar (untuk Gmail: gunakan App Password, bukan password utama)
- Pastikan 2-Step Verification sudah aktif di Gmail
- Coba ulangi buat App Password yang baru

### Error: "Resend API error"
- Pastikan API Key benar (dimulai dengan `re_`)
- Cek koneksi internet
- Verifikasi domain di Resend dashboard

### Email tidak diterima tapi no error
- Cek folder "Spam" atau "Promotions"
- Pastikan `MAIL_RECIPIENT` benar
- Cek apakah sender address terdaftar di Resend/Gmail

---

## File yang Berubah
- `Backend/.env` - Konfigurasi email
- `Backend/utama/utama.py` - Improved error handling
- `Backend/app.py` - Improved error handling

## Tips
- Gunakan Resend untuk production (lebih reliable)
- Gunakan Gmail SMTP untuk testing/development
- Jangan commit `.env` ke GitHub (sudah ada di `.gitignore`)

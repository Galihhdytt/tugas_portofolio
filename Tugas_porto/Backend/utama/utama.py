import json
import smtplib
import urllib.error
import urllib.request
from email.message import EmailMessage

from flask import Blueprint, jsonify, request

from Backend.config import Config
from Backend.model import Database

utama_bp = Blueprint('utama', __name__)


def send_contact_email(name, email, message):
    recipient = Config.MAIL_RECIPIENT or 'galihhdytt@gmail.com'
    sender = Config.MAIL_SENDER or Config.MAIL_USERNAME or 'onboarding@resend.dev'
    api_key = Config.RESEND_API_KEY or ''

    # Try Resend API first
    if api_key:
        try:
            payload = {
                'from': sender,
                'to': [recipient],
                'reply_to': email,
                'subject': f'Pesan dari portofolio: {name}',
                'html': f'<p><strong>Nama:</strong> {name}</p><p><strong>Email:</strong> {email}</p><p>{message}</p>'
            }
            req = urllib.request.Request(
                'https://api.resend.com/emails',
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status < 400:
                    return True, None
                else:
                    return False, f'Resend API error: {resp.status}'
        except urllib.error.HTTPError as e:
            error_msg = f'Resend API HTTP Error {e.code}: {e.reason}'
            return False, error_msg
        except Exception as e:
            error_msg = f'Resend API Error: {str(e)}'
            # Don't return yet, try SMTP fallback

    # Fallback to SMTP
    username = Config.MAIL_USERNAME or ''
    password = Config.MAIL_PASSWORD or ''
    
    if not username or not password:
        return False, 'Email credentials tidak dikonfigurasi. Hubungi admin untuk setup MAIL_USERNAME dan MAIL_PASSWORD.'

    try:
        msg = EmailMessage()
        msg['Subject'] = f'Pesan dari portofolio: {name}'
        msg['From'] = sender
        msg['To'] = recipient
        msg['Reply-To'] = email
        msg.set_content(f'Nama: {name}\nEmail: {email}\n\n{message}')

        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as smtp:
            if Config.MAIL_USE_TLS:
                smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
        return True, None
    except smtplib.SMTPAuthenticationError as e:
        return False, 'SMTP Authentication Failed: Username atau password salah'
    except smtplib.SMTPException as e:
        return False, f'SMTP Error: {str(e)}'
    except Exception as e:
        return False, f'Email Error: {str(e)}'


@utama_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend utama berjalan'}), 200


@utama_bp.route('/info', methods=['GET'])
def app_info():
    return jsonify({'name': 'Portofolio API', 'version': '1.0.0'}), 200


@utama_bp.route('/main-profile', methods=['GET'])
def main_profile():
    response = jsonify({})
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    try:
        db = Database()
        profile_row = db.execute_query('SELECT * FROM profiles ORDER BY id DESC LIMIT 1', fetch=True)
        profile = profile_row[0] if profile_row else {}
        user_id = profile.get('user_id', 1)

        experiences = db.execute_query(
            'SELECT * FROM experiences WHERE user_id = %s ORDER BY created_at DESC',
            (user_id,),
            fetch=True,
        ) or []
        projects = db.execute_query(
            'SELECT * FROM projects WHERE user_id = %s ORDER BY created_at DESC',
            (user_id,),
            fetch=True,
        ) or []
        skills = db.execute_query(
            'SELECT * FROM skills WHERE user_id = %s ORDER BY id DESC',
            (user_id,),
            fetch=True,
        ) or []

        payload = {
            'success': True,
            'data': {
                'nama_lengkap': profile.get('nama_lengkap') or 'Galih Hidayat',
                'prodi': profile.get('prodi') or 'Informatika',
                'universitas': profile.get('universitas') or 'Universitas XYZ',
                'fakultas': profile.get('fakultas') or 'Teknik',
                'semester': profile.get('semester') or '6',
                'alamat': profile.get('alamat') or 'Salatiga',
                'email': profile.get('email') or 'galihdytt.com',
                'foto_url': profile.get('foto_url') or '',
                'skills': skills,
                'experiences': experiences,
                'projects': projects,
            },
        }
        response = jsonify(payload)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as exc:
        response = jsonify({
            'success': True,
            'data': {
                'nama_lengkap': 'Galih Hidayat',
                'prodi': 'Informatika',
                'universitas': 'Universitas XYZ',
                'fakultas': 'Teknik',
                'semester': '6',
                'alamat': 'Bandung',
                'email': 'raihan@example.com',
                'foto_url': '',
                'skills': [],
                'experiences': [],
                'projects': [],
            },
            'warning': str(exc),
        })
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response


@utama_bp.route('/mail-help', methods=['GET'])
def mail_help():
    instructions = [
        '1. Buka akun Gmail Anda.',
        '2. Aktifkan Verifikasi 2 Langkah.',
        '3. Buat App Password untuk aplikasi.',
        '4. Isi nilai MAIL_USERNAME, MAIL_PASSWORD, dan MAIL_SENDER di file .env.',
        '5. Pastikan MAIL_RECIPIENT mengarah ke galihhdytt@gmail.com.',
        '6. Jalankan ulang aplikasi dan coba kirim pesan lagi.',
    ]
    return jsonify({'success': True, 'instructions': instructions})


@utama_bp.route('/contact', methods=['POST'])
def contact():
    payload = request.get_json(silent=True) or {}
    name = (payload.get('name') or '').strip()
    email = (payload.get('email') or '').strip()
    message = (payload.get('message') or '').strip()

    if not name or not email or not message:
        return jsonify({'success': False, 'error': 'Semua field wajib diisi'}), 400

    try:
        sent, error_msg = send_contact_email(name, email, message)
    except Exception as exc:
        return jsonify({'success': False, 'error': f'Gagal mengirim email: {exc}'}), 502

    if not sent:
        help_msg = '\n\nUntuk bantuan setup email, silakan cek /api/mail-help atau hubungi admin.'
        return jsonify({'success': False, 'error': (error_msg or 'Gagal mengirim email') + help_msg}), 502

    return jsonify({'success': True, 'message': 'Pesan berhasil dikirim'})

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from Backend.config import Config
from Backend.model import Database
import json
import os
import smtplib
import sys
import urllib.request
import urllib.error
from email.message import EmailMessage

# Import blueprints
from Backend.admin.login import login_bp
from Backend.admin.dashboard import dashboard_bp
from Backend.admin.profiles import profiles_bp
from Backend.admin.experience import experience_bp
from Backend.admin.projects import projects_bp
from Backend.admin.skills import skills_bp
from Backend.utama.utama import utama_bp
from Backend.admin.upload import upload_bp


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


def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__,
                static_folder=os.path.join(base_dir, 'Frontend'),
                template_folder=base_dir)

    # Konfigurasi
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'Frontend', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Enable CORS untuk development
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(login_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(profiles_bp, url_prefix='/api')
    app.register_blueprint(experience_bp, url_prefix='/api')
    app.register_blueprint(projects_bp, url_prefix='/api')
    app.register_blueprint(skills_bp, url_prefix='/api')
    app.register_blueprint(utama_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    
    # Route untuk serving frontend files
    @app.route('/')
    def index():
        public_index = os.path.join(base_dir, 'Frontend', 'utama', 'index.html')
        if os.path.exists(public_index):
            return send_from_directory(os.path.join(base_dir, 'Frontend', 'utama'), 'index.html')
        return "Error: index.html not found in Frontend/utama folder", 404

    @app.route('/index.html')
    def index_file():
        public_index = os.path.join(base_dir, 'Frontend', 'utama', 'index.html')
        if os.path.exists(public_index):
            return send_from_directory(os.path.join(base_dir, 'Frontend', 'utama'), 'index.html')
        return "Error: index.html not found", 404

    @app.route('/admin')
    def admin_root():
        return send_from_directory(os.path.join(base_dir, 'Frontend', 'admin'), 'dashboard.html')

    @app.route('/admin/<path:filename>')
    def admin_pages(filename):
        return send_from_directory(os.path.join(base_dir, 'Frontend', 'admin'), filename)

    @app.route('/uploads/<path:filename>')
    def uploaded_files(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/Frontend/<path:filename>')
    def frontend_files(filename):
        return send_from_directory(os.path.join(base_dir, 'Frontend'), filename)
    
    @app.route('/profil/<path:filename>')
    def profil_pages(filename):
        return send_from_directory(os.path.join(app.root_path, 'Frontend', 'profil'), filename)
    
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            base_dir,
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )
    @app.route('/api/main-profile', methods=['GET'])
    def main_profile():
        response = jsonify({})
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        try:
            db = Database()
            profile_row = db.execute_query(
                "SELECT * FROM profiles ORDER BY id DESC LIMIT 1",
                fetch=True
            )
            profile = profile_row[0] if profile_row else {}
            user_id = profile.get('user_id', 1)

            experiences = db.execute_query(
                "SELECT * FROM experiences WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,),
                fetch=True
            ) or []
            projects = db.execute_query(
                "SELECT * FROM projects WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,),
                fetch=True
            ) or []
            skills = db.execute_query(
                "SELECT * FROM skills WHERE user_id = %s ORDER BY id DESC",
                (user_id,),
                fetch=True
            ) or []

            payload = {
                'success': True,
                'data': {
                    'nama_lengkap': profile.get('nama_lengkap') or 'Galih Hidayat',
                    'prodi': profile.get('prodi') or 'Informatika',
                    'universitas': profile.get('universitas') or 'Universitas XYZ',
                    'fakultas': profile.get('fakultas') or 'Teknik',
                    'semester': profile.get('semester') or '6',
                    'alamat': profile.get('alamat') or 'Bandung',
                    'email': profile.get('email') or 'raihan@example.com',
                    'foto_url': profile.get('foto_url') or '',
                    'skills': skills,
                    'experiences': experiences,
                    'projects': projects
                }
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
                    'projects': []
                },
                'warning': str(exc)
            })
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response

    @app.route('/api/mail-help', methods=['GET'])
    def mail_help():
        instructions = [
            '1. Buka akun Gmail Anda.',
            '2. Aktifkan Verifikasi 2 Langkah.',
            '3. Buat App Password untuk aplikasi.',
            '4. Isi nilai MAIL_USERNAME, MAIL_PASSWORD, dan MAIL_SENDER di file .env.',
            '5. Pastikan MAIL_RECIPIENT mengarah ke galihhdytt@gmail.com.',
            '6. Jalankan ulang aplikasi dan coba kirim pesan lagi.'
        ]
        return jsonify({'success': True, 'instructions': instructions})

    @app.route('/api/contact', methods=['POST'])
    def contact():
        payload = request.get_json(silent=True) or {}
        name = (payload.get('name') or '').strip()
        email = (payload.get('email') or '').strip()
        message = (payload.get('message') or '').strip()

        if not name or not email or not message:
            return jsonify({'success': False, 'error': 'Semua field wajib diisi'}), 400

        try:
            sender = sys.modules[__name__].send_contact_email
            sent = sender(name, email, message)
        except Exception as exc:
            return jsonify({'success': False, 'error': f'Gagal mengirim email: {exc}'}), 502

        if not sent:
            return jsonify({'success': False, 'error': 'Gagal mengirim email ke galihhdytt@gmail.com. Lihat /api/mail-help untuk panduan Gmail.'}), 502

        return jsonify({'success': True, 'message': 'Pesan berhasil dikirim'})

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        # Jika request HTML (bukan API), kembalikan index.html untuk SPA routing
        if request.accept_mimetypes.best == 'text/html':
            return send_from_directory(app.root_path, 'index.html')
        return jsonify({'error': 'Route tidak ditemukan'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Terjadi kesalahan pada server'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
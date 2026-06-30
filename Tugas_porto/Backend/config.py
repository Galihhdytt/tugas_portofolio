import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    # Database Configuration
    db_type_env = os.getenv('DB_TYPE', '').strip().lower()
    has_mysql_env = any([
        os.getenv('DB_HOST'),
        os.getenv('DB_USER'),
        os.getenv('DB_PASSWORD'),
        os.getenv('DB_NAME')
    ])
    DB_TYPE = db_type_env or 'mysql'
    DB_HOST = os.getenv('DB_HOST', 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com')
    DB_PORT = int(os.getenv('DB_PORT', 4000))
    DB_USER = os.getenv('DB_USER', '5Ur7SCESKPrnmrY.root')
    if DB_TYPE == 'mysql' and 'tidb' in DB_HOST.lower() and DB_USER and '.' not in DB_USER and DB_USER != 'root':
        DB_USER = f'{DB_USER}.root'
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'GEjDmDsj3Q5r5PYG')
    DB_NAME = os.getenv('DB_NAME', 'porto_db')
    DB_SSL_DISABLED = os.getenv('DB_SSL_DISABLED', 'False').lower() == 'true'
    DB_FALLBACK_TO_SQLITE = os.getenv('DB_FALLBACK_TO_SQLITE', 'False').lower() == 'true'
    DB_PATH = os.getenv('DB_PATH', os.path.join(os.path.dirname(__file__), 'portfolio.db'))

    MYSQL_CONFIG = {
        'host': DB_HOST,
        'port': DB_PORT,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'database': DB_NAME,
        'ssl_disabled': DB_SSL_DISABLED,
        'ssl_ca': os.getenv('DB_CA_PATH', None)
    }

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # Cloudinary Configuration (Dipecah agar lebih clean)
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', 'daknwopl3')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '884765233771594')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', 'qOYvn2w1TsW_ipwEzhgqB8RRTKE')

    # Resend API Configuration
    RESEND_API_KEY = os.getenv('RESEND_API_KEY', 're_Sk1G87rv_783KGz9c5QAaifSaZ3oxZdKs')

    # SMTP Configuration for contact form
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com').strip()
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587').strip())
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').strip().lower() == 'true'
    MAIL_USERNAME = (os.getenv('MAIL_USERNAME', '') or '').strip()
    MAIL_PASSWORD = (os.getenv('MAIL_PASSWORD', '') or '').strip()
    MAIL_SENDER = (os.getenv('MAIL_SENDER', 'galihhdytt@gmail.com') or '').strip()
    MAIL_RECIPIENT = (os.getenv('MAIL_RECIPIENT', 'galihhdytt@gmail.com') or '').strip()
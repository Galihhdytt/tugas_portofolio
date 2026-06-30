from flask import Blueprint, request, jsonify
from Backend.model import Database
from Backend.admin.login import token_required
from Backend.admin.file_utils import save_upload_file
import logging
from datetime import datetime

profiles_bp = Blueprint('profiles', __name__)
logger = logging.getLogger(__name__)
FALLBACK_PROFILES = {
    1: {
        'nama_lengkap': 'Galih Hidayat',
        'nama_panggilan': 'Galih',
        'tempat_lahir': '',
        'tanggal_lahir': '',
        'email': '',
        'telepon': '',
        'universitas': '',
        'fakultas': '',
        'prodi': '',
        'semester': '',
        'alamat': '',
        'foto_url': ''
    }
}

@profiles_bp.route('/profiles', methods=['GET'])
@token_required
def get_profil(current_user):
    try:
        db = Database()
        query = "SELECT * FROM profiles WHERE user_id = %s"
        result = db.execute_query(query, (current_user,), fetch=True)
        
        if result:
            return jsonify({'success': True, 'data': result[0]}), 200
        else:
            return jsonify({'success': True, 'data': FALLBACK_PROFILES.get(current_user, FALLBACK_PROFILES[1])}), 200
            
    except Exception as e:
        return jsonify({'success': True, 'data': FALLBACK_PROFILES.get(current_user, FALLBACK_PROFILES[1])}), 200

@profiles_bp.route('/profiles', methods=['POST', 'PUT'])
@token_required
def update_profil(current_user):
    try:
        data = {}
        if request.form:
            data = request.form.to_dict()
        elif request.values:
            data = request.values.to_dict()
        else:
            data = request.get_json(silent=True) or {}

        logger.info('PROFILE REQUEST form_keys=%s values_keys=%s files=%s', list(request.form.keys()), list(request.values.keys()), list(request.files.keys()))
        uploaded_file = request.files.get('foto') or request.files.get('file')
        if uploaded_file and uploaded_file.filename:
            data['foto_url'] = save_upload_file(uploaded_file)

        db = Database()

        allowed_fields = [
            'nama_lengkap', 'nama_panggilan', 'tempat_lahir', 'tanggal_lahir',
            'email', 'telepon', 'universitas', 'fakultas', 'prodi',
            'semester', 'alamat', 'foto_url'
        ]

        check_query = "SELECT id FROM profiles WHERE user_id = %s"
        existing = db.execute_query(check_query, (current_user,), fetch=True)

        updates = []
        values = []

        for field in allowed_fields:
            if field not in data:
                continue

            value = data[field]
            if value is None:
                continue

            if isinstance(value, str):
                value = value.strip()

            if field == 'tanggal_lahir':
                if value in ('', '?'):
                    continue
                try:
                    datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    continue
            elif field in {'nama_lengkap', 'nama_panggilan', 'tempat_lahir', 'email', 'telepon', 'universitas', 'fakultas', 'prodi', 'semester', 'alamat', 'foto_url'}:
                if isinstance(value, str) and value == '?':
                    value = ''

            updates.append(f"{field} = %s")
            values.append(value)

        if not updates:
            return jsonify({'error': 'Tidak ada data valid untuk diupdate'}), 400

        if existing:
            values.append(current_user)
            query = f"UPDATE profiles SET {', '.join(updates)} WHERE user_id = %s"
        else:
            fields_str = ', '.join([f.split(' = ')[0] for f in updates])
            placeholders = ', '.join(['%s'] * len(updates))
            values.insert(0, current_user)
            query = f"INSERT INTO profiles (user_id, {fields_str}) VALUES (%s, {placeholders})"

        db.execute_query(query, tuple(values))
        saved_profile = db.execute_query(
            "SELECT * FROM profiles WHERE user_id = %s",
            (current_user,),
            fetch=True
        )
        profile_data = saved_profile[0] if saved_profile else {}
        return jsonify({'success': True, 'message': 'Profil berhasil disimpan', 'data': profile_data}), 200

    except Exception as exc:
        logger.exception('Gagal menyimpan profil untuk user %s', current_user)
        return jsonify({'success': False, 'error': 'Gagal menyimpan profil ke database', 'details': str(exc)}), 500
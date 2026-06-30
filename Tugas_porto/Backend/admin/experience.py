from flask import Blueprint, request, jsonify
from Backend.model import Database
from Backend.admin.login import token_required

# Inisialisasi Blueprint
experience_bp = Blueprint('experience', __name__)
FALLBACK_EXPERIENCES = {}


def _get_request_data():
    if request.form:
        return request.form.to_dict()
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.get_json(silent=True) or {}


def _get_fallback_experiences(current_user=None):
    if current_user is None:
        items = []
        for user_items in FALLBACK_EXPERIENCES.values():
            items.extend(user_items)
        return items
    return FALLBACK_EXPERIENCES.setdefault(current_user, [])

# ✅ PERBAIKAN: Hapus '/api' di depan route
@experience_bp.route('/experiences', methods=['GET'])
def get_experiences():
    """Mengambil semua experiences (publik)"""
    try:
        db = Database()
        
        query = """
            SELECT e.*, u.username 
            FROM experiences e 
            JOIN users u ON e.user_id = u.id 
            WHERE u.role = 'admin'
            ORDER BY e.created_at DESC
        """
        result = db.execute_query(query, fetch=True)
        
        return jsonify({
            'success': True,
            'data': result if result else []
        }), 200
        
    except Exception as e:
        return jsonify({'success': True, 'data': _get_fallback_experiences()}), 200

@experience_bp.route('/experiences/<int:id>', methods=['GET'])
def get_experience_by_id(id):
    """Mengambil satu experience berdasarkan ID"""
    try:
        db = Database()
        
        query = "SELECT * FROM experiences WHERE id = %s"
        result = db.execute_query(query, (id,), fetch=True)
        
        if not result:
            for user_items in FALLBACK_EXPERIENCES.values():
                for item in user_items:
                    if item['id'] == id:
                        return jsonify({'success': True, 'data': item}), 200
            return jsonify({'error': 'Experience tidak ditemukan'}), 404
        
        return jsonify({
            'success': True,
            'data': result[0]
        }), 200
        
    except Exception as e:
        for user_items in FALLBACK_EXPERIENCES.values():
            for item in user_items:
                if item['id'] == id:
                    return jsonify({'success': True, 'data': item}), 200
        return jsonify({'error': str(e)}), 500

@experience_bp.route('/experiences', methods=['POST'])
@token_required
def create_experience(current_user):
    """Create experience baru (Admin Only)"""
    try:
        data = _get_request_data()
        
        required_fields = ['posisi', 'perusahaan', 'durasi']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} wajib diisi'}), 400
        
        db = Database()
        
        query = """
            INSERT INTO experiences (user_id, posisi, perusahaan, durasi, deskripsi)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            current_user,
            data.get('posisi'),
            data.get('perusahaan'),
            data.get('durasi'),
            data.get('deskripsi')
        )
        
        new_id = db.execute_query(query, values)
        
        return jsonify({
            'success': True,
            'message': 'Experience berhasil dibuat',
            'id': new_id
        }), 201
        
    except Exception as e:
        user_items = _get_fallback_experiences(current_user)
        new_id = max([item['id'] for item in user_items], default=0) + 1
        user_items.append({'id': new_id, 'user_id': current_user, 'posisi': data.get('posisi'), 'perusahaan': data.get('perusahaan'), 'durasi': data.get('durasi'), 'deskripsi': data.get('deskripsi')})
        return jsonify({'success': True, 'message': 'Experience berhasil dibuat', 'id': new_id}), 201

@experience_bp.route('/experiences/<int:id>', methods=['PUT'])
@token_required
def update_experience(current_user, id):
    """Update experience (Admin Only)"""
    try:
        data = _get_request_data()
        
        db = Database()
        
        check_query = "SELECT id FROM experiences WHERE id = %s AND user_id = %s"
        existing = db.execute_query(check_query, (id, current_user), fetch=True)
        
        if not existing:
            return jsonify({'error': 'Experience tidak ditemukan atau bukan milik Anda'}), 404
        
        allowed_fields = ['posisi', 'perusahaan', 'durasi', 'deskripsi']
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])
        
        if not updates:
            return jsonify({'error': 'Tidak ada data yang diupdate'}), 400
        
        values.append(id)
        query = f"UPDATE experiences SET {', '.join(updates)} WHERE id = %s"
        db.execute_query(query, tuple(values))
        
        return jsonify({
            'success': True,
            'message': 'Experience berhasil diupdate'
        }), 200
        
    except Exception as e:
        user_items = _get_fallback_experiences(current_user)
        for item in user_items:
            if item['id'] == id:
                for key in ['posisi', 'perusahaan', 'durasi', 'deskripsi']:
                    if key in data:
                        item[key] = data[key]
                break
        return jsonify({'success': True, 'message': 'Experience berhasil diupdate'}), 200

@experience_bp.route('/experiences/<int:id>', methods=['DELETE'])
@token_required
def delete_experience(current_user, id):
    """Delete experience (Admin Only)"""
    try:
        db = Database()
        
        # Keamanan: Pastikan user hanya bisa hapus miliknya sendiri
        check_query = "SELECT id FROM experiences WHERE id = %s AND user_id = %s"
        existing = db.execute_query(check_query, (id, current_user), fetch=True)
        
        if not existing:
            return jsonify({'error': 'Experience tidak ditemukan atau bukan milik Anda'}), 404
        
        query = "DELETE FROM experiences WHERE id = %s"
        db.execute_query(query, (id,))
        
        return jsonify({
            'success': True,
            'message': 'Experience berhasil dihapus'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
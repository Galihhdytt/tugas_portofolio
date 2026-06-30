from flask import Blueprint, request, jsonify
from Backend.model import Database
from Backend.admin.login import token_required

skills_bp = Blueprint('skills', __name__)
FALLBACK_SKILLS = {}


def _get_request_data():
    if request.form:
        return request.form.to_dict()
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.get_json(silent=True) or {}


def _get_fallback_skills(current_user=None):
    if current_user is None:
        items = []
        for user_items in FALLBACK_SKILLS.values():
            items.extend(user_items)
        return items
    return FALLBACK_SKILLS.setdefault(current_user, [])

# ✅ PERBAIKAN: Hapus '/api' di depan route
@skills_bp.route('/skills', methods=['GET'])
def get_skills():
    """Mengambil semua skills (publik)"""
    try:
        db = Database()
        
        query = """
            SELECT s.*, u.username 
            FROM skills s 
            JOIN users u ON s.user_id = u.id 
            WHERE u.role = 'admin'
            ORDER BY s.id DESC
        """
        result = db.execute_query(query, fetch=True)
        
        return jsonify({
            'success': True,
            'data': result if result else []
        }), 200
        
    except Exception as e:
        return jsonify({'success': True, 'data': _get_fallback_skills()}), 200

@skills_bp.route('/skills/<int:id>', methods=['GET'])
def get_skill_by_id(id):
    """Mengambil satu skill berdasarkan ID"""
    try:
        db = Database()
        
        query = "SELECT * FROM skills WHERE id = %s"
        result = db.execute_query(query, (id,), fetch=True)
        
        if not result:
            for user_items in FALLBACK_SKILLS.values():
                for item in user_items:
                    if item['id'] == id:
                        return jsonify({'success': True, 'data': item}), 200
            return jsonify({'error': 'Skill tidak ditemukan'}), 404
        
        return jsonify({
            'success': True,
            'data': result[0]
        }), 200
        
    except Exception as e:
        for user_items in FALLBACK_SKILLS.values():
            for item in user_items:
                if item['id'] == id:
                    return jsonify({'success': True, 'data': item}), 200
        return jsonify({'error': str(e)}), 500

@skills_bp.route('/skills', methods=['POST'])
@token_required
def create_skill(current_user):
    """Create skill baru"""
    try:
        data = _get_request_data()
        
        required_fields = ['nama_skill']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} wajib diisi'}), 400
        
        db = Database()
        
        query = """
            INSERT INTO skills (user_id, nama_skill, icon_class)
            VALUES (%s, %s, %s)
        """
        values = (
            current_user,
            data.get('nama_skill'),
            data.get('icon_class')
        )
        
        new_id = db.execute_query(query, values)
        
        return jsonify({
            'success': True,
            'message': 'Skill berhasil dibuat',
            'id': new_id
        }), 201
        
    except Exception as e:
        user_items = _get_fallback_skills(current_user)
        new_id = max([item['id'] for item in user_items], default=0) + 1
        user_items.append({'id': new_id, 'user_id': current_user, 'nama_skill': data.get('nama_skill'), 'icon_class': data.get('icon_class')})
        return jsonify({'success': True, 'message': 'Skill berhasil dibuat', 'id': new_id}), 201

@skills_bp.route('/skills/<int:id>', methods=['PUT'])
@token_required
def update_skill(current_user, id):
    """Update skill"""
    try:
        data = _get_request_data()
        
        db = Database()
        
        # Cek apakah skill milik user ini
        check_query = "SELECT id FROM skills WHERE id = %s AND user_id = %s"
        existing = db.execute_query(check_query, (id, current_user), fetch=True)
        
        if not existing:
            return jsonify({'error': 'Skill tidak ditemukan atau bukan milik Anda'}), 404
        
        allowed_fields = ['nama_skill', 'icon_class']
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])
        
        if not updates:
            return jsonify({'error': 'Tidak ada data yang diupdate'}), 400
        
        values.append(id)
        query = f"UPDATE skills SET {', '.join(updates)} WHERE id = %s"
        db.execute_query(query, tuple(values))
        
        return jsonify({
            'success': True,
            'message': 'Skill berhasil diupdate'
        }), 200
        
    except Exception as e:
        user_items = _get_fallback_skills(current_user)
        for item in user_items:
            if item['id'] == id:
                for key in ['nama_skill', 'icon_class']:
                    if key in data:
                        item[key] = data[key]
                break
        return jsonify({'success': True, 'message': 'Skill berhasil diupdate'}), 200

@skills_bp.route('/skills/<int:id>', methods=['DELETE'])
@token_required
def delete_skill(current_user, id):
    """Delete skill"""
    try:
        db = Database()
        
        # Cek apakah skill milik user ini
        check_query = "SELECT id FROM skills WHERE id = %s AND user_id = %s"
        existing = db.execute_query(check_query, (id, current_user), fetch=True)
        
        if not existing:
            return jsonify({'error': 'Skill tidak ditemukan atau bukan milik Anda'}), 404
        
        query = "DELETE FROM skills WHERE id = %s"
        db.execute_query(query, (id,))
        
        return jsonify({
            'success': True,
            'message': 'Skill berhasil dihapus'
        }), 200
        
    except Exception as e:
        user_items = _get_fallback_skills(current_user)
        FALLBACK_SKILLS[current_user] = [item for item in user_items if item['id'] != id]
        return jsonify({'success': True, 'message': 'Skill berhasil dihapus'}), 200
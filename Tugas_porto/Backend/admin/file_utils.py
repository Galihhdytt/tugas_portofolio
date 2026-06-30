import os
import uuid
from flask import current_app


def save_upload_file(uploaded_file):
    if not uploaded_file or not uploaded_file.filename:
        return ''

    filename = f"{uuid.uuid4().hex}_{uploaded_file.filename}"
    upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'Frontend', 'uploads'))
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, filename)
    uploaded_file.save(save_path)
    return f"/uploads/{filename}"

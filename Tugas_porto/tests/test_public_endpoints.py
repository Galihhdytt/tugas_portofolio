import importlib
import os
import unittest
from datetime import date
from unittest import mock

from app import create_app
from model import Database


class PublicEndpointsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_main_profile_endpoint(self):
        response = self.client.get('/api/main-profile')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertIn('nama_lengkap', payload['data'])

    def test_contact_endpoint(self):
        response = self.client.post('/api/contact', json={
            'name': 'Test',
            'email': 'test@example.com',
            'message': 'Hello'
        })
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])

    def test_contact_endpoint_sends_notification(self):
        with mock.patch('app.send_contact_email', return_value=True) as mock_send:
            response = self.client.post('/api/contact', json={
                'name': 'Test',
                'email': 'test@example.com',
                'message': 'Hello'
            })

        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()

    def test_main_profile_endpoint_disables_browser_cache(self):
        response = self.client.get('/api/main-profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response.headers.get('Cache-Control', '').lower())

    def test_tidb_username_is_prefixed(self):
        with mock.patch.dict(os.environ, {
            'DB_TYPE': 'mysql',
            'DB_HOST': 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com',
            'DB_USER': 'prefix123',
            'DB_PASSWORD': 'secret',
            'DB_NAME': 'test'
        }, clear=False):
            import config
            importlib.reload(config)
            self.assertEqual(config.Config.DB_USER, 'prefix123.root')

    def test_profile_update_returns_error_when_db_write_fails(self):
        login_response = self.client.post('/api/login', json={
            'username': 'admin',
            'password': 'password123'
        })
        token = login_response.get_json()['token']

        with mock.patch('Backend.admin.profiles.Database.execute_query', side_effect=RuntimeError('db down')):
            response = self.client.post('/api/profiles', data={'nama_lengkap': 'Test Gagal'}, headers={
                'Authorization': 'Bearer ' + token
            })

        self.assertEqual(response.status_code, 500)
        payload = response.get_json()
        self.assertFalse(payload['success'])
        self.assertIn('database', payload['error'].lower())

    def test_profile_update_accepts_blank_date_values(self):
        login_response = self.client.post('/api/login', json={
            'username': 'admin',
            'password': 'password123'
        })
        token = login_response.get_json()['token']

        response = self.client.post('/api/profiles', data={
            'nama_lengkap': 'Tanggal Kosong',
            'tanggal_lahir': '?'
        }, headers={
            'Authorization': 'Bearer ' + token
        })

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])

    def test_main_profile_endpoint_uses_database_content(self):
        db = Database()
        db.execute_query(
            "REPLACE INTO users (id, username, password_hash, role) VALUES (%s, %s, %s, %s)",
            (1, 'admin', 'dummy', 'admin')
        )
        db.execute_query(
            "DELETE FROM profiles WHERE user_id = %s",
            (1,)
        )
        db.execute_query(
            "INSERT INTO profiles (user_id, nama_lengkap, prodi, universitas, fakultas, semester, alamat, email, foto_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (1, 'Uji Database', 'Teknik Informatika', 'Universitas Uji', 'Teknik', '4', 'Bandung', 'uji@example.com', '')
        )
        db.execute_query(
            "INSERT INTO experiences (user_id, posisi, perusahaan, durasi, deskripsi) VALUES (%s, %s, %s, %s, %s)",
            (1, 'Backend Developer', 'PT Uji', '2024 - Sekarang', 'Mengembangkan API')
        )
        db.execute_query(
            "INSERT INTO projects (user_id, judul, deskripsi, gambar_url, link_project) VALUES (%s, %s, %s, %s, %s)",
            (1, 'Portal Uji', 'Aplikasi test', '', '')
        )
        db.execute_query(
            "INSERT INTO skills (user_id, nama_skill, icon_class) VALUES (%s, %s, %s)",
            (1, 'Flask', 'fab fa-flask')
        )

        response = self.client.get('/api/main-profile')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['data']['nama_lengkap'], 'Uji Database')
        self.assertGreaterEqual(len(payload['data']['experiences']), 1)
        self.assertGreaterEqual(len(payload['data']['projects']), 1)
        self.assertGreaterEqual(len(payload['data']['skills']), 1)

    def test_profile_update_persists_all_supported_fields(self):
        login_response = self.client.post('/api/login', json={
            'username': 'admin',
            'password': 'password123'
        })
        token = login_response.get_json()['token']

        response = self.client.post('/api/profiles', data={
            'nama_lengkap': 'Profil Lengkap',
            'nama_panggilan': 'Lengkap',
            'tempat_lahir': 'Jakarta',
            'tanggal_lahir': '1999-12-31',
            'email': 'lengkap@example.com',
            'telepon': '089999999999',
            'universitas': 'Universitas Lengkap',
            'fakultas': 'Sains',
            'prodi': 'Sistem Informasi',
            'semester': '6',
            'alamat': 'Jakarta Selatan',
            'foto_url': 'https://example.com/avatar.png'
        }, headers={
            'Authorization': 'Bearer ' + token
        })

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])

        db = Database()
        row = db.execute_query(
            'SELECT nama_lengkap, nama_panggilan, tempat_lahir, tanggal_lahir, email, telepon, universitas, fakultas, prodi, semester, alamat, foto_url FROM profiles WHERE user_id = %s',
            (1,),
            fetch=True
        )
        self.assertEqual(len(row), 1)
        saved = row[0]
        self.assertEqual(saved['nama_lengkap'], 'Profil Lengkap')
        self.assertEqual(saved['nama_panggilan'], 'Lengkap')
        self.assertEqual(saved['tempat_lahir'], 'Jakarta')
        self.assertEqual(saved['tanggal_lahir'], date(1999, 12, 31))
        self.assertEqual(saved['email'], 'lengkap@example.com')
        self.assertEqual(saved['telepon'], '089999999999')
        self.assertEqual(saved['universitas'], 'Universitas Lengkap')
        self.assertEqual(saved['fakultas'], 'Sains')
        self.assertEqual(saved['prodi'], 'Sistem Informasi')
        self.assertEqual(saved['semester'], '6')
        self.assertEqual(saved['alamat'], 'Jakarta Selatan')
        self.assertEqual(saved['foto_url'], 'https://example.com/avatar.png')


if __name__ == '__main__':
    unittest.main()

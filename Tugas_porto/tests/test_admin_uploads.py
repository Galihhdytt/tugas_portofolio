import io
import unittest

from app import create_app
from model import Database


class AdminUploadsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_profile_can_store_uploaded_photo(self):
        login_response = self.client.post('/api/login', json={
            'username': 'admin',
            'password': 'password123'
        })
        self.assertEqual(login_response.status_code, 200)
        token = login_response.get_json()['token']

        response = self.client.post('/api/profiles', data={
            'nama_lengkap': 'Budi Santoso',
            'foto': (io.BytesIO(b'fake-image-data'), 'avatar.png')
        }, headers={'Authorization': f'Bearer {token}'})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])

        db = Database()
        result = db.execute_query('SELECT foto_url FROM profiles WHERE user_id = %s', (1,), fetch=True)
        self.assertTrue(result)
        self.assertTrue(result[0]['foto_url'])


if __name__ == '__main__':
    unittest.main()

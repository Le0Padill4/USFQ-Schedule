import unittest
from fastapi.testclient import TestClient
from api.main import app


class CareersEndpointTests(unittest.TestCase):
    def test_only_two_supported_careers(self):
        with TestClient(app) as client:
            response = client.get('/api/v1/careers')
            self.assertEqual(response.status_code, 200)
            self.assertEqual({item['id'] for item in response.json()}, {'1CMP', '1MAC'})
            self.assertTrue(all(item['name'] for item in response.json()))
            self.assertEqual(client.post('/api/v1/careers').status_code, 405)


if __name__ == '__main__':
    unittest.main()

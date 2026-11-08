import unittest
from fastapi.testclient import TestClient
from .flask_app import app as flask_app
from .fastapi_app import app as fastapi_app
class ComparisonTests(unittest.TestCase):
 def test_get_and_methods(self):
  f=flask_app.test_client(); a=TestClient(fastapi_app)
  self.assertEqual(f.get('/').status_code,200); self.assertEqual(f.get('/devices').json,a.get('/devices').json())
  self.assertEqual(f.get('/devices/1').json,a.get('/devices/1').json())
  self.assertEqual(f.get('/devices/999').status_code,404); self.assertEqual(a.get('/devices/999').status_code,404)
  self.assertEqual(f.get('/devices/wrong').status_code,404); self.assertEqual(a.get('/devices/wrong').status_code,422)
  self.assertEqual(f.post('/devices/1').status_code,405); self.assertEqual(a.post('/devices/1').status_code,405)
  self.assertEqual(a.get('/openapi.json').status_code,200)

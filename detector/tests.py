from django.test import TestCase
from django.urls import reverse
import base64
import json
import cv2
import numpy as np

class DetectorTests(TestCase):
    def test_home(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('csrftoken', response.cookies)

    def test_invalid_image_rejected(self):
        response = self.client.post(reverse('analyze'), data=json.dumps({'image': 'incorrecta'}), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_blank_frame(self):
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        ok, encoded = cv2.imencode('.jpg', image)
        self.assertTrue(ok)
        payload = 'data:image/jpeg;base64,' + base64.b64encode(encoded).decode('ascii')
        response = self.client.post(reverse('analyze'), data=json.dumps({'image': payload}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

    def test_save_count(self):
        response = self.client.post(reverse('save_count'), data=json.dumps({'count': 2}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        from .models import DetectionRecord
        self.assertEqual(DetectionRecord.objects.count(), 1)

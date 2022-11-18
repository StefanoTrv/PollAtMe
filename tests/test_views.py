from django.test import Client, TestCase

class ViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()

    def test_sondaggi_attivi(self):
        resp = self.client.get('')
        self.assertEqual(resp.status_code, 200)
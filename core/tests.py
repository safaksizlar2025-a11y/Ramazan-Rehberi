from django.test import TestCase
from django.urls import reverse


class CoreViewsSmokeTests(TestCase):
    def test_ana_sayfa_works(self):
        response = self.client.get(reverse('ana_sayfa'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')

    def test_imsakiye_works(self):
        response = self.client.get(reverse('imsakiye'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/imsakiye.html')

    def test_amel_defterim_works(self):
        response = self.client.get(reverse('amel_defterim'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/amel_defterim.html')

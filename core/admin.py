from django.contrib import admin
from .models import Ayet, Hadis, NamazVakti # Modellerini buradan içeri aktarıyorsun

# Modellerini admin paneline kayıt ediyorsun
admin.site.register(Ayet)
admin.site.register(Hadis)
admin.site.register(NamazVakti)

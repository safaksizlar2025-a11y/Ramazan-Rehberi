from django.db import models

class Ayet(models.Model):
    metin = models.TextField(verbose_name="Ayet Metni")
    kaynak = models.CharField(max_length=250, verbose_name="Sure/Ayet No")
    ramazan_gunu = models.PositiveIntegerField(unique=True, verbose_name="Ramazan Günü (1-30)")

    class Meta:
        verbose_name = "Ayet"
        verbose_name_plural = "Ayetler"

    def __str__(self):
        return f"Görüntülenecek Gün: {self.ramazan_gunu}"

class Hadis(models.Model):
    metin = models.TextField(verbose_name="Hadis Metni")
    kaynak = models.CharField(max_length=250, verbose_name="Hadis Kaynağı")
    ramazan_gunu = models.PositiveIntegerField(unique=True, verbose_name="Ramazan Günü (1-30)")

    class Meta:
        verbose_name = "Hadis"
        verbose_name_plural = "Hadisler"

    def __str__(self):
        return f"Görüntülenecek Gün: {self.ramazan_gunu}"

class NamazVakti(models.Model):
    sehir = models.CharField(max_length=100, verbose_name="Şehir")
    tarih = models.DateField(verbose_name="Tarih")
    imsak = models.TimeField()
    ogle = models.TimeField()
    ikindi = models.TimeField()
    aksam = models.TimeField(verbose_name="İftar (Akşam)")
    yatsi = models.TimeField()

    class Meta:
        verbose_name = "Namaz Vakti"
        verbose_name_plural = "Namaz Vakitleri"
        unique_together = ['sehir', 'tarih'] # Aynı şehre aynı gün iki kayıt girilmesini engeller

    def __str__(self):
        return f"{self.sehir} - {self.tarih}"
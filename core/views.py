from django.shortcuts import render
from .models import Ayet, Hadis
from .data import AYETLER_LISTESI, HADISLER_LISTESI
from datetime import date,datetime
import requests
from .utils import gunun_ayeti_getir
from datetime import datetime, timedelta

# Yardımcı Fonksiyon: Şehir-Ülke eşleşmesi
def ulke_bul(sehir):
    ozel_durumlar = {
        "Berlin": "Germany",
        "London": "United Kingdom",
        "Paris": "France",
        "Vienna": "Austria"
    }
    return ozel_durumlar.get(sehir, "Turkey")

def ana_sayfa(request):
    sehir = request.GET.get('sehir', 'Istanbul')
    ulke = ulke_bul(sehir)

    # Ramazan Günü Hesaplama (aynı kalıyor)
    ramazan_baslangic = date(2026, 2, 19) 
    bugun = date.today()
    gun_no = (bugun - ramazan_baslangic).days + 1
    index = (gun_no - 1) if 1 <= gun_no <= 30 else 0

    ayet_verisi = gunun_ayeti_getir(gun_no)
    secili_hadis = HADISLER_LISTESI[index % len(HADISLER_LISTESI)]

    # GÜNCELLEME: Method 13'e ek olarak Turkey/Diyanet spesifik parametreler ekledik
    # method=13 (Diyanet), school=1 (Hanefi)
    url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country={ulke}&method=13"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            vakitler = response.json().get('data', {}).get('timings', {})
            
            # Diyanet uyumu için düzeltmeler
            fmt = "%H:%M"
            def fix(t_str, mins):
                return (datetime.strptime(t_str, fmt) + timedelta(minutes=mins)).strftime(fmt)

            vakitler['Imsak'] = fix(vakitler['Imsak'], 10)   # 06:06 -> 06:16
            vakitler['Asr'] = fix(vakitler['Asr'], 1)       # İkindi +1 dk
            vakitler['Maghrib'] = fix(vakitler['Maghrib'], -1) # Akşam -1 dk
            vakitler['Isha'] = fix(vakitler['Isha'], -1)    # Yatsı -1 dk
    except Exception as e:
        vakitler = None

    context = {
        'ayet': ayet_verisi,
        'hadis': secili_hadis,
        'gun_no': gun_no,
        'vakitler': vakitler,
        'sehir': sehir
    }
    return render(request, 'core/index.html', context)

def imsakiye_sayfasi(request):
    sehir = request.GET.get('sehir', 'Istanbul')
    ulke = ulke_bul(sehir)

    # Ay isimleri dönüşüm sözlüğü
    aylar_tr = {
        "Feb": "Şubat",
        "Mar": "Mart",
        "Apr": "Nisan"
    }
    
    # Şubat ve Mart verilerini çekmek için aylar listesi
    ramazan_aylari = [2, 3] 
    imsakiye_listesi = []
    
    for ay in ramazan_aylari:
        url = f"http://api.aladhan.com/v1/calendarByCity/2026/{ay}?city={sehir}&country={ulke}&method=13"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json().get('data', [])
                for gun in data:
                    gun_tarihi_str = gun['date']['gregorian']['date']
                    gun_obj = datetime.strptime(gun_tarihi_str, '%d-%m-%Y').date()
                    
                    # 18 Şubat'tan öncesini ve 19 Mart'tan (Ramazan sonu) sonrasını ele
                    if gun_obj < date(2026, 2, 18) or gun_obj > date(2026, 3, 19):
                        continue

                    tarih_ham = gun['date']['readable'] # Örn: "21 Feb 2026"
                
                    # İngilizce ay ismini bul ve Türkçesiyle değiştir
                    tarih_tr = tarih_ham
                    for eng, tr in aylar_tr.items():
                        if eng in tarih_ham:
                            tarih_tr = tarih_ham.replace(eng, tr)
                            break
                    
                    imsakiye_listesi.append({
                        'tarih': tarih_tr,
                        'imsak': gun['timings']['Imsak'].split(' ')[0],
                        'gunes': gun['timings']['Sunrise'].split(' ')[0],
                        'ogle': gun['timings']['Dhuhr'].split(' ')[0],
                        'ikindi': gun['timings']['Asr'].split(' ')[0],
                        'aksam': gun['timings']['Maghrib'].split(' ')[0],
                        'yatsı': gun['timings']['Isha'].split(' ')[0],
                        'is_today': gun_obj == date.today()
                    })
        except Exception: continue
    
    return render(request, 'core/imsakiye.html', {'imsakiye': imsakiye_listesi, 'sehir': sehir})


def amel_defterim(request):
    # Şimdilik içi boş, sadece sayfayı döndürecek
    return render(request, 'core/amel_defterim.html')
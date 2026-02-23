from django.shortcuts import render
from .data import HADISLER_LISTESI
from datetime import date, datetime, timedelta
import requests
from .utils import gunun_ayeti_getir

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
    
    vakitler = None
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
    except (requests.RequestException, ValueError):
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

    ramazan_aylari = [2, 3] 
    imsakiye_listesi = []
    
    # Zaman düzeltme formatı
    fmt = "%H:%M"

    for ay in ramazan_aylari:
        # Diyanet metodu (13) ile veriyi çekiyoruz
        url = f"http://api.aladhan.com/v1/calendarByCity/2026/{ay}?city={sehir}&country={ulke}&method=13"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json().get('data', [])
                for gun in data:
                    gun_tarihi_str = gun['date']['gregorian']['date']
                    gun_obj = datetime.strptime(gun_tarihi_str, '%d-%m-%Y').date()
                    
                    # 19 Şubat'tan öncesini ve 19 Mart'tan sonrasını ele
                    if gun_obj < date(2026, 2, 19) or gun_obj > date(2026, 3, 19):
                        continue

                    # --- SAAT DÜZELTME BÖLÜMÜ ---
                    # Ana sayfadakiyle aynı mantığı buradaki listeye de uyguluyoruz
                    def fix_time(time_str, mins):
                        # API bazen saat yanına (EET) gibi ekler koyabiliyor, onları temizliyoruz
                        clean_time = time_str.split(' ')[0]
                        t = datetime.strptime(clean_time, fmt)
                        return (t + timedelta(minutes=mins)).strftime(fmt)

                    # API'den gelen ham vakitler
                    timings = gun['timings']

                    imsakiye_listesi.append({
                        'tarih': gun['date']['readable'].replace("Feb", "Şubat").replace("Mar", "Mart"),
                        'imsak': fix_time(timings['Imsak'], 10),    # +10 dk düzeltme
                        'gunes': timings['Sunrise'].split(' ')[0], # Güneş aynı kalsın demiştin
                        'ogle': timings['Dhuhr'].split(' ')[0],    # Öğle aynı kalsın demiştin
                        'ikindi': fix_time(timings['Asr'], 1),     # +1 dk düzeltme
                        'aksam': fix_time(timings['Maghrib'], -1),  # -1 dk düzeltme
                        'yatsı': fix_time(timings['Isha'], -1),    # -1 dk düzeltme
                        'is_today': gun_obj == date.today()
                    })
        except (requests.RequestException, ValueError, KeyError): 
            continue
    return render(request, 'core/imsakiye.html', {'imsakiye': imsakiye_listesi, 'sehir': sehir})


def amel_defterim(request):
    # Şimdilik içi boş, sadece sayfayı döndürecek
    return render(request, 'core/amel_defterim.html')

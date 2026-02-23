import requests

def gunun_ayeti_getir(gun_no):
    # Kendi seçtiğin (Sure:Ayet) formatındaki liste
    ozel_ayetler = [
        "2:183", "2:185", "3:133", "33:35", "2:153", "16:128" # 30'a tamamla
    ]
    # gun_no'ya göre listeden bir adres seç (indis 0'dan başladığı için -1)
    secili_adres = ozel_ayetler[(gun_no - 1) % len(ozel_ayetler)]
    # Alquran.cloud API: Sure:Ayet formatında Türkçe meal getirir
    # Örnek: 2:183 (Bakara 183)
    url = f"https://api.alquran.cloud/v1/ayah/{secili_adres}/tr.diyanet"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "metin": data['data']['text'],
                "kaynak": f"{data['data']['surah']['englishName']} - {data['data']['numberInSurah']}"
            }
    except:
        return {"metin": "Ramazan berekettir.", "kaynak": "Bakara 183"}
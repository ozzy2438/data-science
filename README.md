# CSV Data Analysis Assistant

Bu uygulama, veri bilimcilerin CSV dosyalarını analiz etmelerine ve içgörüler elde etmelerine yardımcı olan bir araçtır. Google Gemini AI destekli analiz özellikleri içerir.

## Özellikler

- CSV dosyası yükleme ve önizleme
- Temel veri istatistikleri
- Veri görselleştirme
- AI destekli veri analizi
- Eksik veri analizi

## Kurulum

1. Python 3.11 ortamını oluşturun:
```bash
python3.11 -m venv venv
```

2. Sanal ortamı aktifleştirin:
```bash
source venv/bin/activate  # Unix/macOS
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. `.env` dosyasında Google Gemini API anahtarınızı ayarlayın

## Kullanım

Uygulamayı başlatmak için:
```bash
streamlit run src/app.py
```

## Gereksinimler

- Python 3.11
- Streamlit
- Pandas
- Plotly
- Google Generative AI
- Diğer gereksinimler requirements.txt dosyasında listelenmiştir 
import json
import subprocess
import time

# Yorumları yükle
with open("data/response.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Yayınlanmış ve uzun yorumları filtrele
reviews = [r for r in data["reviews"] if r.get("status") == "published" and len(r.get("comment", "")) > 10]

batch_size = 10

for i in range(0, len(reviews), batch_size):
    batch = reviews[i:i + batch_size]
    if not batch:
        continue

    print(f"\n🔄 İşleniyor: Yorum {i+1} - {i+len(batch)} arası")

    # PROMPT oluştur
    prompt = (
        "Aşağıda 10 yorumu göreceksin.\n"
        "Her yorum için:\n"
        "1) yorumun duygusunu 'positive' | 'negative' | 'neutral' olarak belirtin\n"
        "2) yorumda hangi ürün özellikleri geçiyor? (kalite, fiyat, kargo, ambalaj, kullanım, destek)\n"
        "3) ürünün artı yönlerini çıkarın\n"
        "4) ürünün eksi yönlerini çıkarın\n"
        "Lütfen şöyle bir JSON çıktısı verin:\n"
        "[\n"
        "  { \"sentiment\": \"...\", \"features\": [...], \"pros\": [...], \"cons\": [...] },\n"
        "  ...\n"
        "]\n\n"
    )

    for idx, review in enumerate(batch, 1):
        comment = review["comment"].replace("\n", " ").strip()
        prompt += f"{idx}. {comment}\n"

    print("\n📤 MODELE GİDEN PROMPT:\n", prompt)

    # Modele gönder
    command = ['ollama', 'run', 'mistral:7b-instruct', prompt]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        output = result.stdout.decode('utf-8', errors='ignore')
    except Exception as e:
        output = result.stdout.decode(errors='replace')

    print("\n📥 MODEL ÇIKTISI:\n")
    print(output)
    print("-" * 80)

    time.sleep(1)

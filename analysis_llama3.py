from preprocessing import load_and_clean_reviews, basic_stats, top_words
import subprocess
import time

# Load and clean reviews
clean_reviews = load_and_clean_reviews("response.json")

# Print basic statistics
basic_stats(clean_reviews)

# Show top 10 most frequent words
top_words(clean_reviews)

# ---- OLLAMA LLM: AUTOMATIC PRODUCT INSIGHTS (THREE MAIN QUESTIONS) ----

print("\n--- 1) COMMON PROBLEMS FOR THE SELLER ---")
all_comments = "\n".join([r["comment"] for r in clean_reviews])

def ollama_ask(prompt, model="llama3"):
    command = f'ollama run {model} "{prompt}"'
    result = subprocess.run(
        command,
        capture_output=True, text=True, encoding="utf-8", shell=True
    )
    return result.stdout

# 1) ÜRÜNLE İLGİLİ SIK SORUNLAR
prompt_problems = (
    "Aşağıdaki müşteri yorumlarını dikkatlice oku. "
    "Bu ürünle ilgili en sık tekrar eden 3 ana SORUNU madde madde ve çok kısa özetle. "
    "Sadece sorunları maddeler halinde yaz, açıklama veya başka cümle yazma.\n\n"
    + all_comments
)
problems_summary = ollama_ask(prompt_problems)
print(problems_summary)

# 2) TÜKETİCİYE TAVSİYELER
print("\n--- 2) TIPS & ADVICES FOR THE CUSTOMER ---")
prompt_advices = (
    "Aşağıdaki müşteri yorumlarını dikkatlice oku. "
    "Bu ürünü alacaklara en faydalı olacak 3 TAVSİYEYİ madde madde ve çok kısa şekilde yaz. "
    "Sadece tavsiyeleri yaz, ekstra açıklama yapma.\n\n"
    + all_comments
)
advices_summary = ollama_ask(prompt_advices)
print(advices_summary)

# 3) TÜM YORUMLARI ETİKETLE (SENTIMENT)
print("\n--- 3) LABEL EACH REVIEW AS POSITIVE / NEGATIVE / NEUTRAL ---")
for i, review in enumerate(clean_reviews, 1):
    # Kısa ve kuralcı prompt
    sentiment_prompt = (
        "Aşağıdaki yorumu sadece şu üç etiketten biriyle etiketle: pozitif, negatif veya nötr. "
        "Başka hiçbir açıklama veya cümle yazma, SADECE etiketi döndür.\n"
        f"Yorum: {review['comment']}"
    )
    sentiment = ollama_ask(sentiment_prompt).strip().split("\n")[0].lower()
    print(f"Review {i}: {review['comment']}")
    print("Sentiment:", sentiment)
    print("-" * 60)

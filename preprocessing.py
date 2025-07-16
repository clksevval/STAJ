# preprocessing.py

import json
import re
from collections import Counter

def load_and_clean_reviews(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    clean_reviews = []
    for review in data["reviews"]:
        comment = review.get("comment", "")
        comment = re.sub(r"<.*?>", "", comment)
        if len(comment.strip()) < 10:
            continue
        if review.get("status") != "published":
            continue
        review["comment"] = comment
        clean_reviews.append(review)
    return clean_reviews

def basic_stats(clean_reviews):
    ratings = [r.get("rating", {}).get("code", 0) for r in clean_reviews]
    average_rating = sum(ratings) / len(ratings) if ratings else 0
    recommended = sum(1 for r in clean_reviews if r.get("recommended"))
    not_recommended = sum(1 for r in clean_reviews if not r.get("recommended"))
    print(f"Number of clean reviews: {len(clean_reviews)}")
    print(f"Average Rating: {average_rating:.2f}")
    print(f"Recommended: {recommended} ({100 * recommended / len(clean_reviews):.1f}%)")
    print(f"Not Recommended: {not_recommended} ({100 * not_recommended / len(clean_reviews):.1f}%)\n")

def top_words(clean_reviews, top_n=10):
    words = []
    for r in clean_reviews:
        words += re.findall(r"\b\w+\b", r["comment"].lower())
    stopwords = set([
        "i", "a", "ve", "bir", "çok", "da", "de", "ile", "için", "ama", "bu", "ben", "olan", "gibi", "daha", "en",
        "biraz", "az", "o", "yok", "mi", "veya", "var"
    ])
    filtered_words = [word for word in words if word not in stopwords]
    most_common = Counter(filtered_words).most_common(top_n)
    print("\nTop 10 most frequent words:")
    for word, count in most_common:
        print(f"{word}: {count}")

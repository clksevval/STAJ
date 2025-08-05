import logging
import uuid
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from collections import defaultdict, Counter
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

# Proje ayarları (veritabanı bağlantı dizesi ve model ismi burada tanımlı)
from app.core.config import settings
# LLM (dil modeli) ile etkileşim sağlayan servis sınıfı ve çıkacak veriyi tanımlayan model
from main import LLMService, ReviewFields

# Loglama formatı ayarlanıyor
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==============================================================================
# SummaryClusterer Sınıfı
# ==============================================================================
class SummaryClusterer:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    def fetch_fields_for_product(self, product_id: str) -> dict:
        product_fields = defaultdict(list)
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    query = """
                    SELECT ra.pros, ra.cons, ra.complaints, ra.suggestions
                    FROM review_analysis ra
                    JOIN raw_reviews rr ON rr.id = ra.review_id
                    WHERE rr.product_id = %s;
                    """
                    cur.execute(query, (product_id,))
                    rows = cur.fetchall()
                    if not rows:
                        logging.warning(f"Product ID '{product_id}' için analiz edilmiş yorum bulunamadı.")
                        return {}
                    for pros, cons, complaints, suggestions in rows:
                        if pros: product_fields["pros"].extend(pros)
                        if cons: product_fields["cons"].extend(cons)
                        if complaints: product_fields["complaints"].extend(complaints)
                        if suggestions: product_fields["suggestions"].extend(suggestions)
        except psycopg2.Error as e:
            logging.error(f"Veritabanı hatası (fetch_fields_for_product): {e}")
        return product_fields

    def cluster_and_count_phrases(self, phrases: list[str], n_clusters=10, top_k=5) -> dict:
        phrases = [p.strip().lower() for p in phrases if p and p.strip()]
        if not phrases: return {}
        unique_phrases = list(set(phrases))
        if len(unique_phrases) < 2: return dict(Counter(phrases).most_common(top_k))
        embeddings = self.model.encode(unique_phrases)
        cluster_count = min(n_clusters, len(unique_phrases))
        kmeans = KMeans(n_clusters=cluster_count, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(embeddings)
        cluster_map = defaultdict(list)
        for label, phrase in zip(labels, unique_phrases):
            cluster_map[label].append(phrase)
        phrase_to_cluster_rep = {}
        for cluster_id, phrases_in_cluster in cluster_map.items():
            representative = min(phrases_in_cluster, key=len)
            for phrase in phrases_in_cluster:
                phrase_to_cluster_rep[phrase] = representative
        counts = Counter([phrase_to_cluster_rep[p] for p in phrases])
        return dict(counts.most_common(top_k))

    def update_product_summary(self, product_id: str, summary: dict):
        query = """
        INSERT INTO analysis_summary (product_id, total_reviews, top_pros, top_cons, top_complaints, top_suggestions)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_id) DO UPDATE SET
            total_reviews = EXCLUDED.total_reviews, top_pros = EXCLUDED.top_pros,
            top_cons = EXCLUDED.top_cons, top_complaints = EXCLUDED.top_complaints,
            top_suggestions = EXCLUDED.top_suggestions, last_updated = NOW();
        """
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (
                        product_id, summary.get("total_reviews", 0),
                        json.dumps(summary.get("pros", {}), ensure_ascii=False),
                        json.dumps(summary.get("cons", {}), ensure_ascii=False),
                        json.dumps(summary.get("complaints", {}), ensure_ascii=False),
                        json.dumps(summary.get("suggestions", {}), ensure_ascii=False)
                    ))
            logging.info(f"analysis_summary tablosu product_id '{product_id}' için güncellendi.")
        except psycopg2.Error as e:
            logging.error(f"Özet güncellenirken veritabanı hatası oluştu (product_id: {product_id}): {e}")

    def run(self, product_id: str):
        logging.info(f"'{product_id}' ID'li ürün için özetleme işlemi başlatılıyor...")
        product_fields = self.fetch_fields_for_product(product_id)
        if not product_fields:
            logging.warning(f"'{product_id}' için işlenecek veri bulunamadı. Özetleme atlanıyor.")
            return
        total_reviews_count = sum(len(v) for v in product_fields.values())
        summary = {
            "pros": self.cluster_and_count_phrases(product_fields.get("pros", [])),
            "cons": self.cluster_and_count_phrases(product_fields.get("cons", [])),
            "complaints": self.cluster_and_count_phrases(product_fields.get("complaints", [])),
            "suggestions": self.cluster_and_count_phrases(product_fields.get("suggestions", [])),
            "total_reviews": total_reviews_count,
        }
        self.update_product_summary(product_id, summary)

# ==============================================================================
# DatabaseService Sınıfı
# ==============================================================================
class DatabaseService:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True

    def insert_raw_reviews(self, reviews: list[dict]):
        try:
            with self.conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO raw_reviews (id, product_id, rating_code, title, comment,
                                           language_code, country_code, author_username,
                                           publisher_date, attributes)
                    VALUES (%(id)s, %(product_id)s, %(rating_code)s, %(title)s, %(comment)s,
                            %(language_code)s, %(country_code)s, %(author_username)s,
                            %(publisher_date)s, %(attributes)s)
                    ON CONFLICT (id) DO NOTHING;
                    """,
                    reviews
                )
                logging.info(f"Inserted {cur.rowcount} new reviews.")
        except Exception as e:
            logging.error(f"Failed to insert reviews: {e}")

    def get_pending_reviews(self, product_id: str, limit: int = 50) -> list[dict]:
        query = """
            SELECT rr.id, rr.comment
            FROM raw_reviews rr
            LEFT JOIN review_analysis ra ON rr.id = ra.review_id
            WHERE ra.review_id IS NULL AND rr.product_id = %s
            ORDER BY rr.id
            LIMIT %s;
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (product_id, limit))
                return cur.fetchall()
        except Exception as e:
            logging.error(f"Failed to fetch pending reviews for product_id {product_id}: {e}")
            return []

    def save_analysis_result(self, review_id: uuid.UUID, analysis_data: ReviewFields):
        query = """
            INSERT INTO review_analysis (review_id, sentiment, pros,
                                       cons, complaints, suggestions, expectations, feature_categories)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        data = analysis_data.model_dump()
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (
                    review_id, data.get('sentiment'), json.dumps(data.get('pros'), ensure_ascii=False),
                    json.dumps(data.get('cons'), ensure_ascii=False), json.dumps(data.get('complaints'), ensure_ascii=False),
                    json.dumps(data.get('suggestions'), ensure_ascii=False), json.dumps(data.get('expectations'), ensure_ascii=False),
                    json.dumps(data.get('feature_categories'), ensure_ascii=False)
                ))
                logging.info(f"Saved analysis for review_id: {review_id}")
        except Exception as e:
            logging.error(f"Failed to save analysis result for review_id {review_id}: {e}")

# ==============================================================================
# Yardımcı Fonksiyonlar ve Ana İş Akışı
# ==============================================================================
# GÜNCELLEME: Fonksiyon artık işlenecek ürünün ID'sini parametre olarak alıyor.
def fetch_reviews_from_local(path: str, target_product_id: str) -> List[Dict[str, Any]]:
    """
    JSON dosyasından yorumları okur ve sadece 'target_product_id' ile eşleşenleri alır.
    """
    logging.info(f"Loading reviews from local JSON: {path} for product_id: {target_product_id}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        if isinstance(json_data, dict) and 'reviews' in json_data:
            review_list = json_data['reviews']
        else:
            review_list = json_data

        raw_reviews = []
        for item in review_list:
            if isinstance(item, str):
                try:
                    item = json.loads(item)
                except json.JSONDecodeError:
                    logging.warning(f"Could not decode JSON string, skipping: {item}")
                    continue
            
            # YENİ: JSON'daki 'identifier' ile hedef ID'yi karşılaştır.
            item_identifier = item.get("subject", {}).get("identifier")
            if item_identifier != target_product_id:
                continue  # Eşleşmiyorsa bu yorumu atla.

            if not item.get("comment"):
                continue
                
            raw_reviews.append({
                "id": item.get("id"),
                # YENİ: Veri bütünlüğü için manuel olarak belirtilen ID'yi kullan.
                "product_id": target_product_id,
                "rating_code": item.get("rating", {}).get("code"),
                "title": item.get("title", ""),
                "comment": item.get("comment", ""),
                "language_code": item.get("language", {}).get("code", "tr"),
                "country_code": item.get("country", {}).get("code", "TR"),
                "author_username": item.get("author", {}).get("username", "anon"),
                "publisher_date": item.get("publisherDate"),
                "attributes": json.dumps(item.get("attributes", []))
            })
        logging.info(f"Loaded {len(raw_reviews)} matching reviews for product_id {target_product_id}.")
        return raw_reviews
    except FileNotFoundError:
        logging.error(f"HATA: Belirtilen JSON dosyası bulunamadı: {path}")
        return []
    except Exception as e:
        logging.error(f"Error reading local reviews: {e}")
        return []

def main_workflow():
    """Yorumları yükler, veritabanına ekler, işlenmemişleri LLM ile analiz eder ve sonucu tekrar veritabanına yazar."""
    db_service = DatabaseService(settings.DATABASE_URL)
    llm_service = LLMService()

    # YENİ: İşlemek istediğiniz ürünün ID'sini ve JSON dosyasının yolunu burada belirtin.
    TARGET_PRODUCT_ID = "8883139"  # Burayı analiz etmek istediğiniz ürünün ID'si ile değiştirin.
    LOCAL_JSON_PATH = "C:/Users/SEVVAL/Desktop/workflow/8883139_kazak.json"

    logging.info(f"--- PHASE 1: FETCHING REVIEWS FOR PRODUCT_ID '{TARGET_PRODUCT_ID}' FROM {LOCAL_JSON_PATH} ---")
    # GÜNCELLEME: Fonksiyona hedef ID parametre olarak veriliyor.
    fetched_reviews = fetch_reviews_from_local(LOCAL_JSON_PATH, target_product_id=TARGET_PRODUCT_ID)

    if not fetched_reviews:
        logging.warning("JSON dosyasında belirtilen ürün ID'sine ({TARGET_PRODUCT_ID}) ait hiç yorum bulunamadı veya dosya okunamadı. İş akışı durduruluyor.")
        return

    # Otomatik ID alımına artık gerek yok, her şey manuel ID üzerinden yürüyor.
    logging.info(f"Target Product ID for this workflow is set to: {TARGET_PRODUCT_ID}")
    db_service.insert_raw_reviews(fetched_reviews)
    
    logging.info(f"--- PHASE 2: PROCESSING PENDING REVIEWS FOR PRODUCT: {TARGET_PRODUCT_ID} ---")
    pending_reviews = db_service.get_pending_reviews(product_id=TARGET_PRODUCT_ID) 
    total = len(pending_reviews)
    success, failed = 0, 0

    if not pending_reviews:
        logging.info("Bu ürün için veritabanında işlenecek yeni yorum bulunmuyor.")
    else:
        for review in pending_reviews:
            review_id, comment_text = review['id'], review['comment']
            try:
                analysis_result = llm_service.analyse_review(comment_text)
                if analysis_result:
                    db_service.save_analysis_result(review_id, analysis_result)
                    success += 1
                else:
                    failed += 1
                    logging.warning(f"Analysis for review_id {review_id} returned None.")
            except Exception as e:
                failed += 1
                logging.error(f"Critical error during processing of review_id {review_id}: {e}")

    logging.info(f"--- PHASE 3: CLUSTERING + SUMMARY FOR PRODUCT: {TARGET_PRODUCT_ID} ---")
    clusterer = SummaryClusterer(settings.DATABASE_URL)
    clusterer.run(product_id=TARGET_PRODUCT_ID) 
    
    logging.info("----- ANALYSIS SUMMARY -----")
    logging.info(f"Total new reviews processed: {total}")
    logging.info(f"Successfully analyzed and saved: {success}")
    logging.info(f"Failed to analyze: {failed}")

if __name__ == "__main__":
    main_workflow()

import logging
import uuid
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any

# Proje ayarları (veritabanı bağlantı dizesi ve model ismi burada tanımlı)
from app.core.config import settings

# LLM (dil modeli) ile etkileşim sağlayan servis sınıfı ve çıkacak veriyi tanımlayan model
from main import LLMService, ReviewFields

# Loglama formatı ayarlanıyor
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseService:
    """
    Veritabanıyla bağlantı kurar, yorumları ekler, eksik analizleri çeker, analiz sonuçlarını kaydeder.
    """
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = psycopg2.connect(dsn)  # Veritabanına bağlan
        self.conn.autocommit = True        # Otomatik commit (her işlemden sonra veritabanı güncellensin)

    def insert_raw_reviews(self, reviews: list[dict]):
        """
        JSON'dan gelen yorumları raw_reviews tablosuna ekler. ID çakışmalarında yeni veri yazmaz.
        """
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
                    ON CONFLICT (id) DO NOTHING;  -- Aynı ID varsa ekleme
                    """,
                    reviews
                )
                logging.info(f"Inserted {cur.rowcount} new reviews.")
        except Exception as e:
            logging.error(f"Failed to insert reviews: {e}")

    def get_pending_reviews(self, limit: int = 10) -> list[dict]:
        """
        Daha önce işlenmemiş yorumları çeker (analizi yapılmamış olanlar).
        """
        query = """
            SELECT rr.id, rr.comment
            FROM raw_reviews rr
            LEFT JOIN review_analysis ra ON rr.id = ra.review_id
            WHERE ra.review_id IS NULL  -- Henüz analiz edilmemişler
            ORDER BY rr.id
            LIMIT %s;
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (limit,))
                return cur.fetchall()
        except Exception as e:
            logging.error(f"Failed to fetch pending reviews: {e}")
            return []

    def save_analysis_result(self, review_id: uuid.UUID, analysis_data: ReviewFields):
        """
        LLM çıktısı olan analiz sonuçlarını review_analysis tablosuna kaydeder.
        """
        query = """
            INSERT INTO review_analysis (review_id, sentiment, pros,
                                       cons, complaints, suggestions, expectations, feature_categories)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        data = analysis_data.model_dump()  # Pydantic objesini dict'e çevir
        
        # Debug: Ham veriyi logla
        logging.info(f"DEBUG - Raw analysis data for review_id {review_id}:")
        logging.info(f"  sentiment: {data.get('sentiment')}")
        logging.info(f"  pros: {data.get('pros')}")
        logging.info(f"  cons: {data.get('cons')}")
        logging.info(f"  complaints: {data.get('complaints')}")
        logging.info(f"  suggestions: {data.get('suggestions')}")
        logging.info(f"  expectations: {data.get('expectations')}")
        logging.info(f"  feature_categories: {data.get('feature_categories')}")
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (
                    review_id,
                    data['sentiment'],
                    json.dumps(data['pros']),
                    json.dumps(data['cons']),
                    json.dumps(data['complaints']),
                    json.dumps(data['suggestions']),
                    json.dumps(data['expectations']),
                    json.dumps(data['feature_categories'])
                ))
                logging.info(f"Saved analysis for review_id: {review_id}")
        except Exception as e:
            logging.error(f"Failed to save analysis result for review_id {review_id}: {e}")


def fetch_reviews_from_local(path: str) -> List[Dict[str, Any]]:
    """
    JSON dosyasından yorumları okuyup, veritabanına uygun forma sokar.
    """
    logging.info(f"Loading reviews from local JSON: {path}...")

    try:
        with open(path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        raw_reviews = []

        for item in json_data:
            if not item.get("comment"):  # Yorumu olmayanları atla
                continue

            if "title" not in item:
                logging.warning(f"Missing title in review ID: {item.get('id')}")

            raw_reviews.append({
                "id": item.get("id"),
                "product_id": item.get("subject", {}).get("identifier"),
                "rating_code": item.get("rating", {}).get("code"),
                "title": item.get("title", ""),
                "comment": item.get("comment", ""),
                "language_code": item.get("language", {}).get("code", "tr"),
                "country_code": item.get("country", {}).get("code", "TR"),
                "author_username": item.get("author", {}).get("username", "anon"),
                "publisher_date": item.get("publisherDate"),
                "attributes": json.dumps(item.get("attributes", []))
            })

        logging.info(f"Loaded {len(raw_reviews)} reviews from local JSON.")
        return raw_reviews

    except Exception as e:
        logging.error(f"Error reading local reviews: {e}")
        return []


def main_workflow():
    """
    Yorumları yükler, veritabanına ekler, işlenmemişleri LLM ile analiz eder ve sonucu tekrar veritabanına yazar.
    """
    db_service = DatabaseService(settings.DATABASE_URL)
    llm_service = LLMService()

    # Aşama 1: Yerel JSON dosyasından yorumları çek ve DB'ye kaydet
    logging.info("--- PHASE 1: FETCHING AND STORING RAW REVIEWS ---")
    LOCAL_JSON_PATH = "C:/Users/sude/Desktop/Staj/Pull1/STAJ/workflow_code/product_8118521_reviews.json"
    fetched_reviews = fetch_reviews_from_local(LOCAL_JSON_PATH)

    if fetched_reviews:
        db_service.insert_raw_reviews(fetched_reviews)

    # Aşama 2: Henüz analiz edilmemiş yorumları al
    logging.info("--- PHASE 2: PROCESSING PENDING REVIEWS ---")
    pending_reviews = db_service.get_pending_reviews()

    total = len(pending_reviews)
    success = 0
    failed = 0

    if not pending_reviews:
        logging.info("No pending reviews to process. Workflow finished.")
        return

    # Her yorum için analiz yap ve sonucu kaydet
    for review in pending_reviews:
        review_id = review['id']
        comment_text = review['comment']

        try:
            analysis_result = llm_service.analyse_review(comment_text)

            if analysis_result:
                db_service.save_analysis_result(review_id, analysis_result)
                success += 1
            else:
                failed += 1
                logging.warning(f"Analysis for review_id {review_id} returned None. Skipping save.")

        except Exception as e:
            failed += 1
            logging.error(f"Critical error during processing of review_id {review_id}: {e}")

    # Özet log
    logging.info("----- ANALYSIS SUMMARY -----")
    logging.info(f"Total pending reviews fetched: {total}")
    logging.info(f"Successfully analyzed and saved: {success}")
    logging.info(f"Failed to analyze: {failed}")


# Script olarak çalıştırıldığında workflow'u başlat
if __name__ == "__main__":
    main_workflow()

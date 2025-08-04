import logging
import uuid
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any

from app.core.config import settings
from main import LLMService, ReviewFields

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

    def get_pending_reviews(self, limit: int = 10) -> list[dict]:
        query = """
            SELECT rr.id, rr.comment
            FROM raw_reviews rr
            LEFT JOIN review_analysis ra ON rr.id = ra.review_id
            WHERE ra.review_id IS NULL
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
        query = """
            INSERT INTO review_analysis (review_id, sentiment, sentiment_confidence, pros,
                                       cons, complaints, suggestions, expectations, feature_categories)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        data = analysis_data.model_dump()
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (
                    review_id,
                    data['sentiment'],
                    data['sentiment_confidence'],
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
    logging.info(f"Loading reviews from local JSON: {path}...")

    try:
        with open(path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        raw_reviews = []

        for item in json_data:
            if not item.get("comment"):
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
    db_service = DatabaseService(settings.DATABASE_URL)
    llm_service = LLMService()

    logging.info("--- PHASE 1: FETCHING AND STORING RAW REVIEWS ---")
    LOCAL_JSON_PATH = "C:/Users/sude/Desktop/Staj/Pull1/STAJ/workflow_code/product_8118521_reviews.json"
    fetched_reviews = fetch_reviews_from_local(LOCAL_JSON_PATH)

    if fetched_reviews:
        db_service.insert_raw_reviews(fetched_reviews)

    logging.info("--- PHASE 2: PROCESSING PENDING REVIEWS ---")
    pending_reviews = db_service.get_pending_reviews()

    total = len(pending_reviews)
    success = 0
    failed = 0

    if not pending_reviews:
        logging.info("No pending reviews to process. Workflow finished.")
        return

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

    logging.info("----- ANALYSIS SUMMARY -----")
    logging.info(f"Total pending reviews fetched: {total}")
    logging.info(f"Successfully analyzed and saved: {success}")
    logging.info(f"Failed to analyze: {failed}")


if __name__ == "__main__":
    main_workflow()
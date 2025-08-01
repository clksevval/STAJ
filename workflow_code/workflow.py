import asyncio
import platform 
import httpx
import psycopg
import logging
import uuid
import json  
from typing import List, Dict, Any

from main import LLMService, ReviewFields
from app.core.config import settings
from psycopg_pool import AsyncConnectionPool

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Bu kod, sadece işletim sistemi Windows ise çalışır ve uyumluluk sorununu çözer.
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# --- VERİTABANI YÖNETİMİ ---
class DatabaseService:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: AsyncConnectionPool | None = None

    async def connect(self):
        self.pool = AsyncConnectionPool(conninfo=self.dsn)
        logging.info("Database connection pool created successfully.")

    async def close(self):
        if self.pool:
            await self.pool.close()
            logging.info("Database connection pool closed.")

    async def insert_raw_reviews(self, reviews: list[dict]):
        if not self.pool:
            raise ConnectionError("Database pool is not initialized.")
        
        async with self.pool.connection() as aconn:
            async with aconn.cursor() as acur:
                try:
                    await acur.executemany(
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
                    logging.info(f"Attempted to insert {len(reviews)} reviews. {acur.rowcount} new reviews were inserted.")
                except Exception as e:
                    logging.error(f"Failed to bulk insert raw reviews: {e}")

    async def get_pending_reviews(self, limit: int = 10) -> list[dict]:
        if not self.pool:
            raise ConnectionError("Database pool is not initialized.")

        query = """
            SELECT rr.id, rr.comment
            FROM raw_reviews rr
            LEFT JOIN review_analysis ra ON rr.id = ra.review_id
            WHERE ra.review_id IS NULL
            ORDER BY rr.created_at
            LIMIT %s;
        """
        async with self.pool.connection() as aconn:
            async with aconn.cursor(row_factory=psycopg.rows.dict_row) as acur:
                await acur.execute(query, (limit,))
                reviews = await acur.fetchall()
                logging.info(f"Fetched {len(reviews)} pending reviews from the database.")
                return reviews

# workflow.py dosyasının içindeki bu fonksiyonu güncelleyin

    async def save_analysis_result(self, review_id: uuid.UUID, analysis_data: ReviewFields):
        """LLM'den gelen analiz sonucunu 'review_analysis' tablosuna kaydeder."""
        if not self.pool:
            raise ConnectionError("Database pool is not initialized. Call connect() first.")

        query = """
            INSERT INTO review_analysis (review_id, sentiment, sentiment_confidence, pros, 
                                       cons, complaints, suggestions, expectations, feature_categories)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        data = analysis_data.model_dump()
        async with self.pool.connection() as aconn:
            async with aconn.cursor() as acur:
                try:
                    # <--- DÜZELTME: Listeleri json.dumps() ile JSON string'ine çeviriyoruz --->
                    await acur.execute(query, (
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

async def fetch_reviews_from_source(api_url: str) -> List[Dict[str, Any]]:
    logging.info(f"Fetching reviews from {api_url}...")
    try:
        # --- API OLMADIĞI İÇİN ÖRNEK VERİ ---
        mock_reviews = [
            {
                "id": uuid.uuid4(), "product_id": "SND-001", "rating_code": 5, "title": "Montajı Çok Kolay!", 
                "comment": "Bu sandalyenin montajı çok kolaydı, 15 dakikada kurdum. Rengi de fotoğraftakinden daha güzel.",
                "language_code": "tr", "country_code": "TR", "author_username": "sevval_k",
                "publisher_date": "2025-05-20T10:00:00Z", "attributes": json.dumps({"color": "grey", "verified_purchase": True})
            },
            {
                "id": uuid.uuid4(), "product_id": "SND-001", "rating_code": 3, "title": "Rahat ama gıcırdıyor", 
                "comment": "Sandalye rahat ama gıcırdıyor. Ofis için aldım ama sesten rahatsız oldum. Belki yağlamak gerekir.",
                "language_code": "tr", "country_code": "TR", "author_username": "ahmet_y",
                "publisher_date": "2025-05-21T14:30:00Z", "attributes": json.dumps({"color": "black", "verified_purchase": True})
            }
        ]
        logging.info(f"Generated {len(mock_reviews)} mock reviews for demonstration.")
        return mock_reviews
    except Exception as e:
        logging.error(f"An error occurred during mock data generation: {e}")
        return []

async def main_workflow():
    db_service = DatabaseService(settings.DATABASE_URL)
    await db_service.connect()
    llm_service = LLMService()

    try:
        logging.info("--- PHASE 1: FETCHING AND STORING RAW REVIEWS ---")
        REVIEWS_API_URL = "https://api.example.com/product/SND-001/reviews"
        fetched_reviews = await fetch_reviews_from_source(REVIEWS_API_URL)
        
        if fetched_reviews:
            await db_service.insert_raw_reviews(fetched_reviews)

        logging.info("--- PHASE 2: PROCESSING PENDING REVIEWS ---")
        pending_reviews = await db_service.get_pending_reviews(limit=20)

        if not pending_reviews:
            logging.info("No pending reviews to process. Workflow finished.")
            return

        for review in pending_reviews:
            review_id = review['id']
            comment_text = review['comment']
            
            try:
                analysis_result = llm_service.analyse_review(comment_text)
                
                # <--- DÜZELTME 2: Analiz sonucunun 'None' olup olmadığını kontrol et.
                if analysis_result:
                    await db_service.save_analysis_result(review_id, analysis_result)
                else:
                    logging.warning(f"Analysis for review_id {review_id} returned None. Skipping save.")
            
            except Exception as e:
                logging.error(f"A critical error occurred while processing review_id {review_id}: {e}")

    finally:
        await db_service.close()

if __name__ == "__main__":
    asyncio.run(main_workflow())

# api_server.py

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json

# "kullanici_adiniz", "sifreniz", "veritabani_adiniz" kısımlarını değiştirin.
DATABASE_URL = "postgresql://postgres:1857@localhost:5432/decathlon_db"

# FastAPI uygulamasını başlatıyoruz. Artık bu bizim sunucumuz.
app = FastAPI()

# ==============================================================================
# CORS İzinleri: Bu bölüm çok önemlidir.
# React (localhost:3000) ile Python (localhost:8000) farklı yerlerde çalıştığı için,
# Python sunucusunun React'ten gelen isteklere "Sana güveniyorum, cevap verebilirim"
# demesi gerekir. Bu kod o izni verir.
# ==============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Veritabanına bağlanmak için bir yardımcı fonksiyon
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.OperationalError:
        raise HTTPException(status_code=500, detail="Veritabanı sunucusuna bağlanılamıyor.")

# ==============================================================================
# API URL'LERİ (ENDPOINT)
# React uygulamamızın veri istemek için ziyaret edeceği adresleri burada tanımlıyoruz.
# ==============================================================================

# 1. Ürün listesini getiren URL
@app.get("/products")
def get_all_products():
    """
    React'teki ürün seçme menüsünü (dropdown) doldurmak için kullanılır.
    Veritabanından tüm ürünlerin ID'lerini ve varsa isimlerini çeker.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Not: 'product_name' diye bir kolonunuz yoksa, sorgudan silebilirsiniz.
            # React tarafı bu durumu kontrol edecek şekilde ayarlandı.
            cur.execute("SELECT product_id FROM analysis_summary ORDER BY product_id")
            products = cur.fetchall()
            return products
    finally:
        conn.close()

# 2. Belirli bir ürünün analizini getiren URL
@app.get("/analysis/{product_id}")
def get_analysis_summary(product_id: str):
    """React'ten gelen ürün ID'sine göre ilgili ürünün tüm analiz özetini getirir."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM analysis_summary WHERE product_id = %s", (product_id,))
            summary = cur.fetchone()
            if not summary:
                raise HTTPException(status_code=404, detail="Bu ID ile bir ürün bulunamadı.")
            
            # Veritabanındaki JSONB veya TEXT tipindeki kolonları otomatik olarak
            # Python dictionary nesnesine çevirmek için kontrol.
            # RealDictCursor genelde bunu halleder, bu bir ek güvencedir.
            parsed_summary = dict(summary)
            for key, value in parsed_summary.items():
                if isinstance(value, str) and value.startswith(('[', '{')):
                    try:
                        parsed_summary[key] = json.loads(value)
                    except json.JSONDecodeError:
                        pass # Eğer JSON değilse, olduğu gibi bırak
            
            return parsed_summary
    finally:
        conn.close()
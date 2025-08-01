# main.py

import logging
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bu liste, LLM'in seçim yapabileceği kategorileri tanımlar ve sabittir.
FEATURE_CATEGORIES = [
    "ease of use", "material quality", "pricing", "durability",
    "delivery speed", "packaging quality", "design aesthetics",
    "ease of setup", "seller responsiveness", "size compatibility",
    "product match with listing", "meeting expectations", "eco-friendliness",
    "availability", "noise level", "battery life", "discount",
    "payment options", "return process", "spare parts", "warranty",
    "technical support", "brand trust", "stock issue"
]

# --------------------------------------------------------------------------
# GÜNCELLENMİŞ BÖLÜM: Veritabanı Şemasıyla Uyumlu Pydantic Modeli
# Bu model, 'review_analysis' tablosunun yapısıyla birebir eşleşir.
# --------------------------------------------------------------------------
class ReviewFields(BaseModel):
    """LLM'den dönecek yapılandırılmış veriyi tanımlar."""
    sentiment: str = Field(
        ...,
        description="Genel ton: positive, negative, or neutral"
    )
    sentiment_confidence: float = Field(
        ...,
        description="Duygu analizi tahmini için 0.0 ile 1.0 arasında bir güven skoru"
    )
    pros: List[str] = Field(
        ...,
        description="Olumlu yönler (her etiket en fazla 5 kelime)"
    )
    cons: List[str] = Field(
        ...,
        description="Olumsuz yönler (her etiket en fazla 5 kelime)"
    )
    complaints: List[str] = Field(
        ...,
        description="Üretici tarafından iyileştirilmesi gereken somut sorunlar"
    )
    suggestions: List[str] = Field(
        ...,
        description="Gelecekteki alıcılar için tavsiyeler"
    )
    expectations: List[str] = Field(
        ...,
        description="Kullanıcının beklediği ancak alamadığı özellikler"
    )
    feature_categories: List[str] = Field(
        ...,
        description=f"İlgili ürün özellikleri. YALNIZCA şu listeden seçilmelidir: {', '.join(FEATURE_CATEGORIES)}"
    )


# --------------------------------------------------------------------------
# GÜNCELLENMİŞ BÖLÜM: Prompt, 'sentiment_confidence' istemek üzere güncellendi.
# --------------------------------------------------------------------------
PROMPT_TEMPLATE = """\
Analyse the customer review below and output one standalone JSON object.
Provide a sentiment confidence score between 0.0 and 1.0 for the sentiment prediction.
For "feature_categories", choose ONLY from the predefined list.

Predefined Feature List: {feature_list}

Customer Review:
>>>
{review}
>>>
"""


class LLMService:
    """
    LLM ile etkileşimi yöneten ve yorumları analiz eden servis.
    """
    def __init__(self):
        """LangChain bileşenlerini ve LLM bağlantısını başlatır."""
        # Ayarların app/core/config.py dosyasından geldiğini varsayıyoruz.
        from app.core.config import settings
        
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.LLM_MODEL,
            temperature=0,
            format="json"  # Modeli JSON çıktısı vermeye zorlar
        )
        
        self.prompt = ChatPromptTemplate.from_template(
            PROMPT_TEMPLATE
        ).partial(feature_list=", ".join(FEATURE_CATEGORIES))
        
        # Zincir, tek bir 'ReviewFields' nesnesi döndürecek şekilde ayarlandı.
        self.chain = self.prompt | self.llm.with_structured_output(ReviewFields)
        
        logger.info(f"LLMService initialized with model: {settings.LLM_MODEL}")
    
    def analyse_review(self, review_text: str) -> ReviewFields | None:
        """
        Tek bir yorum metnini analiz eder ve yapılandırılmış bir ReviewFields nesnesi döndürür.
        Hata durumunda None döndürür.
        """
        try:
            logger.info(f"Analyzing review: '{review_text[:60]}...'")
            return self.chain.invoke({"review": review_text})
        except Exception as e:
            logger.error(f"LLM analysis failed for review: '{review_text[:60]}...'. Error: {e}")
            return None


# --------------------------------------------------------------------------
# Bu dosyanın tek başına test edilmesini sağlayan bölüm.
# `python main.py` komutuyla çalıştırıldığında bu blok çalışır.
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    print("--- LLMService Standalone Test ---")
    
    # Test için LLM servisini başlat
    llm_service = LLMService()
    
    # Test edilecek örnek bir yorum
    sample_review = "The chair is comfortable and looks great, but it started to squeak after a week. The price was reasonable though. I'd suggest applying some WD-40 upon assembly."
    
    # Yorumu analiz et
    analysis_result = llm_service.analyse_review(sample_review)
    
    # Sonucu ekrana yazdır
    if analysis_result:
        print("\n--- Analysis Result ---")
        # Pydantic modelini JSON formatında daha okunaklı yazdır
        print(analysis_result.model_dump_json(indent=2))
    else:
        print("\n--- Analysis Failed ---")
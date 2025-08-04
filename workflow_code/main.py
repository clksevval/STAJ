# main.py

import logging
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Yorumda geçen ürün özelliklerini sınırlı bir listeden seçmek için sabit liste
FEATURE_CATEGORIES = [
    "ease of use", "material quality", "pricing", "durability",
    "delivery speed", "packaging quality", "design aesthetics",
    "ease of setup", "seller responsiveness", "size compatibility",
    "product match with listing", "meeting expectations", "eco-friendliness",
    "availability", "noise level", "battery life", "discount",
    "payment options", "return process", "spare parts", "warranty",
    "technical support", "brand trust", "stock issue"
]

# Veritabanı Şemasıyla Uyumlu Pydantic Modeli
# 'review_analysis' tablosunun yapısında
class ReviewFields(BaseModel):
    """LLM'den dönecek yapılandırılmış veriyi tanımlar."""
    sentiment: str = Field(
        ...,
        description="Genel ton: positive, negative, or neutral"
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



PROMPT_TEMPLATE = """\
Analyse the customer review below and output a VALID JSON object.

For "feature_categories", choose ONLY from the predefined list.

Predefined Feature List: {feature_list}

Customer Review:
>>>>
{review}
>>>>

IMPORTANT: You must respond with a VALID JSON object in exactly this format:
{{
  "sentiment": "positive|negative|neutral",
  "pros": ["item1", "item2"],
  "cons": ["item1", "item2"],
  "complaints": ["item1", "item2"],
  "suggestions": ["item1", "item2"],
  "expectations": ["item1", "item2"],
  "feature_categories": ["category1", "category2"]
}}

Do not include any text before or after the JSON object. Only return the JSON.
"""


# LLM ile yorum analizi yapan servis
class LLMService:
    def __init__(self):
        # Config dosyasından ayarları çekiyoruz
        from app.core.config import settings

        # Ollama üzerinden model bağlantısı kuruluyor
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,  # örn. http://localhost:11434
            model=settings.LLM_MODEL,           # örn. qwen3:14b
            temperature=0.7,                      # deterministik çıktı için
            format="json"                       # burası sanırım sorun çıkarıyor
        )

        # Prompt sabiti, özellik listesiyle birlikte kullanıma hazırlanıyor
        self.prompt = ChatPromptTemplate.from_template(
            PROMPT_TEMPLATE
        ).partial(feature_list=", ".join(FEATURE_CATEGORIES))

        # LangChain zinciri tanımlanıyor: prompt → LLM → yapılandırılmış çıktı
        self.chain = self.prompt | self.llm.with_structured_output(ReviewFields)

        logger.info(f"LLMService initialized with model: {settings.LLM_MODEL}")

    def analyse_review(self, review_text: str) -> ReviewFields | None:
        """
        Verilen bir müşteri yorumunu analiz eder.
        Başarılıysa `ReviewFields` nesnesi döner, hata olursa `None`.
        """
        try:
            logger.info(f"Analyzing review: '{review_text[:60]}...'")
            
            # Prompt'u hazırla
            prompt_messages = self.prompt.format_messages(review=review_text)
            logger.info(f"DEBUG - Prompt messages: {prompt_messages}")
            
            # LLM'den ham yanıtı al
            raw_response = self.llm.invoke(prompt_messages)
            logger.info(f"DEBUG - Raw LLM response: {raw_response}")
            
            # Structured output ile parse et
            result = self.chain.invoke({"review": review_text})
            logger.info(f"DEBUG - Parsed result: {result}")
            
            return result
        except Exception as e:
            logger.error(f"LLM analysis failed for review: '{review_text[:60]}...'. Error: {e}")
            return None


# Test
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
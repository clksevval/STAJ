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
You are a product review analyst AI. Analyze the following customer reviews.
Provide the output in English only.

For each review, return one JSON object with the following fields. Be precise and consistent:
1. sentiment: "positive", "neutral", or "negative"
2. sentiment_confidence: A float between 0 and 1 indicating your confidence in the sentiment classification. 1 means very confident, 0 means not confident at all
3. pros: Positive aspects of the product, based on the user’s statements - max 5 words long for each tag
4. cons: Negative aspects of the product (but not suggestions or complaints) - max 5 words long for each tag
5. complaints: Specific problems that should be improved by the producer (e.g., “Brakes should be tighter”, “Saddle should be softer”)
6. suggestions: Contextual advice or recommendations for potential customers, such as how or by whom the product is best used
7. expectations: Features or qualities the user expected but the product did not provide
8. feature_categories: choose only from the predefined list below that describe relevant product aspects

IMPORTANT: feature_categories MUST be selected only from the predefined list below:
Predefined Feature List: {feature_list}

Return one JSON object per review, in a Python list format.

]
Customer Reviews:
{review}
IMPORTANT: Respond in English only, regardless of the review's original language.

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


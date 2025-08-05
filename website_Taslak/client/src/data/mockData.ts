export interface AnalysisSummary {
  product_id: string;
  total_reviews: number;
  sentiment_distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
  top_complaints: string[];
  top_suggestions: string[];
  top_pros: string[];
  top_cons: string[];
  feature_categories: {
    [key: string]: number;
  };
  expectations_from_producer: string[];
  last_updated: string;
}

export const mockAnalysisData: AnalysisSummary = {
  product_id: "DEC001",
  total_reviews: 1247,
  sentiment_distribution: {
    positive: 65,
    negative: 20,
    neutral: 15
  },
  top_complaints: [
    "Beden boyutu küçük geliyor",
    "İlk kullanımda zincir sesi yapıyor",
    "Kışın lastik kayıyor",
    "Sele çok sert",
    "Fren sistemi hassas değil",
    "Vites geçişleri sert",
    "Ağırlık fazla",
    "Pedal sistemi gürültülü",
    "Gidon ayarı zor",
    "Farlar yetersiz"
  ],
  top_suggestions: [
    "Bir beden büyük almanızı öneririm",
    "Şehir içi kullanım için daha uygun",
    "İlk kullanımda zinciri kontrol edin",
    "Kışın kullanacaksanız lastik değiştirin",
    "Sele yastığı ekleyin",
    "Fren ayarını yaptırın",
    "Vites bakımını düzenli yaptırın",
    "Hafif modelleri tercih edin",
    "Pedal yağlaması yaptırın",
    "Gidon yüksekliğini ayarlayın"
  ],
  top_pros: [
    "Dayanıklı ve sağlam yapı",
    "Uygun fiyat",
    "Kolay kullanım",
    "Güvenilir marka",
    "Geniş servis ağı",
    "Kaliteli malzeme",
    "Ergonomik tasarım",
    "Çok amaçlı kullanım",
    "Kolay bakım",
    "Uzun ömürlü"
  ],
  top_cons: [
    "Ağır olması",
    "Beden seçenekleri sınırlı",
    "Renk seçenekleri az",
    "Ek aksesuar maliyeti",
    "Montaj zorluğu",
    "Depolama alanı gerektirir",
    "Taşıma zorluğu",
    "Park yeri problemi",
    "Hırsızlık riski",
    "Hava koşullarına bağımlılık"
  ],
  feature_categories: {
    "Dayanıklılık": 85,
    "Performans": 72,
    "Konfor": 68,
    "Güvenlik": 75,
    "Tasarım": 70,
    "Kullanım Kolaylığı": 78,
    "Fiyat/Performans": 82,
    "Servis": 65,
    "Aksesuar": 60,
    "Teknoloji": 55
  },
  expectations_from_producer: [
    "Daha hafif modeller geliştirilsin",
    "Beden seçenekleri artırılsın",
    "Renk çeşitliliği sağlansın",
    "Fiyatlar daha uygun olsun",
    "Servis kalitesi artırılsın",
    "Garanti süresi uzatılsın",
    "Yedek parça bulunabilirliği artırılsın",
    "Montaj kolaylığı sağlansın",
    "Aksesuar çeşitliliği artırılsın",
    "Teknoloji entegrasyonu geliştirilsin"
  ],
  last_updated: "2024-01-15T10:30:00Z"
}; 
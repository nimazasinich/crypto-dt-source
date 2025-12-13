#!/usr/bin/env python3
"""
Advanced Model Manager
مدیریت پیشرفته مدل‌های AI با قابلیت filtering، ranking، و recommendation
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class ModelCategory(Enum):
    """دسته‌بندی مدل‌ها"""
    SENTIMENT = "sentiment"
    GENERATION = "generation"
    TRADING = "trading"
    SUMMARIZATION = "summarization"
    NER = "ner"
    QA = "question_answering"
    CLASSIFICATION = "classification"
    EMBEDDING = "embedding"
    TRANSLATION = "translation"
    PRICE_PREDICTION = "price_prediction"


class ModelSize(Enum):
    """اندازه مدل‌ها"""
    TINY = "tiny"      # <100 MB
    SMALL = "small"    # 100-500 MB
    MEDIUM = "medium"  # 500MB-1GB
    LARGE = "large"    # 1-3GB
    XLARGE = "xlarge"  # >3GB


@dataclass
class ModelInfo:
    """اطلاعات کامل یک مدل AI"""
    id: str
    hf_id: str
    name: str
    category: str  # ModelCategory value
    size: str      # ModelSize value
    size_mb: int
    description: str
    use_cases: List[str]
    languages: List[str]
    free: bool
    requires_auth: bool
    performance_score: float  # 0-1
    popularity_score: float   # 0-1
    tags: List[str]
    api_compatible: bool = True
    downloadable: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dict"""
        return asdict(self)


class AdvancedModelManager:
    """
    مدیر پیشرفته مدل‌های AI
    
    قابلیت‌ها:
    - Filtering بر اساس category, size, language
    - Ranking بر اساس performance
    - Recommendation بر اساس use case
    - Search در تمام فیلدها
    - Stats و Analytics
    """
    
    def __init__(self):
        self.models = self._load_model_catalog()
        logger.info(f"Loaded {len(self.models)} models into catalog")
    
    def _load_model_catalog(self) -> Dict[str, ModelInfo]:
        """بارگذاری کاتالوگ کامل مدل‌ها"""
        return {
            # ===== SENTIMENT MODELS =====
            
            "cryptobert": ModelInfo(
                id="cryptobert",
                hf_id="kk08/CryptoBERT",
                name="CryptoBERT",
                category=ModelCategory.SENTIMENT.value,
                size=ModelSize.SMALL.value,
                size_mb=420,
                description="Binary sentiment analysis optimized for crypto texts",
                use_cases=["social_media", "news", "tweets", "reddit"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.85,
                popularity_score=0.90,
                tags=["crypto", "sentiment", "bert", "binary"],
                api_compatible=True,
                downloadable=True
            ),
            
            "elkulako_cryptobert": ModelInfo(
                id="elkulako_cryptobert",
                hf_id="ElKulako/cryptobert",
                name="ElKulako CryptoBERT",
                category=ModelCategory.SENTIMENT.value,
                size=ModelSize.SMALL.value,
                size_mb=450,
                description="3-class crypto sentiment (bullish/neutral/bearish)",
                use_cases=["twitter", "reddit", "social", "forums"],
                languages=["en"],
                free=True,
                requires_auth=True,
                performance_score=0.88,
                popularity_score=0.85,
                tags=["crypto", "social", "sentiment", "3-class"],
                api_compatible=True,
                downloadable=True
            ),
            
            "finbert": ModelInfo(
                id="finbert",
                hf_id="ProsusAI/finbert",
                name="FinBERT",
                category=ModelCategory.SENTIMENT.value,
                size=ModelSize.SMALL.value,
                size_mb=440,
                description="Financial sentiment analysis (positive/negative/neutral)",
                use_cases=["news", "articles", "reports", "earnings"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.90,
                popularity_score=0.95,
                tags=["finance", "sentiment", "bert", "financial"],
                api_compatible=True,
                downloadable=True
            ),
            
            "finbert_tone": ModelInfo(
                id="finbert_tone",
                hf_id="yiyanghkust/finbert-tone",
                name="FinBERT Tone",
                category=ModelCategory.SENTIMENT.value,
                size=ModelSize.SMALL.value,
                size_mb=440,
                description="Financial tone analysis for earnings calls and reports",
                use_cases=["earnings_calls", "reports", "financial_documents"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.87,
                popularity_score=0.80,
                tags=["finance", "tone", "bert"],
                api_compatible=True,
                downloadable=True
            ),
            
            "distilroberta_financial": ModelInfo(
                id="distilroberta_financial",
                hf_id="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
                name="DistilRoBERTa Financial",
                category=ModelCategory.SENTIMENT.value,
                size=ModelSize.SMALL.value,
                size_mb=330,
                description="Fast financial sentiment analysis with DistilRoBERTa",
                use_cases=["news", "real_time", "streaming"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.83,
                popularity_score=0.75,
                tags=["finance", "sentiment", "distil", "fast"],
                api_compatible=True,
                downloadable=True
            ),
            
            "fintwit_bert": ModelInfo(
                id="fintwit_bert",
                hf_id="StephanAkkerman/FinTwitBERT-sentiment",
                name="FinTwitBERT",
                category=ModelCategory.SENTIMENT.value,
                size=ModelSize.SMALL.value,
                size_mb=440,
                description="Financial Twitter sentiment analysis",
                use_cases=["twitter", "social", "fintwit"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.86,
                popularity_score=0.82,
                tags=["finance", "twitter", "sentiment"],
                api_compatible=True,
                downloadable=True
            ),
            
            "twitter_roberta": ModelInfo(
                id="twitter_roberta",
                hf_id="cardiffnlp/twitter-roberta-base-sentiment-latest",
                name="Twitter RoBERTa",
                category=ModelCategory.SENTIMENT.value,
                size=ModelSize.MEDIUM.value,
                size_mb=500,
                description="State-of-the-art Twitter sentiment analysis",
                use_cases=["twitter", "social_media", "tweets"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.89,
                popularity_score=0.92,
                tags=["twitter", "sentiment", "roberta", "social"],
                api_compatible=True,
                downloadable=True
            ),
            
            "xlm_roberta_sentiment": ModelInfo(
                id="xlm_roberta_sentiment",
                hf_id="cardiffnlp/twitter-xlm-roberta-base-sentiment",
                name="XLM-RoBERTa Sentiment",
                category=ModelCategory.SENTIMENT.value,
                size=ModelSize.MEDIUM.value,
                size_mb=1100,
                description="Multilingual sentiment (100+ languages)",
                use_cases=["global", "multilingual", "international"],
                languages=["multi"],
                free=True,
                requires_auth=False,
                performance_score=0.87,
                popularity_score=0.88,
                tags=["multilingual", "sentiment", "roberta", "global"],
                api_compatible=True,
                downloadable=True
            ),
            
            "bertweet_sentiment": ModelInfo(
                id="bertweet_sentiment",
                hf_id="finiteautomata/bertweet-base-sentiment-analysis",
                name="BERTweet Sentiment",
                category=ModelCategory.SENTIMENT.value,
                size=ModelSize.MEDIUM.value,
                size_mb=540,
                description="BERT trained specifically on tweets",
                use_cases=["twitter", "social", "monitoring"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.85,
                popularity_score=0.80,
                tags=["twitter", "bert", "sentiment"],
                api_compatible=True,
                downloadable=True
            ),
            
            "crypto_news_bert": ModelInfo(
                id="crypto_news_bert",
                hf_id="mathugo/crypto_news_bert",
                name="Crypto News BERT",
                category=ModelCategory.SENTIMENT.value,
                size=ModelSize.SMALL.value,
                size_mb=420,
                description="BERT fine-tuned on crypto news articles",
                use_cases=["news", "articles", "crypto_media"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.84,
                popularity_score=0.70,
                tags=["crypto", "news", "bert"],
                api_compatible=True,
                downloadable=True
            ),
            
            # ===== GENERATION MODELS =====
            
            "crypto_gpt_o3": ModelInfo(
                id="crypto_gpt_o3",
                hf_id="OpenC/crypto-gpt-o3-mini",
                name="Crypto GPT-O3 Mini",
                category=ModelCategory.GENERATION.value,
                size=ModelSize.MEDIUM.value,
                size_mb=850,
                description="Crypto/DeFi text generation model",
                use_cases=["analysis", "reports", "content", "explanation"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.80,
                popularity_score=0.70,
                tags=["crypto", "generation", "gpt", "defi"],
                api_compatible=True,
                downloadable=True
            ),
            
            "fingpt": ModelInfo(
                id="fingpt",
                hf_id="oliverwang15/FinGPT",
                name="FinGPT",
                category=ModelCategory.GENERATION.value,
                size=ModelSize.LARGE.value,
                size_mb=1500,
                description="Financial text generation and analysis",
                use_cases=["reports", "analysis", "financial_content"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.82,
                popularity_score=0.75,
                tags=["finance", "generation", "gpt"],
                api_compatible=True,
                downloadable=True
            ),
            
            # ===== TRADING MODELS =====
            
            "crypto_trader_lm": ModelInfo(
                id="crypto_trader_lm",
                hf_id="agarkovv/CryptoTrader-LM",
                name="CryptoTrader LM",
                category=ModelCategory.TRADING.value,
                size=ModelSize.SMALL.value,
                size_mb=450,
                description="BTC/ETH trading signals (buy/sell/hold)",
                use_cases=["trading", "signals", "predictions", "analysis"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.75,
                popularity_score=0.65,
                tags=["trading", "signals", "crypto", "predictions"],
                api_compatible=True,
                downloadable=True
            ),
            
            "crypto_price_predictor": ModelInfo(
                id="crypto_price_predictor",
                hf_id="mrm8488/bert-mini-finetuned-crypto-price-prediction",
                name="Crypto Price Predictor",
                category=ModelCategory.PRICE_PREDICTION.value,
                size=ModelSize.TINY.value,
                size_mb=60,
                description="Price trend prediction for cryptocurrencies",
                use_cases=["prediction", "forecasting", "trends"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.70,
                popularity_score=0.60,
                tags=["prediction", "price", "trends"],
                api_compatible=True,
                downloadable=True
            ),
            
            # ===== SUMMARIZATION MODELS =====
            
            "crypto_news_summarizer": ModelInfo(
                id="crypto_news_summarizer",
                hf_id="FurkanGozukara/Crypto-Financial-News-Summarizer",
                name="Crypto News Summarizer",
                category=ModelCategory.SUMMARIZATION.value,
                size=ModelSize.MEDIUM.value,
                size_mb=1200,
                description="Summarize crypto and financial news articles",
                use_cases=["news", "digest", "reports", "articles"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.82,
                popularity_score=0.75,
                tags=["summarization", "news", "crypto"],
                api_compatible=True,
                downloadable=True
            ),
            
            "financial_summarizer_pegasus": ModelInfo(
                id="financial_summarizer_pegasus",
                hf_id="human-centered-summarization/financial-summarization-pegasus",
                name="Financial Summarizer (PEGASUS)",
                category=ModelCategory.SUMMARIZATION.value,
                size=ModelSize.LARGE.value,
                size_mb=2300,
                description="High-quality financial document summarization",
                use_cases=["reports", "documents", "earnings", "filings"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.88,
                popularity_score=0.80,
                tags=["summarization", "finance", "pegasus"],
                api_compatible=True,
                downloadable=True
            ),
            
            "bart_large_cnn": ModelInfo(
                id="bart_large_cnn",
                hf_id="facebook/bart-large-cnn",
                name="BART Large CNN",
                category=ModelCategory.SUMMARIZATION.value,
                size=ModelSize.LARGE.value,
                size_mb=1600,
                description="General-purpose news summarization",
                use_cases=["news", "articles", "blogs", "content"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.90,
                popularity_score=0.95,
                tags=["summarization", "bart", "news"],
                api_compatible=True,
                downloadable=True
            ),
            
            "t5_base_summarization": ModelInfo(
                id="t5_base_summarization",
                hf_id="t5-base",
                name="T5 Base",
                category=ModelCategory.SUMMARIZATION.value,
                size=ModelSize.MEDIUM.value,
                size_mb=850,
                description="Flexible text-to-text model for summarization",
                use_cases=["general", "flexible", "any_text"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.85,
                popularity_score=0.90,
                tags=["summarization", "t5", "flexible"],
                api_compatible=True,
                downloadable=True
            ),
            
            # ===== NER MODELS =====
            
            "bert_base_ner": ModelInfo(
                id="bert_base_ner",
                hf_id="dslim/bert-base-NER",
                name="BERT Base NER",
                category=ModelCategory.NER.value,
                size=ModelSize.SMALL.value,
                size_mb=420,
                description="Named Entity Recognition for financial entities",
                use_cases=["entities", "extraction", "companies", "tickers"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.88,
                popularity_score=0.85,
                tags=["ner", "entities", "bert"],
                api_compatible=True,
                downloadable=True
            ),
            
            # ===== Q&A MODELS =====
            
            "roberta_squad2": ModelInfo(
                id="roberta_squad2",
                hf_id="deepset/roberta-base-squad2",
                name="RoBERTa SQuAD2",
                category=ModelCategory.QA.value,
                size=ModelSize.MEDIUM.value,
                size_mb=500,
                description="Question answering for any text",
                use_cases=["qa", "chatbot", "faq", "retrieval"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.90,
                popularity_score=0.92,
                tags=["qa", "roberta", "squad"],
                api_compatible=True,
                downloadable=True
            ),
            
            "bert_squad2": ModelInfo(
                id="bert_squad2",
                hf_id="deepset/bert-base-cased-squad2",
                name="BERT SQuAD2",
                category=ModelCategory.QA.value,
                size=ModelSize.SMALL.value,
                size_mb=420,
                description="Financial FAQ and Q&A",
                use_cases=["faq", "support", "chatbot"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.87,
                popularity_score=0.88,
                tags=["qa", "bert", "squad"],
                api_compatible=True,
                downloadable=True
            ),
            
            # ===== EMBEDDING MODELS =====
            
            "sentence_bert_mpnet": ModelInfo(
                id="sentence_bert_mpnet",
                hf_id="sentence-transformers/all-mpnet-base-v2",
                name="Sentence-BERT MPNet",
                category=ModelCategory.EMBEDDING.value,
                size=ModelSize.SMALL.value,
                size_mb=420,
                description="High-quality sentence embeddings",
                use_cases=["search", "similarity", "clustering", "retrieval"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.92,
                popularity_score=0.95,
                tags=["embeddings", "sentence", "bert"],
                api_compatible=True,
                downloadable=True
            ),
            
            "e5_large_v2": ModelInfo(
                id="e5_large_v2",
                hf_id="intfloat/e5-large-v2",
                name="E5 Large V2",
                category=ModelCategory.EMBEDDING.value,
                size=ModelSize.MEDIUM.value,
                size_mb=1300,
                description="State-of-the-art embeddings",
                use_cases=["search", "retrieval", "rag", "semantic"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.94,
                popularity_score=0.90,
                tags=["embeddings", "e5", "search"],
                api_compatible=True,
                downloadable=True
            ),
            
            # ===== CLASSIFICATION MODELS =====
            
            "bart_mnli": ModelInfo(
                id="bart_mnli",
                hf_id="facebook/bart-large-mnli",
                name="BART MNLI",
                category=ModelCategory.CLASSIFICATION.value,
                size=ModelSize.LARGE.value,
                size_mb=1600,
                description="Zero-shot topic classification",
                use_cases=["classification", "topics", "zero_shot"],
                languages=["en"],
                free=True,
                requires_auth=False,
                performance_score=0.89,
                popularity_score=0.92,
                tags=["classification", "bart", "zero_shot"],
                api_compatible=True,
                downloadable=True
            ),
        }
    
    # ===== QUERY METHODS =====
    
    def get_all_models(self) -> List[ModelInfo]:
        """دریافت تمام مدل‌ها"""
        return list(self.models.values())
    
    def get_model_by_id(self, model_id: str) -> Optional[ModelInfo]:
        """دریافت مدل بر اساس ID"""
        return self.models.get(model_id)
    
    def filter_models(
        self,
        category: Optional[str] = None,
        size: Optional[str] = None,
        max_size_mb: Optional[int] = None,
        language: Optional[str] = None,
        free_only: bool = True,
        no_auth: bool = True,
        min_performance: float = 0.0,
        api_compatible: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> List[ModelInfo]:
        """
        فیلتر کردن مدل‌ها بر اساس معیارهای مختلف
        """
        filtered = self.get_all_models()
        
        if category:
            filtered = [m for m in filtered if m.category == category]
        
        if size:
            filtered = [m for m in filtered if m.size == size]
        
        if max_size_mb:
            filtered = [m for m in filtered if m.size_mb <= max_size_mb]
        
        if language:
            filtered = [
                m for m in filtered 
                if language in m.languages or "multi" in m.languages
            ]
        
        if free_only:
            filtered = [m for m in filtered if m.free]
        
        if no_auth:
            filtered = [m for m in filtered if not m.requires_auth]
        
        if min_performance > 0:
            filtered = [m for m in filtered if m.performance_score >= min_performance]
        
        if api_compatible is not None:
            filtered = [m for m in filtered if m.api_compatible == api_compatible]
        
        if tags:
            filtered = [
                m for m in filtered 
                if any(tag in m.tags for tag in tags)
            ]
        
        return filtered
    
    def get_best_models(
        self,
        category: str,
        top_n: int = 3,
        max_size_mb: Optional[int] = None
    ) -> List[ModelInfo]:
        """
        دریافت بهترین مدل‌ها بر اساس performance
        """
        filtered = self.filter_models(
            category=category,
            max_size_mb=max_size_mb
        )
        
        # مرتب‌سازی بر اساس performance
        sorted_models = sorted(
            filtered,
            key=lambda m: (m.performance_score, m.popularity_score),
            reverse=True
        )
        
        return sorted_models[:top_n]
    
    def recommend_models(
        self,
        use_case: str,
        max_models: int = 5,
        max_size_mb: Optional[int] = None
    ) -> List[ModelInfo]:
        """
        پیشنهاد مدل‌ها بر اساس use case
        """
        all_models = self.get_all_models()
        
        # فیلتر بر اساس use case
        relevant = [
            m for m in all_models
            if use_case in m.use_cases or any(use_case in uc for uc in m.use_cases)
        ]
        
        # فیلتر size
        if max_size_mb:
            relevant = [m for m in relevant if m.size_mb <= max_size_mb]
        
        # مرتب‌سازی بر اساس relevance و performance
        sorted_models = sorted(
            relevant,
            key=lambda m: (m.performance_score * m.popularity_score),
            reverse=True
        )
        
        return sorted_models[:max_models]
    
    def search_models(self, query: str) -> List[ModelInfo]:
        """
        جستجو در تمام فیلدهای مدل‌ها
        """
        query_lower = query.lower()
        all_models = self.get_all_models()
        
        results = []
        for model in all_models:
            # جستجو در فیلدهای مختلف
            if (
                query_lower in model.name.lower()
                or query_lower in model.description.lower()
                or any(query_lower in tag for tag in model.tags)
                or any(query_lower in uc for uc in model.use_cases)
                or query_lower in model.hf_id.lower()
            ):
                results.append(model)
        
        # مرتب‌سازی بر اساس relevance
        return sorted(
            results,
            key=lambda m: (m.performance_score, m.popularity_score),
            reverse=True
        )
    
    def get_model_stats(self) -> Dict[str, Any]:
        """آمار کامل مدل‌ها"""
        all_models = self.get_all_models()
        
        # آمار بر اساس category
        by_category = {}
        for cat in ModelCategory:
            count = len([m for m in all_models if m.category == cat.value])
            by_category[cat.value] = count
        
        # آمار بر اساس size
        by_size = {}
        for size in ModelSize:
            count = len([m for m in all_models if m.size == size.value])
            by_size[size.value] = count
        
        # آمار tags
        all_tags = {}
        for model in all_models:
            for tag in model.tags:
                all_tags[tag] = all_tags.get(tag, 0) + 1
        
        # Top tags
        top_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_models": len(all_models),
            "by_category": by_category,
            "by_size": by_size,
            "free_models": len([m for m in all_models if m.free]),
            "no_auth_models": len([m for m in all_models if not m.requires_auth]),
            "api_compatible": len([m for m in all_models if m.api_compatible]),
            "downloadable": len([m for m in all_models if m.downloadable]),
            "avg_performance": round(
                sum(m.performance_score for m in all_models) / len(all_models), 2
            ),
            "avg_popularity": round(
                sum(m.popularity_score for m in all_models) / len(all_models), 2
            ),
            "total_size_gb": round(sum(m.size_mb for m in all_models) / 1024, 2),
            "top_tags": [{"tag": tag, "count": count} for tag, count in top_tags],
            "languages_supported": list(set(
                lang for m in all_models for lang in m.languages
            ))
        }
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """لیست categories با آمار"""
        all_models = self.get_all_models()
        
        categories = []
        for cat in ModelCategory:
            models_in_cat = [m for m in all_models if m.category == cat.value]
            if models_in_cat:
                categories.append({
                    "id": cat.value,
                    "name": cat.name,
                    "count": len(models_in_cat),
                    "avg_performance": round(
                        sum(m.performance_score for m in models_in_cat) / len(models_in_cat),
                        2
                    ),
                    "models": [m.id for m in models_in_cat[:5]]  # Top 5
                })
        
        return sorted(categories, key=lambda x: x["count"], reverse=True)
    
    def export_catalog_json(self, filepath: str):
        """Export کردن کاتالوگ به JSON"""
        catalog = {
            "models": [m.to_dict() for m in self.get_all_models()],
            "stats": self.get_model_stats(),
            "categories": self.get_categories()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported catalog to {filepath}")


# ===== Singleton Instance =====
_model_manager = None

def get_model_manager() -> AdvancedModelManager:
    """دریافت instance سراسری model manager"""
    global _model_manager
    if _model_manager is None:
        _model_manager = AdvancedModelManager()
    return _model_manager


# ===== Usage Examples =====
if __name__ == "__main__":
    # ایجاد manager
    manager = AdvancedModelManager()
    
    print("=== Model Manager Test ===\n")
    
    # آمار کلی
    stats = manager.get_model_stats()
    print(f"📊 Total Models: {stats['total_models']}")
    print(f"📊 Free Models: {stats['free_models']}")
    print(f"📊 API Compatible: {stats['api_compatible']}")
    print(f"📊 Avg Performance: {stats['avg_performance']}")
    print(f"📊 Total Size: {stats['total_size_gb']} GB\n")
    
    # بهترین مدل‌های sentiment
    print("🏆 Best Sentiment Models:")
    best_sentiment = manager.get_best_models("sentiment", top_n=3, max_size_mb=500)
    for i, model in enumerate(best_sentiment, 1):
        print(f"   {i}. {model.name} - {model.performance_score:.2f}")
    
    # توصیه بر اساس use case
    print("\n💡 Recommended for 'twitter':")
    recommended = manager.recommend_models("twitter", max_models=3)
    for i, model in enumerate(recommended, 1):
        print(f"   {i}. {model.name} - {model.description[:50]}...")
    
    # جستجو
    print("\n🔍 Search for 'crypto':")
    search_results = manager.search_models("crypto")[:3]
    for i, model in enumerate(search_results, 1):
        print(f"   {i}. {model.name} - {model.category}")
    
    # Export
    # manager.export_catalog_json("/workspace/model_catalog.json")
    print("\n✅ Test complete!")

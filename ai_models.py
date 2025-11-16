#!/usr/bin/env python3
"""
AI Models Module for Crypto Data Aggregator
HuggingFace local inference for sentiment analysis, summarization, and market trend analysis
NO API calls - all inference runs locally using transformers library
"""

import logging
from typing import Dict, List, Optional, Any
from functools import lru_cache
import warnings

# Suppress HuggingFace warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import torch
    from transformers import (
        pipeline,
        AutoModelForSequenceClassification,
        AutoTokenizer,
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("transformers library not available. AI features will be disabled.")

import config

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== GLOBAL MODEL STORAGE ====================
# Lazy loading - models loaded only when first called
_models_initialized = False
_sentiment_twitter_pipeline = None
_sentiment_financial_pipeline = None
_summarization_pipeline = None
_crypto_sentiment_pipeline = None  # CryptoBERT model

# Model loading lock to prevent concurrent initialization
_models_loading = False

# ==================== MODEL INITIALIZATION ====================

def initialize_models() -> Dict[str, Any]:
    """
    Initialize all HuggingFace models for local inference.
    Loads sentiment and summarization models using pipeline().

    Returns:
        Dict with status, success flag, and loaded models info
    """
    global _models_initialized, _sentiment_twitter_pipeline
    global _sentiment_financial_pipeline, _summarization_pipeline
    global _crypto_sentiment_pipeline, _models_loading

    if _models_initialized:
        logger.info("Models already initialized")
        return {
            "success": True,
            "status": "Models already loaded",
            "models": {
                "sentiment_twitter": _sentiment_twitter_pipeline is not None,
                "sentiment_financial": _sentiment_financial_pipeline is not None,
                "summarization": _summarization_pipeline is not None,
                "crypto_sentiment": _crypto_sentiment_pipeline is not None,
            }
        }

    if _models_loading:
        logger.warning("Models are currently being loaded by another process")
        return {"success": False, "status": "Models loading in progress", "models": {}}

    if not TRANSFORMERS_AVAILABLE:
        logger.error("transformers library not available. Cannot initialize models.")
        return {
            "success": False,
            "status": "transformers library not installed",
            "models": {},
            "error": "Install transformers: pip install transformers torch"
        }

    _models_loading = True
    loaded_models = {}
    errors = []

    try:
        logger.info("Starting model initialization...")

        # Load Twitter sentiment model
        try:
            logger.info(f"Loading sentiment_twitter model: {config.HUGGINGFACE_MODELS['sentiment_twitter']}")
            _sentiment_twitter_pipeline = pipeline(
                "sentiment-analysis",
                model=config.HUGGINGFACE_MODELS["sentiment_twitter"],
                tokenizer=config.HUGGINGFACE_MODELS["sentiment_twitter"],
                truncation=True,
                max_length=512
            )
            loaded_models["sentiment_twitter"] = True
            logger.info("Twitter sentiment model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Twitter sentiment model: {str(e)}")
            loaded_models["sentiment_twitter"] = False
            errors.append(f"sentiment_twitter: {str(e)}")

        # Load Financial sentiment model
        try:
            logger.info(f"Loading sentiment_financial model: {config.HUGGINGFACE_MODELS['sentiment_financial']}")
            _sentiment_financial_pipeline = pipeline(
                "sentiment-analysis",
                model=config.HUGGINGFACE_MODELS["sentiment_financial"],
                tokenizer=config.HUGGINGFACE_MODELS["sentiment_financial"],
                truncation=True,
                max_length=512
            )
            loaded_models["sentiment_financial"] = True
            logger.info("Financial sentiment model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Financial sentiment model: {str(e)}")
            loaded_models["sentiment_financial"] = False
            errors.append(f"sentiment_financial: {str(e)}")

        # Load Summarization model
        try:
            logger.info(f"Loading summarization model: {config.HUGGINGFACE_MODELS['summarization']}")
            _summarization_pipeline = pipeline(
                "summarization",
                model=config.HUGGINGFACE_MODELS["summarization"],
                tokenizer=config.HUGGINGFACE_MODELS["summarization"],
                truncation=True
            )
            loaded_models["summarization"] = True
            logger.info("Summarization model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Summarization model: {str(e)}")
            loaded_models["summarization"] = False
            errors.append(f"summarization: {str(e)}")

        # Load CryptoBERT model (requires authentication)
        try:
            logger.info(f"Loading crypto_sentiment model: {config.HUGGINGFACE_MODELS['crypto_sentiment']}")
            # Load with authentication token
            use_auth_token = config.HF_TOKEN if config.HF_USE_AUTH_TOKEN else None
            if use_auth_token:
                logger.info("Using HF_TOKEN for authenticated model access")
            
            _crypto_sentiment_pipeline = pipeline(
                "fill-mask",  # CryptoBERT is a masked language model
                model=config.HUGGINGFACE_MODELS["crypto_sentiment"],
                tokenizer=config.HUGGINGFACE_MODELS["crypto_sentiment"],
                use_auth_token=use_auth_token,
                truncation=True,
                max_length=512
            )
            loaded_models["crypto_sentiment"] = True
            logger.info("CryptoBERT sentiment model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load CryptoBERT model: {str(e)}")
            loaded_models["crypto_sentiment"] = False
            errors.append(f"crypto_sentiment: {str(e)}")
            if "401" in str(e) or "403" in str(e) or "authentication" in str(e).lower():
                logger.error("Authentication failed. Please set HF_TOKEN environment variable.")

        # Check if at least one model loaded successfully
        success = any(loaded_models.values())
        _models_initialized = success

        result = {
            "success": success,
            "status": "Models loaded" if success else "All models failed to load",
            "models": loaded_models
        }

        if errors:
            result["errors"] = errors

        logger.info(f"Model initialization complete. Success: {success}")
        return result

    except Exception as e:
        logger.error(f"Unexpected error during model initialization: {str(e)}")
        return {
            "success": False,
            "status": "Initialization failed",
            "models": loaded_models,
            "error": str(e)
        }
    finally:
        _models_loading = False


def _ensure_models_loaded() -> bool:
    """
    Internal function to ensure models are loaded (lazy loading).

    Returns:
        bool: True if at least one model is loaded, False otherwise
    """
    global _models_initialized

    if not _models_initialized:
        result = initialize_models()
        return result.get("success", False)

    return True


# ==================== SENTIMENT ANALYSIS ====================

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of text using both Twitter and Financial sentiment models.
    Averages the scores and maps to sentiment labels.

    Args:
        text: Input text to analyze (will be truncated to 512 chars)

    Returns:
        Dict with:
            - label: str (positive/negative/neutral/very_positive/very_negative)
            - score: float (averaged sentiment score from -1 to 1)
            - confidence: float (confidence in the prediction 0-1)
            - details: Dict with individual model results
    """
    try:
        # Input validation
        if not text or not isinstance(text, str):
            logger.warning("Invalid text input for sentiment analysis")
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "error": "Invalid input text"
            }

        # Truncate text to model limit
        original_length = len(text)
        text = text[:512].strip()

        if len(text) < 10:
            logger.warning("Text too short for meaningful sentiment analysis")
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "warning": "Text too short"
            }

        # Ensure models are loaded
        if not _ensure_models_loaded():
            logger.error("Models not available for sentiment analysis")
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "error": "Models not initialized"
            }

        scores = []
        confidences = []
        model_results = {}

        # Analyze with Twitter sentiment model
        if _sentiment_twitter_pipeline is not None:
            try:
                twitter_result = _sentiment_twitter_pipeline(text)[0]

                # Convert label to score (-1 to 1)
                label = twitter_result['label'].lower()
                confidence = twitter_result['score']

                # Map label to numeric score
                if 'positive' in label:
                    score = confidence
                elif 'negative' in label:
                    score = -confidence
                else:  # neutral
                    score = 0.0

                scores.append(score)
                confidences.append(confidence)
                model_results["twitter"] = {
                    "label": label,
                    "score": score,
                    "confidence": confidence
                }
                logger.debug(f"Twitter sentiment: {label} (score: {score:.3f})")

            except Exception as e:
                logger.error(f"Twitter sentiment analysis failed: {str(e)}")
                model_results["twitter"] = {"error": str(e)}

        # Analyze with Financial sentiment model
        if _sentiment_financial_pipeline is not None:
            try:
                financial_result = _sentiment_financial_pipeline(text)[0]

                # Convert label to score (-1 to 1)
                label = financial_result['label'].lower()
                confidence = financial_result['score']

                # Map FinBERT labels to score
                if 'positive' in label:
                    score = confidence
                elif 'negative' in label:
                    score = -confidence
                else:  # neutral
                    score = 0.0

                scores.append(score)
                confidences.append(confidence)
                model_results["financial"] = {
                    "label": label,
                    "score": score,
                    "confidence": confidence
                }
                logger.debug(f"Financial sentiment: {label} (score: {score:.3f})")

            except Exception as e:
                logger.error(f"Financial sentiment analysis failed: {str(e)}")
                model_results["financial"] = {"error": str(e)}

        # Check if we got any results
        if not scores:
            logger.error("All sentiment models failed")
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "error": "All models failed",
                "details": model_results
            }

        # Average the scores
        avg_score = sum(scores) / len(scores)
        avg_confidence = sum(confidences) / len(confidences)

        # Map score to sentiment label based on config.SENTIMENT_LABELS
        sentiment_label = "neutral"
        for label, (min_score, max_score) in config.SENTIMENT_LABELS.items():
            if min_score <= avg_score < max_score:
                sentiment_label = label
                break

        result = {
            "label": sentiment_label,
            "score": round(avg_score, 4),
            "confidence": round(avg_confidence, 4),
            "details": model_results
        }

        if original_length > 512:
            result["warning"] = f"Text truncated from {original_length} to 512 characters"

        logger.info(f"Sentiment analysis complete: {sentiment_label} (score: {avg_score:.3f})")
        return result

    except Exception as e:
        logger.error(f"Unexpected error in sentiment analysis: {str(e)}")
        return {
            "label": "neutral",
            "score": 0.0,
            "confidence": 0.0,
            "error": f"Analysis failed: {str(e)}"
        }


# ==================== CRYPTO SENTIMENT ANALYSIS (CryptoBERT) ====================

def analyze_crypto_sentiment(text: str, mask_token: str = "[MASK]") -> Dict[str, Any]:
    """
    Analyze cryptocurrency-specific sentiment using CryptoBERT model.
    Uses fill-mask to predict sentiment-related tokens in crypto context.
    
    Args:
        text: Input text to analyze (crypto-related content)
        mask_token: Token to use for masking (default: [MASK])
    
    Returns:
        Dict with:
            - label: str (positive/negative/neutral)
            - score: float (confidence score 0-1)
            - predictions: List of top predictions from the model
            - error: str (if any error occurs)
    """
    try:
        # Input validation
        if not text or not isinstance(text, str):
            logger.warning("Invalid text input for crypto sentiment analysis")
            return {
                "label": "neutral",
                "score": 0.0,
                "error": "Invalid input text"
            }
        
        # Ensure models are loaded
        if not _ensure_models_loaded():
            logger.error("Models not available for crypto sentiment analysis")
            return {
                "label": "neutral",
                "score": 0.0,
                "error": "CryptoBERT model not initialized"
            }
        
        # Check if CryptoBERT model is available
        if _crypto_sentiment_pipeline is None:
            logger.warning("CryptoBERT model not loaded, falling back to standard sentiment")
            return analyze_sentiment(text)
        
        try:
            # Create masked version for sentiment prediction
            # Add sentiment-related mask context
            masked_text = f"{text[:400]} The market sentiment is {mask_token}."
            
            # Get predictions from CryptoBERT
            predictions = _crypto_sentiment_pipeline(masked_text, top_k=5)
            
            # Analyze predictions to determine sentiment
            sentiment_keywords = {
                "positive": ["bullish", "positive", "optimistic", "good", "great", "rising", "high", "strong"],
                "negative": ["bearish", "negative", "pessimistic", "bad", "poor", "falling", "low", "weak"],
                "neutral": ["neutral", "stable", "flat", "unchanged", "moderate"]
            }
            
            # Score each prediction
            sentiment_scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
            
            for pred in predictions:
                token = pred["token_str"].lower().strip()
                score = pred["score"]
                
                for sentiment, keywords in sentiment_keywords.items():
                    if any(keyword in token for keyword in keywords):
                        sentiment_scores[sentiment] += score
                        break
            
            # Determine dominant sentiment
            if sum(sentiment_scores.values()) == 0:
                # No sentiment keywords found, use standard sentiment analysis
                return analyze_sentiment(text)
            
            dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
            confidence = sentiment_scores[dominant_sentiment]
            
            result = {
                "label": dominant_sentiment,
                "score": round(confidence, 4),
                "predictions": [
                    {
                        "token": p["token_str"],
                        "score": round(p["score"], 4)
                    } for p in predictions[:3]
                ],
                "model": "CryptoBERT"
            }
            
            logger.info(f"CryptoBERT sentiment: {dominant_sentiment} (score: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"CryptoBERT analysis failed: {str(e)}")
            # Fallback to standard sentiment analysis
            logger.info("Falling back to standard sentiment analysis")
            return analyze_sentiment(text)
    
    except Exception as e:
        logger.error(f"Unexpected error in crypto sentiment analysis: {str(e)}")
        return {
            "label": "neutral",
            "score": 0.0,
            "error": f"Analysis failed: {str(e)}"
        }


# ==================== TEXT SUMMARIZATION ====================

def summarize_text(text: str, max_length: int = 130, min_length: int = 30) -> str:
    """
    Summarize text using HuggingFace summarization model.
    Returns original text if it's too short or if summarization fails.

    Args:
        text: Input text to summarize
        max_length: Maximum length of summary (default: 130)
        min_length: Minimum length of summary (default: 30)

    Returns:
        str: Summarized text or original text if summarization fails
    """
    try:
        # Input validation
        if not text or not isinstance(text, str):
            logger.warning("Invalid text input for summarization")
            return ""

        text = text.strip()

        # Return as-is if text is too short
        if len(text) < 100:
            logger.debug("Text too short for summarization, returning original")
            return text

        # Ensure models are loaded
        if not _ensure_models_loaded():
            logger.error("Models not available for summarization")
            return text

        # Check if summarization model is available
        if _summarization_pipeline is None:
            logger.warning("Summarization model not loaded, returning original text")
            return text

        try:
            # Perform summarization
            logger.debug(f"Summarizing text of length {len(text)}")

            # Adjust max_length based on input length
            input_length = len(text.split())
            if input_length < max_length:
                max_length = max(min_length, int(input_length * 0.7))

            summary_result = _summarization_pipeline(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True
            )

            if summary_result and len(summary_result) > 0:
                summary_text = summary_result[0]['summary_text']
                logger.info(f"Text summarized: {len(text)} -> {len(summary_text)} chars")
                return summary_text
            else:
                logger.warning("Summarization returned empty result")
                return text

        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            return text

    except Exception as e:
        logger.error(f"Unexpected error in summarization: {str(e)}")
        return text if isinstance(text, str) else ""


# ==================== MARKET TREND ANALYSIS ====================

def analyze_market_trend(price_history: List[Dict]) -> Dict[str, Any]:
    """
    Analyze market trends using technical indicators (MA, RSI) and price history.
    Generates predictions and support/resistance levels.

    Args:
        price_history: List of dicts with 'price', 'timestamp', 'volume' keys
                      Format: [{"price": 50000.0, "timestamp": 1234567890, "volume": 1000}, ...]

    Returns:
        Dict with:
            - trend: str (Bullish/Bearish/Neutral)
            - ma7: float (7-day moving average)
            - ma30: float (30-day moving average)
            - rsi: float (Relative Strength Index)
            - support_level: float (recent price minimum)
            - resistance_level: float (recent price maximum)
            - prediction: str (market prediction for next 24-72h)
            - confidence: float (confidence score 0-1)
    """
    try:
        # Input validation
        if not price_history or not isinstance(price_history, list):
            logger.warning("Invalid price_history input")
            return {
                "trend": "Neutral",
                "support_level": 0.0,
                "resistance_level": 0.0,
                "prediction": "Insufficient data for analysis",
                "confidence": 0.0,
                "error": "Invalid input"
            }

        if len(price_history) < 2:
            logger.warning("Insufficient price history for analysis")
            return {
                "trend": "Neutral",
                "support_level": 0.0,
                "resistance_level": 0.0,
                "prediction": "Need at least 2 data points",
                "confidence": 0.0,
                "error": "Insufficient data"
            }

        # Extract prices from history
        prices = []
        for item in price_history:
            if isinstance(item, dict) and 'price' in item:
                try:
                    price = float(item['price'])
                    if price > 0:
                        prices.append(price)
                except (ValueError, TypeError):
                    continue
            elif isinstance(item, (int, float)):
                if item > 0:
                    prices.append(float(item))

        if len(prices) < 2:
            logger.warning("No valid prices found in price_history")
            return {
                "trend": "Neutral",
                "support_level": 0.0,
                "resistance_level": 0.0,
                "prediction": "No valid price data",
                "confidence": 0.0,
                "error": "No valid prices"
            }

        # Calculate support and resistance levels
        support_level = min(prices[-30:]) if len(prices) >= 30 else min(prices)
        resistance_level = max(prices[-30:]) if len(prices) >= 30 else max(prices)

        # Calculate Moving Averages
        ma7 = None
        ma30 = None

        if len(prices) >= 7:
            ma7 = sum(prices[-7:]) / 7
        else:
            ma7 = sum(prices) / len(prices)

        if len(prices) >= 30:
            ma30 = sum(prices[-30:]) / 30
        else:
            ma30 = sum(prices) / len(prices)

        # Calculate RSI (Relative Strength Index)
        rsi = _calculate_rsi(prices, period=config.RSI_PERIOD)

        # Determine trend based on MA crossover and current price
        current_price = prices[-1]
        trend = "Neutral"

        if ma7 > ma30 and current_price > ma7:
            trend = "Bullish"
        elif ma7 < ma30 and current_price < ma7:
            trend = "Bearish"
        elif abs(ma7 - ma30) / ma30 < 0.02:  # Within 2% = neutral
            trend = "Neutral"
        else:
            # Additional checks
            if current_price > ma30:
                trend = "Bullish"
            elif current_price < ma30:
                trend = "Bearish"

        # Generate prediction based on trend and RSI
        prediction = _generate_market_prediction(
            trend=trend,
            rsi=rsi,
            current_price=current_price,
            ma7=ma7,
            ma30=ma30,
            support_level=support_level,
            resistance_level=resistance_level
        )

        # Calculate confidence score based on data quality
        confidence = _calculate_confidence(
            data_points=len(prices),
            rsi=rsi,
            trend=trend,
            price_volatility=_calculate_volatility(prices)
        )

        result = {
            "trend": trend,
            "ma7": round(ma7, 2),
            "ma30": round(ma30, 2),
            "rsi": round(rsi, 2),
            "support_level": round(support_level, 2),
            "resistance_level": round(resistance_level, 2),
            "current_price": round(current_price, 2),
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "data_points": len(prices)
        }

        logger.info(f"Market analysis complete: {trend} trend, RSI: {rsi:.2f}, Confidence: {confidence:.2f}")
        return result

    except Exception as e:
        logger.error(f"Unexpected error in market trend analysis: {str(e)}")
        return {
            "trend": "Neutral",
            "support_level": 0.0,
            "resistance_level": 0.0,
            "prediction": "Analysis failed",
            "confidence": 0.0,
            "error": f"Analysis error: {str(e)}"
        }


# ==================== HELPER FUNCTIONS ====================

def _calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI).

    Args:
        prices: List of prices
        period: RSI period (default: 14)

    Returns:
        float: RSI value (0-100)
    """
    try:
        if len(prices) < period + 1:
            # Not enough data, use available data
            period = max(2, len(prices) - 1)

        # Calculate price changes
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]

        # Separate gains and losses
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]

        # Calculate average gains and losses
        if len(gains) >= period:
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
        else:
            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0

        # Avoid division by zero
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0

        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    except Exception as e:
        logger.error(f"RSI calculation error: {str(e)}")
        return 50.0  # Return neutral RSI on error


def _generate_market_prediction(
    trend: str,
    rsi: float,
    current_price: float,
    ma7: float,
    ma30: float,
    support_level: float,
    resistance_level: float
) -> str:
    """
    Generate market prediction based on technical indicators.

    Returns:
        str: Detailed prediction for next 24-72 hours
    """
    try:
        predictions = []

        # RSI-based predictions
        if rsi > 70:
            predictions.append("overbought conditions suggest potential correction")
        elif rsi < 30:
            predictions.append("oversold conditions suggest potential bounce")
        elif 40 <= rsi <= 60:
            predictions.append("neutral momentum")

        # Trend-based predictions
        if trend == "Bullish":
            if current_price < resistance_level * 0.95:
                predictions.append(f"upward movement toward resistance at ${resistance_level:.2f}")
            else:
                predictions.append("potential breakout above resistance if momentum continues")
        elif trend == "Bearish":
            if current_price > support_level * 1.05:
                predictions.append(f"downward pressure toward support at ${support_level:.2f}")
            else:
                predictions.append("potential breakdown below support if selling continues")
        else:  # Neutral
            predictions.append(f"consolidation between ${support_level:.2f} and ${resistance_level:.2f}")

        # MA crossover signals
        if ma7 > ma30 * 1.02:
            predictions.append("strong bullish crossover signal")
        elif ma7 < ma30 * 0.98:
            predictions.append("strong bearish crossover signal")

        # Combine predictions
        if predictions:
            prediction_text = f"Next 24-72h: Expect {', '.join(predictions)}."
        else:
            prediction_text = "Next 24-72h: Insufficient signals for reliable prediction."

        # Add price range estimate
        price_range = resistance_level - support_level
        if price_range > 0:
            expected_low = current_price - (price_range * 0.1)
            expected_high = current_price + (price_range * 0.1)
            prediction_text += f" Price likely to range between ${expected_low:.2f} and ${expected_high:.2f}."

        return prediction_text

    except Exception as e:
        logger.error(f"Prediction generation error: {str(e)}")
        return "Unable to generate prediction due to data quality issues."


def _calculate_volatility(prices: List[float]) -> float:
    """
    Calculate price volatility (standard deviation).

    Args:
        prices: List of prices

    Returns:
        float: Volatility as percentage
    """
    try:
        if len(prices) < 2:
            return 0.0

        mean_price = sum(prices) / len(prices)
        variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
        std_dev = variance ** 0.5

        # Return as percentage of mean
        volatility = (std_dev / mean_price) * 100 if mean_price > 0 else 0.0
        return volatility

    except Exception as e:
        logger.error(f"Volatility calculation error: {str(e)}")
        return 0.0


def _calculate_confidence(
    data_points: int,
    rsi: float,
    trend: str,
    price_volatility: float
) -> float:
    """
    Calculate confidence score for market analysis.

    Args:
        data_points: Number of price data points
        rsi: RSI value
        trend: Market trend
        price_volatility: Price volatility percentage

    Returns:
        float: Confidence score (0-1)
    """
    try:
        confidence = 0.0

        # Data quality score (0-0.4)
        if data_points >= 30:
            data_score = 0.4
        elif data_points >= 14:
            data_score = 0.3
        elif data_points >= 7:
            data_score = 0.2
        else:
            data_score = 0.1

        confidence += data_score

        # RSI confidence (0-0.3)
        # Extreme RSI values (very high or very low) give higher confidence
        if rsi > 70 or rsi < 30:
            rsi_score = 0.3
        elif rsi > 60 or rsi < 40:
            rsi_score = 0.2
        else:
            rsi_score = 0.1

        confidence += rsi_score

        # Trend clarity (0-0.2)
        if trend in ["Bullish", "Bearish"]:
            trend_score = 0.2
        else:
            trend_score = 0.1

        confidence += trend_score

        # Volatility penalty (0-0.1)
        # Lower volatility = higher confidence
        if price_volatility < 5:
            volatility_score = 0.1
        elif price_volatility < 10:
            volatility_score = 0.05
        else:
            volatility_score = 0.0

        confidence += volatility_score

        # Ensure confidence is between 0 and 1
        confidence = max(0.0, min(1.0, confidence))

        return confidence

    except Exception as e:
        logger.error(f"Confidence calculation error: {str(e)}")
        return 0.5  # Return medium confidence on error


# ==================== CACHE DECORATORS ====================

@lru_cache(maxsize=100)
def _cached_sentiment(text_hash: int) -> Dict[str, Any]:
    """Cache wrapper for sentiment analysis (internal use only)."""
    # This would be called by analyze_sentiment with hash(text)
    # Not exposed directly to avoid cache invalidation issues
    pass


# ==================== MODULE INFO ====================

def get_model_info() -> Dict[str, Any]:
    """
    Get information about loaded models and their status.

    Returns:
        Dict with model information
    """
    return {
        "transformers_available": TRANSFORMERS_AVAILABLE,
        "models_initialized": _models_initialized,
        "models_loading": _models_loading,
        "loaded_models": {
            "sentiment_twitter": _sentiment_twitter_pipeline is not None,
            "sentiment_financial": _sentiment_financial_pipeline is not None,
            "summarization": _summarization_pipeline is not None,
            "crypto_sentiment": _crypto_sentiment_pipeline is not None,
        },
        "model_names": config.HUGGINGFACE_MODELS,
        "hf_auth_configured": config.HF_USE_AUTH_TOKEN,
        "device": "cuda" if TRANSFORMERS_AVAILABLE and torch.cuda.is_available() else "cpu"
    }


if __name__ == "__main__":
    # Test the module
    print("="*60)
    print("AI Models Module Test")
    print("="*60)

    # Get model info
    info = get_model_info()
    print(f"\nTransformers available: {info['transformers_available']}")
    print(f"Models initialized: {info['models_initialized']}")
    print(f"Device: {info['device']}")

    # Initialize models
    print("\n" + "="*60)
    print("Initializing models...")
    print("="*60)
    result = initialize_models()
    print(f"Success: {result['success']}")
    print(f"Status: {result['status']}")
    print(f"Loaded models: {result['models']}")

    if result['success']:
        # Test sentiment analysis
        print("\n" + "="*60)
        print("Testing Sentiment Analysis")
        print("="*60)
        test_text = "Bitcoin shows strong bullish momentum with increasing adoption and positive market sentiment."
        sentiment = analyze_sentiment(test_text)
        print(f"Text: {test_text}")
        print(f"Sentiment: {sentiment['label']}")
        print(f"Score: {sentiment['score']}")
        print(f"Confidence: {sentiment['confidence']}")

        # Test summarization
        print("\n" + "="*60)
        print("Testing Summarization")
        print("="*60)
        long_text = """
        Bitcoin, the world's largest cryptocurrency by market capitalization, has experienced
        significant growth over the past decade. Initially created as a peer-to-peer electronic
        cash system, Bitcoin has evolved into a store of value and investment asset. Institutional
        adoption has increased dramatically, with major companies adding Bitcoin to their balance
        sheets. The cryptocurrency market has matured, with improved infrastructure, regulatory
        clarity, and growing mainstream acceptance. However, volatility remains a characteristic
        feature of the market, presenting both opportunities and risks for investors.
        """
        summary = summarize_text(long_text)
        print(f"Original length: {len(long_text)} chars")
        print(f"Summary length: {len(summary)} chars")
        print(f"Summary: {summary}")

        # Test market trend analysis
        print("\n" + "="*60)
        print("Testing Market Trend Analysis")
        print("="*60)
        # Simulated price history (bullish trend)
        test_prices = [
            {"price": 45000, "timestamp": 1000000, "volume": 100},
            {"price": 45500, "timestamp": 1000001, "volume": 120},
            {"price": 46000, "timestamp": 1000002, "volume": 110},
            {"price": 46500, "timestamp": 1000003, "volume": 130},
            {"price": 47000, "timestamp": 1000004, "volume": 140},
            {"price": 47500, "timestamp": 1000005, "volume": 150},
            {"price": 48000, "timestamp": 1000006, "volume": 160},
            {"price": 48500, "timestamp": 1000007, "volume": 170},
        ]
        trend = analyze_market_trend(test_prices)
        print(f"Trend: {trend['trend']}")
        print(f"RSI: {trend['rsi']}")
        print(f"MA7: {trend['ma7']}")
        print(f"MA30: {trend['ma30']}")
        print(f"Support: ${trend['support_level']}")
        print(f"Resistance: ${trend['resistance_level']}")
        print(f"Prediction: {trend['prediction']}")
        print(f"Confidence: {trend['confidence']}")

    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)

/**
 * ═══════════════════════════════════════════════════════════════════
 * HUGGING FACE MODELS INTEGRATION
 * Using Popular HF Models for Crypto Analysis
 * ═══════════════════════════════════════════════════════════════════
 */

class HuggingFaceIntegration {
    constructor() {
        this.apiEndpoint = 'https://api-inference.huggingface.co/models';
        this.models = {
            sentiment: 'cardiffnlp/twitter-roberta-base-sentiment-latest',
            emotion: 'j-hartmann/emotion-english-distilroberta-base',
            textClassification: 'distilbert-base-uncased-finetuned-sst-2-english',
            summarization: 'facebook/bart-large-cnn',
            translation: 'Helsinki-NLP/opus-mt-en-fa'
        };
        this.cache = new Map();
        this.init();
    }

    init() {
        this.setupSentimentAnalysis();
        this.setupNewsSummarization();
        this.setupEmotionDetection();
    }

    /**
     * Sentiment Analysis using HF Model
     */
    async analyzeSentiment(text) {
        const cacheKey = `sentiment_${text.substring(0, 50)}`;
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        try {
            const response = await fetch(`${this.apiEndpoint}/${this.models.sentiment}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getApiKey()}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ inputs: text })
            });

            if (!response.ok) {
                throw new Error(`HF API error: ${response.status}`);
            }

            const data = await response.json();
            const result = this.processSentimentResult(data);
            
            this.cache.set(cacheKey, result);
            return result;
        } catch (error) {
            console.error('Sentiment analysis error:', error);
            return this.getFallbackSentiment(text);
        }
    }

    processSentimentResult(data) {
        if (Array.isArray(data) && data[0]) {
            const scores = data[0];
            return {
                label: scores[0]?.label || 'NEUTRAL',
                score: scores[0]?.score || 0.5,
                confidence: Math.round(scores[0]?.score * 100) || 50
            };
        }
        return { label: 'NEUTRAL', score: 0.5, confidence: 50 };
    }

    getFallbackSentiment(text) {
        // Simple fallback sentiment analysis
        const positiveWords = ['good', 'great', 'excellent', 'bullish', 'up', 'rise', 'gain', 'profit'];
        const negativeWords = ['bad', 'terrible', 'bearish', 'down', 'fall', 'loss', 'crash'];
        
        const lowerText = text.toLowerCase();
        const positiveCount = positiveWords.filter(w => lowerText.includes(w)).length;
        const negativeCount = negativeWords.filter(w => lowerText.includes(w)).length;

        if (positiveCount > negativeCount) {
            return { label: 'POSITIVE', score: 0.7, confidence: 70 };
        } else if (negativeCount > positiveCount) {
            return { label: 'NEGATIVE', score: 0.3, confidence: 70 };
        }
        return { label: 'NEUTRAL', score: 0.5, confidence: 50 };
    }

    /**
     * News Summarization
     */
    async summarizeNews(text, maxLength = 100) {
        const cacheKey = `summary_${text.substring(0, 50)}`;
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        try {
            const response = await fetch(`${this.apiEndpoint}/${this.models.summarization}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getApiKey()}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    inputs: text,
                    parameters: { max_length: maxLength, min_length: 30 }
                })
            });

            if (!response.ok) {
                throw new Error(`HF API error: ${response.status}`);
            }

            const data = await response.json();
            const summary = Array.isArray(data) ? data[0]?.summary_text : data.summary_text;
            
            this.cache.set(cacheKey, summary);
            return summary || text.substring(0, maxLength) + '...';
        } catch (error) {
            console.error('Summarization error:', error);
            return text.substring(0, maxLength) + '...';
        }
    }

    /**
     * Emotion Detection
     */
    async detectEmotion(text) {
        try {
            const response = await fetch(`${this.apiEndpoint}/${this.models.emotion}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getApiKey()}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ inputs: text })
            });

            if (!response.ok) {
                throw new Error(`HF API error: ${response.status}`);
            }

            const data = await response.json();
            return this.processEmotionResult(data);
        } catch (error) {
            console.error('Emotion detection error:', error);
            return { label: 'neutral', score: 0.5 };
        }
    }

    processEmotionResult(data) {
        if (Array.isArray(data) && data[0]) {
            const emotions = data[0];
            const topEmotion = emotions.reduce((max, curr) => 
                curr.score > max.score ? curr : max
            );
            return {
                label: topEmotion.label,
                score: topEmotion.score,
                confidence: Math.round(topEmotion.score * 100)
            };
        }
        return { label: 'neutral', score: 0.5, confidence: 50 };
    }

    /**
     * Setup sentiment analysis for news
     */
    setupSentimentAnalysis() {
        // Analyze news sentiment when news is loaded
        document.addEventListener('newsLoaded', async (e) => {
            const newsItems = e.detail;
            for (const item of newsItems) {
                if (item.title && !item.sentiment) {
                    item.sentiment = await this.analyzeSentiment(item.title + ' ' + (item.description || ''));
                }
            }
            
            // Dispatch event with analyzed news
            document.dispatchEvent(new CustomEvent('newsAnalyzed', { detail: newsItems }));
        });
    }

    /**
     * Setup news summarization
     */
    setupNewsSummarization() {
        document.addEventListener('newsLoaded', async (e) => {
            const newsItems = e.detail;
            for (const item of newsItems) {
                if (item.description && item.description.length > 200 && !item.summary) {
                    item.summary = await this.summarizeNews(item.description, 100);
                }
            }
        });
    }

    /**
     * Setup emotion detection
     */
    setupEmotionDetection() {
        // Can be used for social media posts, comments, etc.
        window.detectEmotion = async (text) => {
            return await this.detectEmotion(text);
        };
    }

    /**
     * Get API Key (should be set in environment or config)
     */
    getApiKey() {
        // Priority: window.HF_API_KEY > DASHBOARD_CONFIG.HF_TOKEN > default
        return window.HF_API_KEY || 
               (window.DASHBOARD_CONFIG && window.DASHBOARD_CONFIG.HF_TOKEN) || 
               'HF_TOKEN_HERE';
    }
}

// Initialize HF integration
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.hfIntegration = new HuggingFaceIntegration();
    });
} else {
    window.hfIntegration = new HuggingFaceIntegration();
}


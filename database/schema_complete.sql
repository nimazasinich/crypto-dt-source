-- ============================================
-- HF Space Complete Database Schema
-- Supports both SQLite (dev) and PostgreSQL (prod)
-- ============================================

-- Drop existing tables if needed (careful in production!)
-- DROP TABLE IF EXISTS rates CASCADE;
-- DROP TABLE IF EXISTS pairs CASCADE;
-- DROP TABLE IF EXISTS ohlc CASCADE;
-- DROP TABLE IF EXISTS market_snapshots CASCADE;
-- DROP TABLE IF EXISTS news CASCADE;
-- DROP TABLE IF EXISTS sentiment CASCADE;
-- DROP TABLE IF EXISTS whales CASCADE;
-- DROP TABLE IF EXISTS onchain_events CASCADE;
-- DROP TABLE IF EXISTS model_outputs CASCADE;
-- DROP TABLE IF EXISTS signals CASCADE;
-- DROP TABLE IF EXISTS econ_reports CASCADE;
-- DROP TABLE IF EXISTS api_logs CASCADE;
-- DROP TABLE IF EXISTS cache_entries CASCADE;

-- ============================================
-- A. RATES TABLE - Real-time price data
-- ============================================

CREATE TABLE IF NOT EXISTS rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite syntax, use SERIAL for PostgreSQL
    symbol VARCHAR(20) NOT NULL,
    pair VARCHAR(20) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    ts TIMESTAMP NOT NULL,
    source VARCHAR(100) NOT NULL,
    stored_from VARCHAR(100),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_rates_pair (pair),
    INDEX idx_rates_symbol (symbol),
    INDEX idx_rates_ts (ts),
    INDEX idx_rates_stored (stored_at)
);

-- PostgreSQL version:
-- CREATE TABLE IF NOT EXISTS rates (
--     id SERIAL PRIMARY KEY,
--     symbol VARCHAR(20) NOT NULL,
--     pair VARCHAR(20) NOT NULL,
--     price NUMERIC(20, 8) NOT NULL,
--     ts TIMESTAMP WITH TIME ZONE NOT NULL,
--     source VARCHAR(100) NOT NULL,
--     stored_from VARCHAR(100),
--     stored_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- );
-- CREATE INDEX idx_rates_pair ON rates(pair);
-- CREATE INDEX idx_rates_symbol ON rates(symbol);
-- CREATE INDEX idx_rates_ts ON rates(ts);
-- CREATE INDEX idx_rates_stored ON rates(stored_at);

-- ============================================
-- B. PAIRS TABLE - Trading pair metadata
-- ============================================

CREATE TABLE IF NOT EXISTS pairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair VARCHAR(20) NOT NULL UNIQUE,
    base VARCHAR(10) NOT NULL,
    quote VARCHAR(10) NOT NULL,
    tick_size DECIMAL(20, 10) NOT NULL,
    min_qty DECIMAL(20, 10) NOT NULL,
    max_qty DECIMAL(20, 10),
    status VARCHAR(20) DEFAULT 'active',
    source VARCHAR(100) NOT NULL,
    stored_from VARCHAR(100),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_pairs_base (base),
    INDEX idx_pairs_quote (quote),
    INDEX idx_pairs_status (status)
);

-- ============================================
-- C. OHLC TABLE - Historical candlestick data
-- ============================================

CREATE TABLE IF NOT EXISTS ohlc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL,
    interval INTEGER NOT NULL,  -- Interval in seconds
    ts TIMESTAMP NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    trades INTEGER,
    source VARCHAR(100) NOT NULL,
    stored_from VARCHAR(100),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite unique constraint
    UNIQUE(symbol, interval, ts),
    
    INDEX idx_ohlc_symbol (symbol),
    INDEX idx_ohlc_interval (interval),
    INDEX idx_ohlc_ts (ts),
    INDEX idx_ohlc_composite (symbol, interval, ts)
);

-- ============================================
-- D. MARKET_SNAPSHOTS TABLE - Market overview data
-- ============================================

CREATE TABLE IF NOT EXISTS market_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_ts TIMESTAMP NOT NULL,
    total_market_cap DECIMAL(20, 2),
    btc_dominance DECIMAL(5, 2),
    eth_dominance DECIMAL(5, 2),
    volume_24h DECIMAL(20, 2),
    active_cryptos INTEGER,
    fear_greed_index INTEGER,
    payload_json TEXT,  -- JSON blob for flexible additional data
    source VARCHAR(100) NOT NULL,
    stored_from VARCHAR(100),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_snapshots_ts (snapshot_ts),
    INDEX idx_snapshots_stored (stored_at)
);

-- ============================================
-- E. NEWS TABLE - Crypto news articles
-- ============================================

CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id VARCHAR(100) UNIQUE,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000),
    author VARCHAR(200),
    raw_text TEXT,
    summary TEXT,
    published_at TIMESTAMP,
    tags VARCHAR(500),  -- Comma-separated tags
    sentiment_score DECIMAL(3, 2),  -- -1 to 1
    relevance_score DECIMAL(3, 2),  -- 0 to 1
    source VARCHAR(100) NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stored_from VARCHAR(100),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_news_published (published_at),
    INDEX idx_news_sentiment (sentiment_score),
    INDEX idx_news_source (source)
);

-- ============================================
-- F. SENTIMENT TABLE - Sentiment analysis results
-- ============================================

CREATE TABLE IF NOT EXISTS sentiment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20),
    text_hash VARCHAR(64),  -- Hash of analyzed text
    score DECIMAL(3, 2) NOT NULL,  -- -1 to 1
    label VARCHAR(20) NOT NULL,  -- POSITIVE, NEGATIVE, NEUTRAL
    confidence DECIMAL(3, 2),  -- 0 to 1
    summary TEXT,
    model VARCHAR(100) NOT NULL,
    features_used TEXT,  -- JSON of features
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100) NOT NULL,
    stored_from VARCHAR(100),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_sentiment_symbol (symbol),
    INDEX idx_sentiment_label (label),
    INDEX idx_sentiment_generated (generated_at)
);

-- ============================================
-- G. WHALES TABLE - Large transactions
-- ============================================

CREATE TABLE IF NOT EXISTS whales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_hash VARCHAR(100) NOT NULL,
    chain VARCHAR(50) NOT NULL,
    from_addr VARCHAR(100) NOT NULL,
    to_addr VARCHAR(100) NOT NULL,
    token VARCHAR(20) NOT NULL,
    amount DECIMAL(30, 10) NOT NULL,
    amount_usd DECIMAL(20, 2) NOT NULL,
    gas_used DECIMAL(20, 0),
    gas_price DECIMAL(20, 10),
    block INTEGER NOT NULL,
    tx_at TIMESTAMP NOT NULL,
    tx_type VARCHAR(50),  -- transfer, swap, mint, burn
    metadata TEXT,  -- JSON for additional data
    source VARCHAR(100) NOT NULL,
    stored_from VARCHAR(100),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite unique constraint
    UNIQUE(chain, tx_hash),
    
    INDEX idx_whales_chain (chain),
    INDEX idx_whales_token (token),
    INDEX idx_whales_amount_usd (amount_usd),
    INDEX idx_whales_tx_at (tx_at),
    INDEX idx_whales_from (from_addr),
    INDEX idx_whales_to (to_addr)
);

-- ============================================
-- H. ONCHAIN_EVENTS TABLE - On-chain activity
-- ============================================

CREATE TABLE IF NOT EXISTS onchain_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id VARCHAR(100) UNIQUE,
    chain VARCHAR(50) NOT NULL,
    address VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- transfer, approve, swap, etc.
    contract_addr VARCHAR(100),
    method VARCHAR(100),
    block_number INTEGER NOT NULL,
    tx_hash VARCHAR(100),
    log_index INTEGER,
    event_data TEXT,  -- JSON blob
    decoded_data TEXT,  -- JSON blob of decoded params
    event_at TIMESTAMP NOT NULL,
    source VARCHAR(100) NOT NULL,
    stored_from VARCHAR(100),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_onchain_chain (chain),
    INDEX idx_onchain_address (address),
    INDEX idx_onchain_type (event_type),
    INDEX idx_onchain_block (block_number),
    INDEX idx_onchain_at (event_at)
);

-- ============================================
-- I. MODEL_OUTPUTS TABLE - AI model predictions
-- ============================================

CREATE TABLE IF NOT EXISTS model_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id VARCHAR(100) UNIQUE,
    model_key VARCHAR(100) NOT NULL,
    model_version VARCHAR(20),
    symbol VARCHAR(20),
    prediction_type VARCHAR(50) NOT NULL,  -- price, sentiment, signal, etc.
    horizon VARCHAR(20),  -- 1h, 24h, 7d, etc.
    score DECIMAL(5, 4) NOT NULL,  -- 0 to 1
    confidence DECIMAL(3, 2),  -- 0 to 1
    prediction_value DECIMAL(20, 8),
    lower_bound DECIMAL(20, 8),
    upper_bound DECIMAL(20, 8),
    features_json TEXT,  -- Input features used
    data_json TEXT,  -- Full prediction data
    explanation TEXT,
    meta_json TEXT,  -- Meta information
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,
    source VARCHAR(100) NOT NULL,
    stored_from VARCHAR(100),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_models_key (model_key),
    INDEX idx_models_symbol (symbol),
    INDEX idx_models_type (prediction_type),
    INDEX idx_models_generated (generated_at),
    INDEX idx_models_score (score)
);

-- ============================================
-- J. SIGNALS TABLE - Trading signals
-- ============================================

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id VARCHAR(100) UNIQUE,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,  -- buy, sell, hold, alert
    strength VARCHAR(20),  -- weak, moderate, strong
    score DECIMAL(5, 4) NOT NULL,
    confidence DECIMAL(3, 2),
    timeframe VARCHAR(20),
    entry_price DECIMAL(20, 8),
    target_price DECIMAL(20, 8),
    stop_loss DECIMAL(20, 8),
    risk_reward_ratio DECIMAL(5, 2),
    conditions TEXT,  -- JSON of trigger conditions
    metadata TEXT,  -- Additional JSON data
    model_used VARCHAR(100),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',  -- active, expired, triggered, cancelled
    source VARCHAR(100) NOT NULL,
    stored_from VARCHAR(100),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_signals_symbol (symbol),
    INDEX idx_signals_type (signal_type),
    INDEX idx_signals_status (status),
    INDEX idx_signals_generated (generated_at),
    INDEX idx_signals_score (score)
);

-- ============================================
-- K. ECON_REPORTS TABLE - Economic analysis
-- ============================================

CREATE TABLE IF NOT EXISTS econ_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id VARCHAR(100) UNIQUE,
    currency VARCHAR(10) NOT NULL,
    period VARCHAR(20) NOT NULL,
    context VARCHAR(500),
    report_text TEXT NOT NULL,
    findings_json TEXT,  -- JSON array of findings
    metrics_json TEXT,  -- JSON of economic metrics
    score DECIMAL(3, 1),  -- 0 to 10
    sentiment VARCHAR(20),
    risk_level VARCHAR(20),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,
    source VARCHAR(100) NOT NULL,
    stored_from VARCHAR(100),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_econ_currency (currency),
    INDEX idx_econ_period (period),
    INDEX idx_econ_generated (generated_at)
);

-- ============================================
-- L. API_LOGS TABLE - API request logging
-- ============================================

CREATE TABLE IF NOT EXISTS api_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id VARCHAR(100) UNIQUE,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    params TEXT,  -- JSON of parameters
    response_code INTEGER,
    response_time_ms INTEGER,
    source_used VARCHAR(100),
    fallback_attempted TEXT,  -- JSON array of attempted sources
    error_message TEXT,
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_logs_endpoint (endpoint),
    INDEX idx_logs_created (created_at),
    INDEX idx_logs_response_code (response_code)
);

-- ============================================
-- M. CACHE_ENTRIES TABLE - Response caching
-- ============================================

CREATE TABLE IF NOT EXISTS cache_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key VARCHAR(200) NOT NULL UNIQUE,
    endpoint VARCHAR(200) NOT NULL,
    params_hash VARCHAR(64) NOT NULL,
    response_data TEXT NOT NULL,  -- JSON response
    ttl_seconds INTEGER NOT NULL,
    hit_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_accessed TIMESTAMP,
    
    INDEX idx_cache_key (cache_key),
    INDEX idx_cache_expires (expires_at),
    INDEX idx_cache_endpoint (endpoint)
);

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- Latest rates view
CREATE VIEW IF NOT EXISTS v_latest_rates AS
SELECT 
    pair,
    price,
    ts,
    source
FROM rates
WHERE (pair, stored_at) IN (
    SELECT pair, MAX(stored_at)
    FROM rates
    GROUP BY pair
);

-- Market summary view
CREATE VIEW IF NOT EXISTS v_market_summary AS
SELECT 
    (SELECT total_market_cap FROM market_snapshots ORDER BY snapshot_ts DESC LIMIT 1) as market_cap,
    (SELECT btc_dominance FROM market_snapshots ORDER BY snapshot_ts DESC LIMIT 1) as btc_dominance,
    (SELECT COUNT(DISTINCT pair) FROM rates WHERE stored_at > datetime('now', '-1 hour')) as active_pairs,
    (SELECT AVG(sentiment_score) FROM news WHERE fetched_at > datetime('now', '-24 hours')) as avg_news_sentiment;

-- Top whales view (last 24h)
CREATE VIEW IF NOT EXISTS v_top_whales_24h AS
SELECT 
    chain,
    token,
    COUNT(*) as tx_count,
    SUM(amount_usd) as total_volume_usd,
    AVG(amount_usd) as avg_tx_usd,
    MAX(amount_usd) as max_tx_usd
FROM whales
WHERE tx_at > datetime('now', '-24 hours')
GROUP BY chain, token
ORDER BY total_volume_usd DESC;

-- Active signals view
CREATE VIEW IF NOT EXISTS v_active_signals AS
SELECT 
    symbol,
    signal_type,
    strength,
    score,
    confidence,
    entry_price,
    target_price,
    stop_loss,
    generated_at,
    expires_at
FROM signals
WHERE status = 'active' 
  AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
ORDER BY score DESC, generated_at DESC;

-- ============================================
-- TRIGGERS FOR AUTO-UPDATE
-- ============================================

-- SQLite trigger for updated_at
CREATE TRIGGER IF NOT EXISTS update_pairs_timestamp 
AFTER UPDATE ON pairs
BEGIN
    UPDATE pairs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- PostgreSQL version:
-- CREATE OR REPLACE FUNCTION update_updated_at()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     NEW.updated_at = CURRENT_TIMESTAMP;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;
-- 
-- CREATE TRIGGER update_pairs_timestamp
-- BEFORE UPDATE ON pairs
-- FOR EACH ROW
-- EXECUTE FUNCTION update_updated_at();

-- ============================================
-- INITIAL DATA / SEEDS
-- ============================================

-- Insert default pairs (if not exists)
INSERT OR IGNORE INTO pairs (pair, base, quote, tick_size, min_qty, source)
VALUES 
    ('BTC/USDT', 'BTC', 'USDT', 0.01, 0.00001, 'hf'),
    ('ETH/USDT', 'ETH', 'USDT', 0.01, 0.0001, 'hf'),
    ('SOL/USDT', 'SOL', 'USDT', 0.001, 0.01, 'hf'),
    ('BNB/USDT', 'BNB', 'USDT', 0.01, 0.001, 'hf'),
    ('XRP/USDT', 'XRP', 'USDT', 0.0001, 1.0, 'hf');

-- ============================================
-- PERFORMANCE OPTIMIZATIONS
-- ============================================

-- Enable WAL mode for SQLite (better concurrency)
-- PRAGMA journal_mode = WAL;
-- PRAGMA synchronous = NORMAL;
-- PRAGMA cache_size = -64000;  -- 64MB cache
-- PRAGMA temp_store = MEMORY;

-- PostgreSQL optimizations (run as superuser):
-- ALTER DATABASE your_db SET random_page_cost = 1.1;
-- ALTER DATABASE your_db SET effective_cache_size = '4GB';
-- ALTER DATABASE your_db SET shared_buffers = '256MB';
-- ALTER DATABASE your_db SET work_mem = '16MB';

-- ============================================
-- MAINTENANCE QUERIES
-- ============================================

-- Clean old cache entries
-- DELETE FROM cache_entries WHERE expires_at < CURRENT_TIMESTAMP;

-- Archive old logs
-- DELETE FROM api_logs WHERE created_at < datetime('now', '-30 days');

-- Vacuum and analyze (maintenance)
-- VACUUM;
-- ANALYZE;

-- ============================================
-- GRANTS FOR POSTGRESQL
-- ============================================

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hf_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hf_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO hf_user;
# Crypto Data Source - Project Structure Report

## Overview

A comprehensive cryptocurrency data aggregation and analysis platform designed for deployment on Hugging Face Spaces. The system provides real-time market data, AI-powered sentiment analysis, trading signals, and multi-source data aggregation.

## Architecture Layers

### 1. **Entry Points**

- **`main.py`**: FastAPI entry point for HuggingFace Spaces (port 7860)
- **`app.py`**: Flask-based fallback server with basic endpoints
- **`hf_unified_server.py`**: Main FastAPI application with unified routing

### 2. **API Layer** (`/api/`)

- **FastAPI Routers** (`backend/routers/`): 28 router modules for different API domains
- **Legacy Endpoints** (`api/`): 15+ endpoint modules for various services
- **WebSocket Support**: Real-time data streaming via WebSocket endpoints
- **Key Features**:
  - Multi-source data aggregation
  - AI trading signals and sentiment analysis
  - OHLCV data endpoints
  - News aggregation
  - Resource management APIs

### 3. **Backend Services** (`backend/services/`)

- **70 service modules** organized by functionality:
  - **Data Collection**: `unified_data_collector.py`, `market_data_aggregator.py`, `news_aggregator.py`
  - **AI/ML**: `real_ai_models.py`, `ai_service_unified.py`, `hf_inference_api_client.py`
  - **Trading**: `futures_trading_service.py`, `backtesting_service.py`
  - **Providers**: Integration with CoinGecko, Binance, CryptoPanic, etc.
  - **Fallback Management**: `multi_source_fallback_engine.py`, `provider_fallback_manager.py`
  - **Resource Management**: `master_resource_orchestrator.py`, `resources_registry_service.py`

### 4. **Data Collection** (`collectors/`)

- **15 collector modules** for:
  - Market data collection
  - News aggregation
  - Sentiment analysis
  - On-chain data
  - Whale tracking
  - Scheduled data collection

### 5. **Database Layer** (`database/`)

- **SQLAlchemy models** (`models.py`)
- **Database manager** (`db_manager.py`)
- **Data access layer** (`data_access.py`)
- **Migration support** (`migrations.py`)
- **Schema definition** (`schema_complete.sql`)

### 6. **Monitoring & Health** (`monitoring/`)

- Health checking system
- Rate limiting
- Source pool management
- Scheduler for background tasks

### 7. **Core Infrastructure** (`core/`)

- Smart proxy manager
- Smart fallback manager
- Resource management utilities

### 8. **Configuration**

- **`config.py`**: Main configuration with HuggingFace integration
- **`providers_config_extended.json`**: Provider configurations
- **`api-resources/`**: Unified API resource registry
- **Strategy/Scoring configs**: Trading and scoring configurations

### 9. **Frontend** (`static/`, `templates/`)

- **263 static files**: HTML, CSS, JavaScript
- Dashboard UI
- System monitoring interface
- Multi-page architecture

### 10. **Workers** (`workers/`)

- Background worker processes
- Data processing tasks

## Key Technologies

- **Backend**: FastAPI, Flask
- **AI/ML**: HuggingFace Inference API, custom sentiment models
- **Data Sources**: CoinGecko, Binance, CryptoPanic, AlphaVantage, etc.
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Real-time**: WebSocket support
- **Deployment**: Docker, HuggingFace Spaces

## Key Features

1. **Multi-Source Data Aggregation**: Aggregates data from 70+ API providers
2. **AI-Powered Analysis**: Sentiment analysis, trading signals, decision support
3. **Fallback System**: Automatic failover between data sources
4. **Real-time Updates**: WebSocket support for live data streaming
5. **Resource Management**: Dynamic API key rotation and smart access management
6. **Health Monitoring**: Self-healing system with health checks
7. **Trading Support**: Backtesting, futures trading, signal generation

## Project Statistics

- **Total Python Files**: ~200+
- **API Endpoints**: 100+ endpoints across multiple routers
- **Service Modules**: 70 backend services
- **Data Collectors**: 15 collector modules
- **API Providers**: 70+ integrated providers
- **Frontend Assets**: 263 static files

## Deployment

- **Primary**: HuggingFace Spaces (Docker)
- **Port**: 7860 (HF standard)
- **Entry Point**: `hf_unified_server:app`
- **Health Check**: `/api/health`

## Notable Design Patterns

- **Multi-source fallback**: Automatic provider switching on failure
- **Lazy loading**: Resources loaded on-demand to optimize memory
- **Service-oriented**: Modular service architecture
- **Router-based**: FastAPI router pattern for API organization
- **Provider abstraction**: Unified interface for multiple data sources

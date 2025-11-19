#!/usr/bin/env python3
"""
Hugging Face Unified Server - Main FastAPI application entry point.
This module imports the FastAPI app from api_server_extended for HF Docker Space deployment.
"""

from api_server_extended import app

__all__ = ["app"]


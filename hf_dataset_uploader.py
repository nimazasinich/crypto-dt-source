#!/usr/bin/env python3
"""
HuggingFace Dataset Uploader - Upload Real Data to HuggingFace Datasets
Ensures all data from external APIs is stored in HuggingFace Datasets first,
then served to clients from there.

Data Flow:
    External APIs → SQLite Cache → HuggingFace Datasets → Clients
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

try:
    from huggingface_hub import HfApi, create_repo, upload_file
    from datasets import Dataset, DatasetDict
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    print("⚠️  WARNING: huggingface_hub and datasets libraries not available")
    print("   Install with: pip install huggingface_hub datasets")

from utils.logger import setup_logger

logger = setup_logger("hf_dataset_uploader")


class HuggingFaceDatasetUploader:
    """
    Upload cryptocurrency data to HuggingFace Datasets

    Features:
    1. Upload market data (prices, volumes, etc.)
    2. Upload OHLC/candlestick data
    3. Automatic dataset creation if not exists
    4. Incremental updates (append new data)
    5. Dataset versioning and metadata
    """

    def __init__(
        self,
        hf_token: Optional[str] = None,
        dataset_namespace: Optional[str] = None,
        auto_create: bool = True
    ):
        """
        Initialize HuggingFace Dataset Uploader

        Args:
            hf_token: HuggingFace API token (or from HF_TOKEN env var)
            dataset_namespace: Dataset namespace (username or org name)
            auto_create: Automatically create datasets if they don't exist
        """
        if not HF_HUB_AVAILABLE:
            raise ImportError(
                "huggingface_hub and datasets libraries required. "
                "Install with: pip install huggingface_hub datasets"
            )

        self.token = hf_token or os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN")
        if not self.token:
            raise ValueError(
                "HuggingFace token required. Set HF_TOKEN environment variable "
                "or pass hf_token parameter"
            )

        self.namespace = dataset_namespace or os.getenv("HF_USERNAME")
        if not self.namespace:
            # Try to get username from HF API
            try:
                api = HfApi(token=self.token)
                user_info = api.whoami()
                self.namespace = user_info.get("name")
                logger.info(f"Detected HuggingFace username: {self.namespace}")
            except Exception as e:
                logger.warning(f"Could not detect HuggingFace username: {e}")
                self.namespace = "crypto-data-hub"  # Default namespace

        self.auto_create = auto_create
        self.api = HfApi(token=self.token)

        # Dataset names - ALL data types
        self.market_data_dataset = f"{self.namespace}/crypto-market-data"
        self.ohlc_dataset = f"{self.namespace}/crypto-ohlc-data"
        self.news_dataset = f"{self.namespace}/crypto-news-data"
        self.sentiment_dataset = f"{self.namespace}/crypto-sentiment-data"
        self.onchain_dataset = f"{self.namespace}/crypto-onchain-data"
        self.whale_dataset = f"{self.namespace}/crypto-whale-data"
        self.explorer_dataset = f"{self.namespace}/crypto-explorer-data"

        logger.info(f"HuggingFace Dataset Uploader initialized")
        logger.info(f"  Namespace: {self.namespace}")
        logger.info(f"  Datasets:")
        logger.info(f"    - Market: {self.market_data_dataset}")
        logger.info(f"    - OHLC: {self.ohlc_dataset}")
        logger.info(f"    - News: {self.news_dataset}")
        logger.info(f"    - Sentiment: {self.sentiment_dataset}")
        logger.info(f"    - On-chain: {self.onchain_dataset}")
        logger.info(f"    - Whale: {self.whale_dataset}")
        logger.info(f"    - Explorer: {self.explorer_dataset}")

    def _ensure_dataset_exists(self, dataset_name: str, description: str) -> bool:
        """
        Ensure dataset exists on HuggingFace Hub

        Args:
            dataset_name: Full dataset name (namespace/dataset)
            description: Dataset description

        Returns:
            bool: True if dataset exists or was created
        """
        try:
            # Check if dataset exists
            try:
                self.api.dataset_info(dataset_name, token=self.token)
                logger.info(f"Dataset exists: {dataset_name}")
                return True
            except Exception as check_error:
                # Check if it's an authentication error
                if "401" in str(check_error) or "Unauthorized" in str(check_error) or "expired" in str(check_error).lower():
                    logger.error(
                        f"❌ HuggingFace token authentication failed for {dataset_name}. "
                        f"Token may be expired or invalid. Please update HF_TOKEN environment variable."
                    )
                    return False
                
                # Dataset doesn't exist
                if self.auto_create:
                    logger.info(f"Creating dataset: {dataset_name}")
                    create_repo(
                        dataset_name,
                        token=self.token,
                        repo_type="dataset",
                        private=False  # Public dataset
                    )

                    # Upload README
                    readme_content = f"""---
tags:
- cryptocurrency
- crypto
- market-data
- real-time
- data-hub
license: mit
---

# {dataset_name}

{description}

## Data Source
This dataset is automatically updated from real cryptocurrency APIs:
- CoinGecko API (market data)
- Binance API (OHLC data)

## Update Frequency
Data is updated every 60 seconds with real-time information.

## Usage

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("{dataset_name}")

# Access data
df = dataset['train'].to_pandas()
print(df.head())
```

## Data Hub Architecture

```
External APIs → Data Hub → HuggingFace Datasets → Clients
```

All data is real - no mock or fake data.

## Last Updated
{datetime.utcnow().isoformat()}Z
"""

                    readme_path = Path("/tmp") / "README.md"
                    readme_path.write_text(readme_content)

                    self.api.upload_file(
                        path_or_fileobj=str(readme_path),
                        path_in_repo="README.md",
                        repo_id=dataset_name,
                        repo_type="dataset",
                        token=self.token
                    )

                    logger.info(f"✅ Created dataset: {dataset_name}")
                    return True
                else:
                    logger.error(f"Dataset does not exist and auto_create=False: {dataset_name}")
                    return False

        except Exception as e:
            # Check for authentication errors
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg or "expired" in error_msg.lower():
                logger.error(
                    f"❌ HuggingFace authentication error: {error_msg}\n"
                    f"   Please update your HF_TOKEN with a valid token from https://huggingface.co/settings/tokens"
                )
            else:
                logger.error(f"Error ensuring dataset exists: {e}", exc_info=True)
            return False

    async def upload_market_data(
        self,
        market_data: List[Dict[str, Any]],
        append: bool = True
    ) -> bool:
        """
        Upload market data to HuggingFace Dataset

        Args:
            market_data: List of market data dictionaries
            append: If True, append to existing data; if False, replace

        Returns:
            bool: True if upload successful
        """
        try:
            if not market_data:
                logger.warning("No market data to upload")
                return False

            # Ensure dataset exists
            if not self._ensure_dataset_exists(
                self.market_data_dataset,
                "Real-time cryptocurrency market data from multiple sources"
            ):
                return False

            # Add timestamp if not present
            current_time = datetime.utcnow().isoformat() + "Z"
            for data in market_data:
                if "timestamp" not in data:
                    data["timestamp"] = current_time
                if "fetched_at" not in data:
                    data["fetched_at"] = current_time

            # Convert to pandas DataFrame
            df = pd.DataFrame(market_data)

            # Create HuggingFace Dataset
            dataset = Dataset.from_pandas(df)

            # If append mode, we need to download existing data first
            if append:
                try:
                    from datasets import load_dataset
                    existing_dataset = load_dataset(
                        self.market_data_dataset,
                        split="train",
                        token=self.token
                    )

                    # Combine with new data
                    existing_df = existing_dataset.to_pandas()
                    combined_df = pd.concat([existing_df, df], ignore_index=True)

                    # Remove duplicates based on symbol and timestamp
                    # Keep only the latest record for each symbol
                    combined_df = combined_df.sort_values(
                        by=["symbol", "timestamp"],
                        ascending=[True, False]
                    )
                    combined_df = combined_df.drop_duplicates(
                        subset=["symbol"],
                        keep="first"
                    )

                    dataset = Dataset.from_pandas(combined_df)
                    logger.info(f"Appended {len(df)} new records to {len(existing_df)} existing records")

                except Exception as e:
                    logger.warning(f"Could not load existing dataset (might be first upload): {e}")
                    # First upload, use new data only
                    pass

            # Push to hub
            logger.info(f"Uploading {len(dataset)} records to {self.market_data_dataset}...")
            dataset.push_to_hub(
                self.market_data_dataset,
                token=self.token,
                private=False
            )

            logger.info(f"✅ Successfully uploaded market data to {self.market_data_dataset}")
            logger.info(f"   Records: {len(dataset)}")
            logger.info(f"   Columns: {dataset.column_names}")

            return True

        except Exception as e:
            logger.error(f"Error uploading market data: {e}", exc_info=True)
            return False

    async def upload_ohlc_data(
        self,
        ohlc_data: List[Dict[str, Any]],
        append: bool = True
    ) -> bool:
        """
        Upload OHLC/candlestick data to HuggingFace Dataset

        Args:
            ohlc_data: List of OHLC data dictionaries
            append: If True, append to existing data; if False, replace

        Returns:
            bool: True if upload successful
        """
        try:
            if not ohlc_data:
                logger.warning("No OHLC data to upload")
                return False

            # Ensure dataset exists
            if not self._ensure_dataset_exists(
                self.ohlc_dataset,
                "Real-time cryptocurrency OHLC/candlestick data from multiple exchanges"
            ):
                return False

            # Add fetched_at timestamp if not present
            current_time = datetime.utcnow().isoformat() + "Z"
            for data in ohlc_data:
                if "fetched_at" not in data:
                    data["fetched_at"] = current_time

            # Convert to pandas DataFrame
            df = pd.DataFrame(ohlc_data)

            # Create HuggingFace Dataset
            dataset = Dataset.from_pandas(df)

            # If append mode, download and combine with existing data
            if append:
                try:
                    from datasets import load_dataset
                    existing_dataset = load_dataset(
                        self.ohlc_dataset,
                        split="train",
                        token=self.token
                    )

                    existing_df = existing_dataset.to_pandas()
                    combined_df = pd.concat([existing_df, df], ignore_index=True)

                    # Remove duplicates based on symbol, interval, and timestamp
                    combined_df = combined_df.drop_duplicates(
                        subset=["symbol", "interval", "timestamp"],
                        keep="last"
                    )

                    dataset = Dataset.from_pandas(combined_df)
                    logger.info(f"Appended {len(df)} new OHLC records to {len(existing_df)} existing records")

                except Exception as e:
                    logger.warning(f"Could not load existing OHLC dataset: {e}")
                    pass

            # Push to hub
            logger.info(f"Uploading {len(dataset)} OHLC records to {self.ohlc_dataset}...")
            dataset.push_to_hub(
                self.ohlc_dataset,
                token=self.token,
                private=False
            )

            logger.info(f"✅ Successfully uploaded OHLC data to {self.ohlc_dataset}")
            logger.info(f"   Records: {len(dataset)}")
            logger.info(f"   Columns: {dataset.column_names}")

            return True

        except Exception as e:
            logger.error(f"Error uploading OHLC data: {e}", exc_info=True)
            return False

    async def upload_news_data(
        self,
        news_data: List[Dict[str, Any]],
        append: bool = True
    ) -> bool:
        """Upload news data to HuggingFace Dataset"""
        try:
            if not news_data:
                return False

            if not self._ensure_dataset_exists(
                self.news_dataset,
                "Real-time cryptocurrency news from multiple sources"
            ):
                return False

            df = pd.DataFrame(news_data)
            dataset = Dataset.from_pandas(df)

            if append:
                try:
                    from datasets import load_dataset
                    existing = load_dataset(self.news_dataset, split="train", token=self.token)
                    existing_df = existing.to_pandas()
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                    combined_df = combined_df.drop_duplicates(subset=["url"], keep="last")
                    dataset = Dataset.from_pandas(combined_df)
                except:
                    pass

            dataset.push_to_hub(self.news_dataset, token=self.token, private=False)
            logger.info(f"✅ Uploaded {len(dataset)} news records to {self.news_dataset}")
            return True
        except Exception as e:
            logger.error(f"Error uploading news data: {e}", exc_info=True)
            return False

    async def upload_sentiment_data(
        self,
        sentiment_data: List[Dict[str, Any]],
        append: bool = True
    ) -> bool:
        """Upload sentiment data to HuggingFace Dataset"""
        try:
            if not sentiment_data:
                return False

            if not self._ensure_dataset_exists(
                self.sentiment_dataset,
                "Cryptocurrency market sentiment indicators from multiple sources"
            ):
                return False

            df = pd.DataFrame(sentiment_data)
            dataset = Dataset.from_pandas(df)

            if append:
                try:
                    from datasets import load_dataset
                    existing = load_dataset(self.sentiment_dataset, split="train", token=self.token)
                    existing_df = existing.to_pandas()
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                    dataset = Dataset.from_pandas(combined_df)
                except:
                    pass

            dataset.push_to_hub(self.sentiment_dataset, token=self.token, private=False)
            logger.info(f"✅ Uploaded {len(dataset)} sentiment records to {self.sentiment_dataset}")
            return True
        except Exception as e:
            logger.error(f"Error uploading sentiment data: {e}", exc_info=True)
            return False

    async def upload_onchain_data(
        self,
        onchain_data: List[Dict[str, Any]],
        append: bool = True
    ) -> bool:
        """Upload on-chain analytics to HuggingFace Dataset"""
        try:
            if not onchain_data:
                return False

            if not self._ensure_dataset_exists(
                self.onchain_dataset,
                "On-chain cryptocurrency analytics and metrics"
            ):
                return False

            df = pd.DataFrame(onchain_data)
            dataset = Dataset.from_pandas(df)

            if append:
                try:
                    from datasets import load_dataset
                    existing = load_dataset(self.onchain_dataset, split="train", token=self.token)
                    existing_df = existing.to_pandas()
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                    dataset = Dataset.from_pandas(combined_df)
                except:
                    pass

            dataset.push_to_hub(self.onchain_dataset, token=self.token, private=False)
            logger.info(f"✅ Uploaded {len(dataset)} on-chain records to {self.onchain_dataset}")
            return True
        except Exception as e:
            logger.error(f"Error uploading on-chain data: {e}", exc_info=True)
            return False

    async def upload_whale_data(
        self,
        whale_data: List[Dict[str, Any]],
        append: bool = True
    ) -> bool:
        """Upload whale transaction data to HuggingFace Dataset"""
        try:
            if not whale_data:
                return False

            if not self._ensure_dataset_exists(
                self.whale_dataset,
                "Large cryptocurrency transactions and whale movements"
            ):
                return False

            df = pd.DataFrame(whale_data)
            dataset = Dataset.from_pandas(df)

            if append:
                try:
                    from datasets import load_dataset
                    existing = load_dataset(self.whale_dataset, split="train", token=self.token)
                    existing_df = existing.to_pandas()
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                    dataset = Dataset.from_pandas(combined_df)
                except:
                    pass

            dataset.push_to_hub(self.whale_dataset, token=self.token, private=False)
            logger.info(f"✅ Uploaded {len(dataset)} whale transaction records to {self.whale_dataset}")
            return True
        except Exception as e:
            logger.error(f"Error uploading whale data: {e}", exc_info=True)
            return False

    async def upload_explorer_data(
        self,
        explorer_data: List[Dict[str, Any]],
        append: bool = True
    ) -> bool:
        """Upload block explorer data to HuggingFace Dataset"""
        try:
            if not explorer_data:
                return False

            if not self._ensure_dataset_exists(
                self.explorer_dataset,
                "Blockchain data from multiple block explorers"
            ):
                return False

            df = pd.DataFrame(explorer_data)
            dataset = Dataset.from_pandas(df)

            if append:
                try:
                    from datasets import load_dataset
                    existing = load_dataset(self.explorer_dataset, split="train", token=self.token)
                    existing_df = existing.to_pandas()
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                    dataset = Dataset.from_pandas(combined_df)
                except:
                    pass

            dataset.push_to_hub(self.explorer_dataset, token=self.token, private=False)
            logger.info(f"✅ Uploaded {len(dataset)} explorer records to {self.explorer_dataset}")
            return True
        except Exception as e:
            logger.error(f"Error uploading explorer data: {e}", exc_info=True)
            return False

    def get_dataset_info(self, dataset_type: str = "market") -> Optional[Dict[str, Any]]:
        """
        Get information about a dataset

        Args:
            dataset_type: "market", "ohlc", "news", "sentiment", "onchain", "whale", or "explorer"

        Returns:
            Dataset information dictionary
        """
        try:
            dataset_map = {
                "market": self.market_data_dataset,
                "ohlc": self.ohlc_dataset,
                "news": self.news_dataset,
                "sentiment": self.sentiment_dataset,
                "onchain": self.onchain_dataset,
                "whale": self.whale_dataset,
                "explorer": self.explorer_dataset
            }

            dataset_name = dataset_map.get(dataset_type, self.market_data_dataset)
            info = self.api.dataset_info(dataset_name, token=self.token)

            return {
                "id": info.id,
                "author": info.author,
                "created_at": str(info.created_at),
                "last_modified": str(info.last_modified),
                "downloads": info.downloads,
                "likes": info.likes,
                "tags": info.tags,
                "private": info.private,
                "url": f"https://huggingface.co/datasets/{dataset_name}"
            }

        except Exception as e:
            logger.error(f"Error getting dataset info: {e}")
            return None


# Singleton instance
_uploader_instance: Optional[HuggingFaceDatasetUploader] = None


def get_dataset_uploader(
    hf_token: Optional[str] = None,
    dataset_namespace: Optional[str] = None
) -> HuggingFaceDatasetUploader:
    """
    Get or create HuggingFace Dataset Uploader singleton instance

    Args:
        hf_token: HuggingFace API token
        dataset_namespace: Dataset namespace

    Returns:
        HuggingFaceDatasetUploader instance
    """
    global _uploader_instance

    if _uploader_instance is None:
        _uploader_instance = HuggingFaceDatasetUploader(
            hf_token=hf_token,
            dataset_namespace=dataset_namespace
        )

    return _uploader_instance


# Testing
if __name__ == "__main__":
    import asyncio

    async def test_uploader():
        """Test the uploader"""
        print("=" * 80)
        print("Testing HuggingFace Dataset Uploader")
        print("=" * 80)

        # Sample market data
        sample_market_data = [
            {
                "symbol": "BTC",
                "price": 45000.50,
                "market_cap": 850000000000.0,
                "volume_24h": 25000000000.0,
                "change_24h": 2.5,
                "high_24h": 45500.0,
                "low_24h": 44000.0,
                "provider": "coingecko",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            {
                "symbol": "ETH",
                "price": 3200.75,
                "market_cap": 380000000000.0,
                "volume_24h": 15000000000.0,
                "change_24h": 3.2,
                "high_24h": 3250.0,
                "low_24h": 3100.0,
                "provider": "coingecko",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        ]

        # Sample OHLC data
        sample_ohlc_data = [
            {
                "symbol": "BTCUSDT",
                "interval": "1h",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "open": 44500.0,
                "high": 45000.0,
                "low": 44300.0,
                "close": 44800.0,
                "volume": 1250000.0,
                "provider": "binance"
            }
        ]

        try:
            # Create uploader
            uploader = get_dataset_uploader()

            # Upload market data
            print("\n📤 Uploading market data...")
            success = await uploader.upload_market_data(sample_market_data)
            print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

            # Upload OHLC data
            print("\n📤 Uploading OHLC data...")
            success = await uploader.upload_ohlc_data(sample_ohlc_data)
            print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

            # Get dataset info
            print("\n📊 Dataset Information:")
            market_info = uploader.get_dataset_info("market")
            if market_info:
                print(f"   Market Data Dataset:")
                print(f"     URL: {market_info['url']}")
                print(f"     Downloads: {market_info['downloads']}")
                print(f"     Likes: {market_info['likes']}")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

    asyncio.run(test_uploader())

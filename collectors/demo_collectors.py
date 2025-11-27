"""
Demonstration Script for All Collector Modules

This script demonstrates the usage of all collector modules and
provides a comprehensive overview of data collection capabilities.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List

# Import all collector functions
from collectors import (
    collect_explorer_data,
    collect_market_data,
    collect_news_data,
    collect_onchain_data,
    collect_sentiment_data,
)


def print_separator(title: str = ""):
    """Print a formatted separator line"""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    else:
        print(f"{'='*70}\n")


def format_result_summary(result: Dict[str, Any]) -> str:
    """Format a single result for display"""
    lines = []
    lines.append(f"Provider: {result.get('provider', 'Unknown')}")
    lines.append(f"Category: {result.get('category', 'Unknown')}")
    lines.append(f"Success: {result.get('success', False)}")

    if result.get("success"):
        lines.append(f"Response Time: {result.get('response_time_ms', 0):.2f}ms")
        staleness = result.get("staleness_minutes")
        if staleness is not None:
            lines.append(f"Data Staleness: {staleness:.2f} minutes")

        # Add provider-specific info
        if result.get("index_value"):
            lines.append(
                f"Fear & Greed Index: {result['index_value']} ({result['index_classification']})"
            )
        if result.get("post_count"):
            lines.append(f"Posts: {result['post_count']}")
        if result.get("article_count"):
            lines.append(f"Articles: {result['article_count']}")
        if result.get("is_placeholder"):
            lines.append("Status: PLACEHOLDER IMPLEMENTATION")
    else:
        lines.append(f"Error Type: {result.get('error_type', 'unknown')}")
        lines.append(f"Error: {result.get('error', 'Unknown error')}")

    return "\n".join(lines)


def print_category_summary(category: str, results: List[Dict[str, Any]]):
    """Print summary for a category of collectors"""
    print_separator(f"{category.upper()}")

    total = len(results)
    successful = sum(1 for r in results if r.get("success", False))

    print(f"Total Collectors: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print()

    for i, result in enumerate(results, 1):
        print(f"[{i}/{total}] {'-'*60}")
        print(format_result_summary(result))
        print()


async def collect_all_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Collect data from all categories concurrently

    Returns:
        Dictionary with categories as keys and results as values
    """
    print_separator("Starting Data Collection from All Sources")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z\n")

    # Run all collectors concurrently
    print("Executing all collectors in parallel...")

    market_results, explorer_results, news_results, sentiment_results, onchain_results = (
        await asyncio.gather(
            collect_market_data(),
            collect_explorer_data(),
            collect_news_data(),
            collect_sentiment_data(),
            collect_onchain_data(),
            return_exceptions=True,
        )
    )

    # Handle any exceptions
    def handle_exception(result, category):
        if isinstance(result, Exception):
            return [
                {
                    "provider": "Unknown",
                    "category": category,
                    "success": False,
                    "error": str(result),
                    "error_type": "exception",
                }
            ]
        return result

    return {
        "market_data": handle_exception(market_results, "market_data"),
        "explorers": handle_exception(explorer_results, "blockchain_explorers"),
        "news": handle_exception(news_results, "news"),
        "sentiment": handle_exception(sentiment_results, "sentiment"),
        "onchain": handle_exception(onchain_results, "onchain_analytics"),
    }


async def main():
    """Main demonstration function"""
    print_separator("Cryptocurrency Data Collector - Comprehensive Demo")

    # Collect all data
    all_results = await collect_all_data()

    # Print results by category
    print_category_summary("Market Data Collection", all_results["market_data"])
    print_category_summary("Blockchain Explorer Data", all_results["explorers"])
    print_category_summary("News Data Collection", all_results["news"])
    print_category_summary("Sentiment Data Collection", all_results["sentiment"])
    print_category_summary("On-Chain Analytics Data", all_results["onchain"])

    # Overall statistics
    print_separator("Overall Collection Statistics")

    total_collectors = sum(len(results) for results in all_results.values())
    total_successful = sum(
        sum(1 for r in results if r.get("success", False)) for results in all_results.values()
    )
    total_failed = total_collectors - total_successful

    # Calculate average response time for successful calls
    response_times = [
        r.get("response_time_ms", 0)
        for results in all_results.values()
        for r in results
        if r.get("success", False) and "response_time_ms" in r
    ]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0

    print(f"Total Collectors Run: {total_collectors}")
    print(f"Successful: {total_successful} ({total_successful/total_collectors*100:.1f}%)")
    print(f"Failed: {total_failed} ({total_failed/total_collectors*100:.1f}%)")
    print(f"Average Response Time: {avg_response_time:.2f}ms")
    print()

    # Category breakdown
    print("By Category:")
    for category, results in all_results.items():
        successful = sum(1 for r in results if r.get("success", False))
        total = len(results)
        print(f"  {category:20} {successful}/{total} successful")

    print_separator()

    # Save results to file
    output_file = f"collector_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(output_file, "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"Results saved to: {output_file}")
    except Exception as e:
        print(f"Failed to save results: {e}")

    print_separator("Demo Complete")

    return all_results


if __name__ == "__main__":
    # Run the demonstration
    results = asyncio.run(main())

    # Exit with appropriate code
    total_collectors = sum(len(r) for r in results.values())
    total_successful = sum(
        sum(1 for item in r if item.get("success", False)) for r in results.values()
    )

    # Exit with 0 if at least 50% successful, else 1
    exit(0 if total_successful >= total_collectors / 2 else 1)

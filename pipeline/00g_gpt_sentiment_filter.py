"""
Step 0G: GPT Sentiment Pre-Filter
Analyzes news and removes high-risk stocks
"""
import json
import sys
import os
from datetime import datetime
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY


def analyze_news_sentiment():
    """Use GPT to filter out risky stocks"""
    print("=" * 60)
    print("STEP 0G: GPT Sentiment Analysis")
    print("=" * 60)

    # Load news
    with open('data/finnhub_news.json', 'r') as f:
        news_data = json.load(f)

    stocks_with_news = news_data['news_data']

    print(f"\nAnalyzing {len(stocks_with_news)} stocks for risk...")

    # Build prompt for GPT
    prompt = """Analyze these stocks for HIGH RISK indicators that make them bad for credit spreads (15-45 days).

REMOVE stocks with:
- Earnings in next 45 days
- FDA decisions pending
- Merger/acquisition rumors
- Major lawsuits or regulatory action
- Severe negative sentiment spike

KEEP stocks with:
- Normal business news
- Stable or improving sentiment
- No major catalysts upcoming

STOCKS & NEWS:
"""

    for ticker, data in list(stocks_with_news.items())[:22]:
        prompt += f"\n{ticker} ({data['article_count']} articles):\n"
        for article in data['articles'][:5]:
            headline = article.get('headline', '')
            prompt += f"  - {headline}\n"

    prompt += """

OUTPUT JSON:
{
  "keep": ["TICKER1", "TICKER2"...],
  "remove": {
    "TICKER3": "earnings in 12 days",
    "TICKER4": "merger rumors"
  }
}
"""

    # Call GPT via Responses API (reasoning is supported here)
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.responses.create(
        # Use the reasoning-capable model you have access to; adjust if needed
        model="gpt-5.1",  # or "gpt-5.1-thinking" if that's the actual model name on your account
        input=[
            {
                "role": "system",
                "content": "You filter stocks for credit spread safety. Output JSON only."
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        reasoning={
            "effort": "medium"
        },
        text={
            "verbosity": "low"
        }
    )

    # In the Responses API, use the helper to get the text
    # (if your installed openai version doesn't support `output_text`,
    # you may need to inspect `response.output` manually).
    content = getattr(response, "output_text", None)
    if not content or not content.strip():
        raise RuntimeError(
            f"Model returned empty content. Raw response object: {response}"
        )

    # Parse response
    try:
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            json_str = content[start:end]
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            json_str = content[start:end]
        else:
            json_str = content

        result = json.loads(json_str)

        keep_tickers = result.get('keep', [])
        remove_tickers = result.get('remove', {})

        print(f"\n✅ GPT Analysis Complete:")
        print(f"   Keep: {len(keep_tickers)} stocks")
        print(f"   Remove: {len(remove_tickers)} stocks")

        if remove_tickers:
            print(f"\n   Removed:")
            for ticker, reason in remove_tickers.items():
                print(f"      {ticker}: {reason}")

        # Update stocks.py with filtered list
        with open('data/stocks.py', 'w') as f:
            f.write(f"# Filtered by sentiment analysis: {datetime.now()}\n")
            f.write(f"STOCKS = {keep_tickers}\n\n")
            f.write(f"REMOVED_STOCKS = {remove_tickers}\n")

        print(f"\n✅ Updated data/stocks.py with {len(keep_tickers)} safe stocks")

    except Exception as e:
        print(f"❌ Parse error: {e}")
        print(f"Raw content from model:\n{content!r}")
        print("Keeping all stocks as fallback")


if __name__ == "__main__":
    analyze_news_sentiment()
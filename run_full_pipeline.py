#!/usr/bin/env python3
"""
Master Pipeline Runner - Complete Data Flow
"""
import subprocess
import sys
import time
from datetime import datetime

def run_step(step_name, script_path, description):
    print("\n" + "="*80)
    print(f"▶ {step_name}: {description}")
    print("="*80)
    
    start = time.time()
    result = subprocess.run([sys.executable, script_path], text=True)
    elapsed = time.time() - start
    
    if result.returncode == 0:
        print(f"\n✅ {step_name} complete ({elapsed:.1f}s)")
        return True
    else:
        print(f"\n❌ {step_name} FAILED ({elapsed:.1f}s)")
        return False

def main():
    print("\n" + "█"*80)
    print("█" + "  CREDIT SPREAD FINDER - FULL PIPELINE".center(78) + "█")
    print("█" + f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(78) + "█")
    print("█"*80)
    
    start = time.time()
    
    steps = [
        ("00A", "pipeline/00a_get_sp500.py", "Get S&P 500 tickers"),
        ("00B", "pipeline/00b_filter_price.py", "Filter by price & spread"),
        ("00C", "pipeline/00c_filter_options.py", "Filter by options chains"),
        ("00D", "pipeline/00d_filter_iv.py", "Filter by IV range"),
        ("00E", "pipeline/00e_select_22.py", "Score & select top 22"),
        ("00F", "pipeline/00f_get_news.py", "Fetch news headlines"),
        ("00G", "pipeline/00g_gpt_sentiment_filter.py", "GPT sentiment filter"),
        ("01", "pipeline/01_get_prices.py", "Get real-time prices"),
        ("02", "pipeline/02_get_chains.py", "Get options chains"),
        ("03", "pipeline/03_check_liquidity.py", "Check liquidity"),
        ("04", "pipeline/04_get_greeks.py", "Collect Greeks"),
        ("05", "pipeline/05_calculate_spreads.py", "Calculate spreads"),
        ("06", "pipeline/06_rank_spreads.py", "Rank by score"),
        ("07", "pipeline/07_build_report.py", "Build report table"),
        ("08", "pipeline/08_gpt_analysis.py", "GPT 5W1H analysis"),
        ("09", "pipeline/09_format_trades.py", "Format final trades")
    ]
    
    completed = 0
    for step_name, script, desc in steps:
        if run_step(step_name, script, desc):
            completed += 1
            time.sleep(0.3)
        else:
            break
    
    elapsed = time.time() - start
    print("\n" + "="*80)
    print(f"{'✅ COMPLETE' if completed == len(steps) else '❌ STOPPED'}: {completed}/{len(steps)} ({elapsed:.1f}s)")
    print("="*80)

if __name__ == "__main__":
    main()

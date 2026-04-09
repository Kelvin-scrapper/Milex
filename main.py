"""
SIPRI Military Expenditure Pipeline — Entry Point
===================================================
Runs the full pipeline:
  1. scraper.scrape()  — downloads the SIPRI Excel workbook
  2. map.scrape()      — converts it to MILEX_DATA format, saves DATA/META/ZIP

Usage:
  python main.py
"""

import time
import scraper
import map


def main():
    print("=" * 55)
    print("  SIPRI MILEX Data Pipeline")
    print("=" * 55)

    # Step 1 — Download
    print("\n[Step 1] Downloading SIPRI source file...")
    downloaded = scraper.scrape()
    if not downloaded:
        print("[ERROR] Download failed — aborting pipeline")
        return

    # Brief pause to ensure the file is fully flushed to disk
    time.sleep(3)

    # Step 2 — Map & package
    print("\n[Step 2] Mapping and packaging output...")
    data_path, meta_path, zip_path = map.scrape()

    print("\n" + "=" * 55)
    if zip_path:
        print(f"  Pipeline complete")
        print(f"  DATA : {data_path}")
        print(f"  META : {meta_path}")
        print(f"  ZIP  : {zip_path}")
    else:
        print("  Pipeline finished with errors — check logs above")
    print("=" * 55)


if __name__ == "__main__":
    main()

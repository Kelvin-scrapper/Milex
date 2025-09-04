
'''
This script orchestrates the downloading and processing of the SIPRI Military Expenditure Database.
'''

import main
import map
import time

def run_orchestrator():
    """
    Runs the full download and processing pipeline.
    """
    print("Starting the SIPRI data pipeline...")
    
    # Step 1: Download the data
    print("\n--- Running Downloader ---")
    main.main()
    print("--- Downloader Finished ---\n")
    
    # Give a moment for the file to be fully saved
    time.sleep(5)
    
    # Step 2: Process the downloaded data
    print("--- Running Data Mapper ---")
    map.main()
    print("--- Data Mapper Finished ---\n")
    
    print("SIPRI data pipeline completed successfully.")

if __name__ == "__main__":
    run_orchestrator()

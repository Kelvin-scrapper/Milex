import pandas as pd
import os

# Hardcoded column headers - exact order from MILEX_DATA_20250429 (country columns only)
HARDCODED_COUNTRY_COLUMNS = [
    'DZA.MILEX.A', 'LBY.MILEX.A', 'MAR.MILEX.A', 'TUN.MILEX.A', 'AGO.MILEX.A', 'BEN.MILEX.A', 
    'BWA.MILEX.A', 'BFA.MILEX.A', 'BDI.MILEX.A', 'CMR.MILEX.A', 'CPV.MILEX.A', 'CAF.MILEX.A',
    'TCD.MILEX.A', 'COD.MILEX.A', 'COG.MILEX.A', 'CIV.MILEX.A', 'DJI.MILEX.A', 'GNQ.MILEX.A',
    'ERI.MILEX.A', 'ETH.MILEX.A', 'GAB.MILEX.A', 'GMB.MILEX.A', 'GHA.MILEX.A', 'GIN.MILEX.A',
    'GNB.MILEX.A', 'KEN.MILEX.A', 'LSO.MILEX.A', 'LBR.MILEX.A', 'MDG.MILEX.A', 'MWI.MILEX.A',
    'MLI.MILEX.A', 'MRT.MILEX.A', 'MUS.MILEX.A', 'MOZ.MILEX.A', 'NAM.MILEX.A', 'NER.MILEX.A',
    'NGA.MILEX.A', 'RWA.MILEX.A', 'SEN.MILEX.A', 'SYC.MILEX.A', 'SLE.MILEX.A', 'SOM.MILEX.A',
    'ZAF.MILEX.A', 'SSD.MILEX.A', 'SDN.MILEX.A', 'SWZ.MILEX.A', 'TZA.MILEX.A', 'TGO.MILEX.A',
    'UGA.MILEX.A', 'ZMB.MILEX.A', 'ZWE.MILEX.A', 'BLZ.MILEX.A', 'CRI.MILEX.A', 'CUB.MILEX.A',
    'DOM.MILEX.A', 'SLV.MILEX.A', 'GTM.MILEX.A', 'HTI.MILEX.A', 'HND.MILEX.A', 'JAM.MILEX.A',
    'MEX.MILEX.A', 'NIC.MILEX.A', 'PAN.MILEX.A', 'TTO.MILEX.A', 'CAN.MILEX.A', 'USA.MILEX.A',
    'ARG.MILEX.A', 'BOL.MILEX.A', 'BRA.MILEX.A', 'CHL.MILEX.A', 'COL.MILEX.A', 'ECU.MILEX.A',
    'GUY.MILEX.A', 'PRY.MILEX.A', 'PER.MILEX.A', 'URY.MILEX.A', 'VEN.MILEX.A', 'AUS.MILEX.A',
    'FJI.MILEX.A', 'NZL.MILEX.A', 'PNG.MILEX.A', 'AFG.MILEX.A', 'BGD.MILEX.A', 'IND.MILEX.A',
    'NPL.MILEX.A', 'PAK.MILEX.A', 'LKA.MILEX.A', 'CHN.MILEX.A', 'JPN.MILEX.A', 'PRK.MILEX.A',
    'KOR.MILEX.A', 'MNG.MILEX.A', 'TWN.MILEX.A', 'BRN.MILEX.A', 'KHM.MILEX.A', 'IDN.MILEX.A',
    'LAO.MILEX.A', 'MYS.MILEX.A', 'MMR.MILEX.A', 'PHL.MILEX.A', 'SGP.MILEX.A', 'THA.MILEX.A',
    'TLS.MILEX.A', 'VNM.MILEX.A', 'KAZ.MILEX.A', 'KGZ.MILEX.A', 'TJK.MILEX.A', 'TKM.MILEX.A',
    'UZB.MILEX.A', 'ALB.MILEX.A', 'BIH.MILEX.A', 'BGR.MILEX.A', 'HRV.MILEX.A', 'CZE.MILEX.A',
    'CZSL.MILEX.A', 'EST.MILEX.A', 'GDR.MILEX.A', 'HUN.MILEX.A', 'XKX.MILEX.A', 'LVA.MILEX.A',
    'LTU.MILEX.A', 'MKD.MILEX.A', 'MNE.MILEX.A', 'POL.MILEX.A', 'ROU.MILEX.A', 'SRB.MILEX.A',
    'SVK.MILEX.A', 'SVN.MILEX.A', 'YUSL.MILEX.A', 'ARM.MILEX.A', 'AZE.MILEX.A', 'BLR.MILEX.A',
    'GEO.MILEX.A', 'MDA.MILEX.A', 'RUS.MILEX.A', 'UKR.MILEX.A', 'USSR.MILEX.A', 'AUT.MILEX.A',
    'BEL.MILEX.A', 'CYP.MILEX.A', 'DNK.MILEX.A', 'FIN.MILEX.A', 'FRA.MILEX.A', 'DEU.MILEX.A',
    'GRC.MILEX.A', 'ISL.MILEX.A', 'IRL.MILEX.A', 'ITA.MILEX.A', 'LUX.MILEX.A', 'MLT.MILEX.A',
    'NLD.MILEX.A', 'NOR.MILEX.A', 'PRT.MILEX.A', 'ESP.MILEX.A', 'SWE.MILEX.A', 'CHE.MILEX.A',
    'GBR.MILEX.A', 'BHR.MILEX.A', 'EGY.MILEX.A', 'IRN.MILEX.A', 'IRQ.MILEX.A', 'ISR.MILEX.A',
    'JOR.MILEX.A', 'KWT.MILEX.A', 'LBN.MILEX.A', 'OMN.MILEX.A', 'QAT.MILEX.A', 'SAU.MILEX.A',
    'SYR.MILEX.A', 'TUR.MILEX.A', 'ARE.MILEX.A', 'YMD.MILEX.A', 'YEM.MILEX.A'
]

# Country code mapping (ISO 3-letter codes to country names) - for flexible matching
COUNTRY_CODE_MAP = {
    'DZA': 'Algeria', 'LBY': 'Libya', 'MAR': 'Morocco', 'TUN': 'Tunisia',
    'AGO': 'Angola', 'BEN': 'Benin', 'BWA': 'Botswana', 'BFA': 'Burkina Faso',
    'BDI': 'Burundi', 'CMR': 'Cameroon', 'CPV': 'Cape Verde', 'CAF': 'Central African Republic',
    'TCD': 'Chad', 'COD': 'Democratic Republic of the Congo', 'COG': 'Republic of the Congo',
    'CIV': 'Côte d\'Ivoire', 'DJI': 'Djibouti', 'GNQ': 'Equatorial Guinea',
    'ERI': 'Eritrea', 'ETH': 'Ethiopia', 'GAB': 'Gabon', 'GMB': 'Gambia',
    'GHA': 'Ghana', 'GIN': 'Guinea', 'GNB': 'Guinea-Bissau', 'KEN': 'Kenya',
    'LSO': 'Lesotho', 'LBR': 'Liberia', 'MDG': 'Madagascar', 'MWI': 'Malawi',
    'MLI': 'Mali', 'MRT': 'Mauritania', 'MUS': 'Mauritius', 'MOZ': 'Mozambique',
    'NAM': 'Namibia', 'NER': 'Niger', 'NGA': 'Nigeria', 'RWA': 'Rwanda',
    'SEN': 'Senegal', 'SYC': 'Seychelles', 'SLE': 'Sierra Leone', 'SOM': 'Somalia',
    'ZAF': 'South Africa', 'SSD': 'South Sudan', 'SDN': 'Sudan', 'SWZ': 'Eswatini',
    'TZA': 'Tanzania', 'TGO': 'Togo', 'UGA': 'Uganda', 'ZMB': 'Zambia', 'ZWE': 'Zimbabwe',
    'BLZ': 'Belize', 'CRI': 'Costa Rica', 'CUB': 'Cuba', 'DOM': 'Dominican Republic',
    'SLV': 'El Salvador', 'GTM': 'Guatemala', 'HTI': 'Haiti', 'HND': 'Honduras',
    'JAM': 'Jamaica', 'MEX': 'Mexico', 'NIC': 'Nicaragua', 'PAN': 'Panama',
    'TTO': 'Trinidad and Tobago', 'CAN': 'Canada', 'USA': 'United States of America',
    'ARG': 'Argentina', 'BOL': 'Bolivia', 'BRA': 'Brazil', 'CHL': 'Chile',
    'COL': 'Colombia', 'ECU': 'Ecuador', 'GUY': 'Guyana', 'PRY': 'Paraguay',
    'PER': 'Peru', 'URY': 'Uruguay', 'VEN': 'Venezuela', 'AUS': 'Australia',
    'FJI': 'Fiji', 'NZL': 'New Zealand', 'PNG': 'Papua New Guinea',
    'AFG': 'Afghanistan', 'BGD': 'Bangladesh', 'IND': 'India', 'NPL': 'Nepal',
    'PAK': 'Pakistan', 'LKA': 'Sri Lanka', 'CHN': 'China', 'JPN': 'Japan',
    'PRK': 'North Korea', 'KOR': 'Korea, South', 'MNG': 'Mongolia', 'TWN': 'Taiwan',
    'BRN': 'Brunei', 'KHM': 'Cambodia', 'IDN': 'Indonesia', 'LAO': 'Laos',
    'MYS': 'Malaysia', 'MMR': 'Myanmar', 'PHL': 'Philippines', 'SGP': 'Singapore',
    'THA': 'Thailand', 'TLS': 'Timor-Leste', 'VNM': 'Vietnam',
    'KAZ': 'Kazakhstan', 'KGZ': 'Kyrgyzstan', 'TJK': 'Tajikistan',
    'TKM': 'Turkmenistan', 'UZB': 'Uzbekistan', 'ALB': 'Albania',
    'BIH': 'Bosnia and Herzegovina', 'BGR': 'Bulgaria', 'HRV': 'Croatia',
    'CZE': 'Czech Republic', 'CZSL': 'Czechoslovakia', 'EST': 'Estonia', 'GDR': 'East Germany', 
    'HUN': 'Hungary', 'XKX': 'Kosovo', 'LVA': 'Latvia', 'LTU': 'Lithuania', 
    'MKD': 'North Macedonia', 'MNE': 'Montenegro', 'POL': 'Poland', 'ROU': 'Romania', 
    'SRB': 'Serbia', 'SVK': 'Slovakia', 'SVN': 'Slovenia', 'YUSL': 'Yugoslavia',
    'ARM': 'Armenia', 'AZE': 'Azerbaijan', 'BLR': 'Belarus', 'GEO': 'Georgia', 
    'MDA': 'Moldova', 'RUS': 'Russia', 'UKR': 'Ukraine', 'USSR': 'Soviet Union',
    'AUT': 'Austria', 'BEL': 'Belgium', 'CYP': 'Cyprus', 'DNK': 'Denmark', 
    'FIN': 'Finland', 'FRA': 'France', 'DEU': 'Germany', 'GRC': 'Greece', 
    'ISL': 'Iceland', 'IRL': 'Ireland', 'ITA': 'Italy', 'LUX': 'Luxembourg', 
    'MLT': 'Malta', 'NLD': 'Netherlands', 'NOR': 'Norway', 'PRT': 'Portugal', 
    'ESP': 'Spain', 'SWE': 'Sweden', 'CHE': 'Switzerland', 'GBR': 'United Kingdom',
    'BHR': 'Bahrain', 'EGY': 'Egypt', 'IRN': 'Iran', 'IRQ': 'Iraq', 'ISR': 'Israel',
    'JOR': 'Jordan', 'KWT': 'Kuwait', 'LBN': 'Lebanon', 'OMN': 'Oman', 'QAT': 'Qatar',
    'SAU': 'Saudi Arabia', 'SYR': 'Syria', 'TUR': 'Turkey', 'ARE': 'United Arab Emirates',
    'YMD': 'Yemen Democratic', 'YEM': 'Yemen'
}

def get_country_code(country_name):
    """Find the 3-letter code for a country name"""
    # Direct lookup
    for code, name in COUNTRY_CODE_MAP.items():
        if country_name.lower() == name.lower():
            return code
    
    # Partial match
    for code, name in COUNTRY_CODE_MAP.items():
        if country_name.lower() in name.lower() or name.lower() in country_name.lower():
            return code
    
    return None

def find_excel_files(directory):
    """
    Recursively find all Excel files in directory and subdirectories
    """
    excel_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.xlsx', '.xls')) and not file.startswith('~'):  # Ignore temp files
                excel_files.append(os.path.join(root, file))
    return excel_files

def read_milex_data():
    """
    Reads the SIPRI Military Expenditure Database Excel file and processes the 'Current US$' sheet
    Scans current directory and subdirectories for Excel files
    """
    # Scan current directory and subdirectories for Excel files
    current_dir = os.getcwd()
    excel_files = find_excel_files(current_dir)
    
    if not excel_files:
        print("No Excel files found in current directory and subdirectories")
        return None
    
    print(f"Found {len(excel_files)} Excel file(s):")
    for i, file in enumerate(excel_files, 1):
        rel_path = os.path.relpath(file, current_dir)
        print(f"  {i}. {rel_path}")
    
    # Look for SIPRI source files, avoiding our own output files
    sipri_file = None
    
    # First, look for SIPRI source files
    for file in excel_files:
        filename = os.path.basename(file).lower()
        # Skip our own output files
        if 'milex_data_' in filename and '_mapped' in filename:
            continue
        if 'milex_data_output' in filename:
            continue
            
        # Look for SIPRI source indicators
        if any(keyword in filename for keyword in ['sipri', 'milex-data', 'military']):
            sipri_file = file
            break
    
    # If no SIPRI file found, look in downloads folder specifically
    if not sipri_file:
        for file in excel_files:
            if 'downloads' in file.lower() and not ('milex_data_' in os.path.basename(file).lower()):
                sipri_file = file
                break
    
    # Final fallback - use first non-output file
    if not sipri_file:
        for file in excel_files:
            filename = os.path.basename(file).lower()
            if not ('milex_data_' in filename and '_mapped' in filename):
                sipri_file = file
                break
    
    # Last resort
    if not sipri_file and excel_files:
        sipri_file = excel_files[0]
    
    excel_file = sipri_file
    rel_path = os.path.relpath(excel_file, current_dir)
    print(f"Using Excel file: {rel_path}")
    
    try:
        # Read all sheet names first
        xl_file = pd.ExcelFile(excel_file)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        # Look for the "Current US$" sheet
        current_usd_sheet = None
        for sheet_name in xl_file.sheet_names:
            if "Current US$" in sheet_name or "current us$" in sheet_name.lower():
                current_usd_sheet = sheet_name
                break
        
        if not current_usd_sheet:
            print("Could not find 'Current US$' sheet. Available sheets:")
            for sheet in xl_file.sheet_names:
                print(f"  - {sheet}")
            # Use first sheet as fallback
            current_usd_sheet = xl_file.sheet_names[0]
            print(f"Using first sheet as fallback: {current_usd_sheet}")
        
        # Read the specific sheet and dynamically detect the header structure
        print(f"Reading sheet: {current_usd_sheet}")
        
        # First, read raw data to find the header row
        df_raw = pd.read_excel(excel_file, sheet_name=current_usd_sheet)
        
        # Find the header row (look for 'Country' in first column and years in subsequent columns)
        header_row_idx = None
        detected_years = []
        
        for i in range(min(10, len(df_raw))):  # Check first 10 rows
            row = df_raw.iloc[i]
            first_col = str(row.iloc[0]).strip().lower()
            
            if 'country' in first_col:
                # Check if this row has years in subsequent columns
                years_in_row = []
                for j in range(1, len(row)):
                    cell = row.iloc[j]
                    if isinstance(cell, (int, float)) and not pd.isna(cell):
                        year = int(cell)
                        if 1900 <= year <= 2100:  # Reasonable year range
                            years_in_row.append(year)
                    elif isinstance(cell, str) and cell.isdigit():
                        year = int(cell)
                        if 1900 <= year <= 2100:
                            years_in_row.append(year)
                
                if len(years_in_row) >= 10:  # Must have at least 10 years to be a valid header
                    header_row_idx = i
                    detected_years = years_in_row
                    break
        
        if header_row_idx is None:
            print("Could not find header row with years, using default row 4")
            header_row_idx = 4
        
        print(f"Found header at row {header_row_idx}")
        
        # Get the actual header values from the detected row
        header_values = df_raw.iloc[header_row_idx].values
        
        print(f"Detected header values: {list(header_values[:5])}...{list(header_values[-5:])}")
        
        # Read the data starting from after the header row, but include one extra row to align properly
        df = pd.read_excel(excel_file, sheet_name=current_usd_sheet, skiprows=header_row_idx+1)
        
        # Ensure we have the right number of columns and apply header values
        if len(header_values) <= len(df.columns):
            # Use only the columns that have corresponding headers
            df = df.iloc[:, :len(header_values)]
            df.columns = header_values
            print(f"Applied {len(header_values)} header values to data columns")
        else:
            print(f"Header has more values ({len(header_values)}) than data columns ({len(df.columns)})")
            # Pad with NaN columns if needed
            for i in range(len(df.columns), len(header_values)):
                df[f'Extra_{i}'] = None
            df.columns = header_values
        
        print(f"Applied header columns: {list(df.columns[:5])}...{list(df.columns[-5:])}")
        
        # Build the column structure dynamically
        # Process each column and build lists of columns to keep vs skip
        columns_to_keep = []
        new_column_names = []
        year_columns = []
        
        for i, col in enumerate(df.columns):
            if i == 0 and ('country' in str(col).lower() or pd.isna(col)):
                columns_to_keep.append(i)
                new_column_names.append('Country')
            elif isinstance(col, (int, float)) and not pd.isna(col):
                year = int(col)
                if 1900 <= year <= 2100:
                    columns_to_keep.append(i)
                    new_column_names.append(year)
                    year_columns.append(year)
                else:
                    print(f"Skipping non-year column at position {i}: {col}")
            elif isinstance(col, str):
                if col.isdigit():
                    year = int(col)
                    if 1900 <= year <= 2100:
                        columns_to_keep.append(i)
                        new_column_names.append(year)
                        year_columns.append(year)
                    else:
                        print(f"Skipping non-year column at position {i}: {col}")
                elif 'note' in col.lower():
                    print(f"Skipping notes column at position {i}: {col}")
                    # Don't add to columns_to_keep - this column will be dropped
                else:
                    print(f"Skipping unknown column at position {i}: {col}")
            else:
                print(f"Skipping unrecognized column at position {i}: {col}")
        
        # Keep only the columns we want using specific column indices
        df = df.iloc[:, columns_to_keep]
        df.columns = new_column_names
        
        if year_columns:
            min_year = min(year_columns)
            max_year = max(year_columns)
            print(f"Successfully mapped columns: Country + {len(year_columns)} years ({min_year}-{max_year})")
        else:
            print("Error: No year columns detected in the data!")
            print("This may not be a SIPRI military expenditure data file.")
            return None
        
        # Remove any empty rows at the beginning
        df = df.dropna(subset=['Country'])
        df = df[df['Country'] != '']
        df = df[df['Country'].notna()]
        
        print(f"Data shape after cleaning: {df.shape}")
        print(f"Column headers: {list(df.columns[:10])}...")  # Show first 10
        print("\nFirst few rows:")
        if len(year_columns) >= 5:
            recent_years = year_columns[-5:]  # Last 5 years
            print(df[['Country'] + recent_years].head())
            
            # Debug: Check USA data specifically
            print("\n=== DEBUG USA DATA ===")
            usa_rows = df[df['Country'].str.contains('United States', na=False)]
            if len(usa_rows) > 0:
                usa_row = usa_rows.iloc[0]
                print("USA data for last 5 years:")
                for year in recent_years:
                    value = usa_row[year]
                    print(f"  {year}: {value}")
        else:
            print(df.head())
        
        return df, current_usd_sheet, excel_file
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def create_country_mapping(df):
    """
    Creates a mapping of countries and their military expenditure data
    """
    if df is None:
        return None
    
    # Assuming the first column contains country names
    # and subsequent columns contain years with expenditure data
    
    country_column = df.columns[0]  # First column (usually country names)
    year_columns = df.columns[1:]   # Remaining columns (usually years)
    
    print(f"\nCountry column: {country_column}")
    print(f"Year columns: {list(year_columns)}")
    
    # Create mapping dictionary
    country_mapping = {}
    
    for index, row in df.iterrows():
        country = row[country_column]
        if pd.notna(country) and country != '':  # Skip empty country names
            country_data = {}
            for year_col in year_columns:
                value = row[year_col]
                if pd.notna(value):
                    country_data[str(year_col)] = value
            
            if country_data:  # Only add if country has data
                country_mapping[country] = country_data
    
    return country_mapping

def display_mapping_summary(mapping):
    """
    Displays a summary of the country mapping
    """
    if not mapping:
        print("No mapping data available")
        return
    
    print(f"\n=== MILITARY EXPENDITURE MAPPING SUMMARY ===")
    print(f"Total countries: {len(mapping)}")
    
    # Get years available
    all_years = set()
    for country_data in mapping.values():
        all_years.update(country_data.keys())
    
    years_list = sorted(all_years)
    print(f"Years covered: {min(years_list)} - {max(years_list)}")
    print(f"Total years: {len(years_list)}")
    
    print(f"\nFirst 10 countries:")
    for i, (country, data) in enumerate(list(mapping.items())[:10]):
        latest_year = max(data.keys()) if data else "N/A"
        latest_value = data.get(latest_year, "N/A") if data else "N/A"
        print(f"  {i+1}. {country}: Latest data ({latest_year}): {latest_value}")
    
    return years_list

def get_country_data(mapping, country_name):
    """
    Gets military expenditure data for a specific country
    """
    if not mapping or country_name not in mapping:
        print(f"No data found for country: {country_name}")
        return None
    
    country_data = mapping[country_name]
    print(f"\n=== MILITARY EXPENDITURE DATA FOR {country_name.upper()} ===")
    
    for year, value in sorted(country_data.items()):
        print(f"{year}: {value}")
    
    return country_data

def get_year_data(mapping, year):
    """
    Gets military expenditure data for all countries in a specific year
    """
    if not mapping:
        print("No mapping data available")
        return None
    
    year_str = str(year)
    year_data = {}
    
    for country, country_data in mapping.items():
        if year_str in country_data:
            year_data[country] = country_data[year_str]
    
    if not year_data:
        print(f"No data found for year: {year}")
        return None
    
    print(f"\n=== MILITARY EXPENDITURE DATA FOR {year} ===")
    # Sort by expenditure value (descending)
    sorted_data = sorted(year_data.items(), key=lambda x: float(x[1]) if isinstance(x[1], (int, float)) else 0, reverse=True)
    
    for i, (country, value) in enumerate(sorted_data[:20], 1):  # Show top 20
        print(f"{i:2d}. {country}: {value}")
    
    return year_data

def create_milex_format(df):
    """
    Creates the exact MILEX_DATA format matching MILEX_DATA_20250429 structure
    Uses hardcoded country column order for consistency
    """
    if df is None:
        return None
    
    print("Creating MILEX_DATA format with hardcoded column order...")
    
    # Get years from source data dynamically
    year_columns = [col for col in df.columns if isinstance(col, int)]
    years = sorted(year_columns)
    
    print(f"Processing years: {min(years)} to {max(years)}")
    
    # Create the result dataframe with years as rows and countries as columns
    result_data = []
    
    # Create the header row with country names (using hardcoded order) - will be handled separately
    header_row = [None]  # First column is empty in header
    
    # Create country name mapping for headers
    for country_column in HARDCODED_COUNTRY_COLUMNS:
        country_code = country_column.split('.')[0]
        country_name = COUNTRY_CODE_MAP.get(country_code, country_code)
        header_row.append(f"Military expenditure, {country_name}")
    
    # Don't append header_row to result_data - it will be handled when saving to Excel
    
    # Create a lookup dictionary for source data (country name -> row data)
    source_data_lookup = {}
    for index, row in df.iterrows():
        country_name = row['Country']
        if pd.notna(country_name) and country_name != '' and country_name != 'Country':
            source_data_lookup[country_name] = row
    
    # Add data rows for each year
    for year in years:
        year_row = [float(year)]  # First column is the year
        
        # For each hardcoded country column, get the data for this year
        for country_column in HARDCODED_COUNTRY_COLUMNS:
            country_code = country_column.split('.')[0]
            expected_country_names = [COUNTRY_CODE_MAP.get(country_code, '')]
            
            # Find matching country in source data with flexible matching
            value = 0  # Default value
            found = False
            
            for src_country_name, src_row in source_data_lookup.items():
                # Try different matching strategies
                matched = False
                
                # Direct country code match
                if get_country_code(src_country_name) == country_code:
                    matched = True
                
                # Alternative name matching for special cases
                if not matched:
                    src_lower = src_country_name.lower()
                    expected_lower = expected_country_names[0].lower()
                    
                    if (src_lower in expected_lower or expected_lower in src_lower or
                        # Special cases
                        (country_code == 'TUR' and 'türkiye' in src_lower) or
                        (country_code == 'CIV' and 'ivoire' in src_lower) or
                        (country_code == 'COD' and 'congo' in src_lower and 'democratic' in src_lower) or
                        (country_code == 'COG' and 'congo' in src_lower and 'republic' in src_lower and 'democratic' not in src_lower)):
                        matched = True
                
                if matched:
                    if year in src_row.index:
                        cell_value = src_row[year]
                        if pd.notna(cell_value) and cell_value != '...' and cell_value != 'xxx' and cell_value != '':
                            try:
                                value = float(cell_value)
                                found = True
                            except (ValueError, TypeError):
                                value = 0
                    break
            
            # Suppress verbose "not found" messages for cleaner output
            # Only show warnings for recent years when data should exist
            if not found and country_code not in ['YMD', 'YUSL', 'USSR', 'GDR', 'CZSL'] and year >= 2020:
                print(f"Warning: No recent data for {country_code} ({COUNTRY_CODE_MAP.get(country_code, country_code)}) in {year}")
            
            year_row.append(value)
        
        result_data.append(year_row)
    
    # Create DataFrame with hardcoded column structure
    # Insert header row at the beginning
    all_data = [header_row] + result_data
    columns = ['Unnamed: 0'] + HARDCODED_COUNTRY_COLUMNS
    result_df = pd.DataFrame(all_data, columns=columns)
    
    print(f"Created MILEX format with shape: {result_df.shape}")
    print(f"Countries: {len(HARDCODED_COUNTRY_COLUMNS)}")
    print(f"Years: {len(years)}")
    
    return result_df

def save_milex_format(df, source_file_path=None):
    """
    Saves the MILEX format data to Excel file with dynamic naming
    """
    if df is None:
        print("No data to save")
        return
    
    # Generate dynamic filename based on source file or current date
    from datetime import datetime
    
    if source_file_path:
        # Extract base name from source file
        source_base = os.path.splitext(os.path.basename(source_file_path))[0]
        # Clean up the name
        clean_name = source_base.replace('SIPRI-', '').replace('Milex-', '').replace('data-', '')
        filename = f"MILEX_DATA_{clean_name}_MAPPED.xlsx"
    else:
        # Use current date as fallback
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"MILEX_DATA_{current_date}_MAPPED.xlsx"
    
    filepath = os.path.join(os.getcwd(), filename)
    
    # Handle file conflicts
    counter = 1
    original_filepath = filepath
    while os.path.exists(filepath):
        name_part = os.path.splitext(original_filepath)[0]
        ext_part = os.path.splitext(original_filepath)[1]
        filepath = f"{name_part}_{counter}{ext_part}"
        counter += 1
    
    try:
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='DATA', index=False)
        
        print(f"MILEX format data saved to: {os.path.basename(filepath)}")
        return filepath
    
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def main():
    """
    Main function to create MILEX_DATA format from SIPRI data
    """
    print("SIPRI to MILEX_DATA Format Converter")
    print("=" * 50)
    
    # Read the SIPRI Excel file
    result = read_milex_data()
    if not result:
        return None, None
    
    df, sheet_name, source_file_path = result
    
    # Create MILEX format
    milex_df = create_milex_format(df)
    
    if milex_df is not None:
        # Save to file with dynamic naming based on source file
        output_file = save_milex_format(milex_df, source_file_path)
        
        # Display sample data
        print(f"\n=== SAMPLE OUTPUT (First 5 rows, First 10 columns) ===")
        sample_cols = milex_df.columns[:10] if len(milex_df.columns) >= 10 else milex_df.columns
        print(milex_df[sample_cols].head())
        
        # Show some statistics
        numeric_cols = [col for col in milex_df.columns if col != 'Unnamed: 0']
        if len(numeric_cols) > 0 and len(milex_df) > 1:
            print(f"\n=== STATISTICS ===")
            print(f"Total countries: {len(numeric_cols)}")
            print(f"Years covered: 1949-2024")
            
            # Show top countries for latest year (2024)
            latest_year_data = milex_df.iloc[-1]  # Last row is 2024
            country_values = []
            for i, col in enumerate(numeric_cols):
                if i < len(latest_year_data) - 1:  # Skip year column
                    value = latest_year_data.iloc[i + 1]  # +1 to skip year column
                    if pd.notna(value) and value > 0:
                        country_code = col.split('.')[0]
                        country_name = COUNTRY_CODE_MAP.get(country_code, country_code)
                        country_values.append((country_name, value))
            
            # Sort by expenditure and show top 10
            country_values.sort(key=lambda x: x[1], reverse=True)
            print(f"\n=== TOP 10 MILITARY SPENDERS IN 2024 ===")
            for i, (country, value) in enumerate(country_values[:10], 1):
                print(f"{i:2d}. {country}: ${value:,.0f} million")
    
    return milex_df, output_file

if __name__ == "__main__":
    milex_df, output_file = main()
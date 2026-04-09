"""
SIPRI Military Expenditure — Data Mapper
==========================================
Dataset : MILEX
Input   : downloads/SIPRI-Milex-data-*.xlsx  (raw SIPRI workbook)
Output  : output/MILEX_DATA_{YYYYMMDD}.xlsx
          output/MILEX_META_{YYYYMMDD}.xlsx
          output/MILEX_{YYYYMMDD}.ZIP
Usage   : python map.py
"""

import io
import zipfile
import pandas as pd
import numpy as np
import os
import openpyxl
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATASET_CODE  = "MILEX"
OUTPUT_PREFIX = "MILEX"
SHEET_NAME    = "DATA"
YEAR_COL      = "Year"
SIPRI_SHEET   = "Current US$"       # target sheet in SIPRI source workbook
OUTPUT_DIR    = "output"            # all output files go here
SOURCE_DIR    = "downloads"         # where scraper.py places the raw file

# ISO codes for dissolved/historical states — expected to have no recent data
HISTORICAL_CODES = frozenset({'YMD', 'YUSL', 'USSR', 'GDR', 'CZSL'})

# Country columns in the fixed output order (ISO code + descriptor)
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

# ISO 3-letter code -> canonical country name
COUNTRY_CODE_MAP = {
    'DZA': 'Algeria', 'LBY': 'Libya', 'MAR': 'Morocco', 'TUN': 'Tunisia',
    'AGO': 'Angola', 'BEN': 'Benin', 'BWA': 'Botswana', 'BFA': 'Burkina Faso',
    'BDI': 'Burundi', 'CMR': 'Cameroon', 'CPV': 'Cape Verde', 'CAF': 'Central African Republic',
    'TCD': 'Chad', 'COD': 'Democratic Republic of the Congo', 'COG': 'Republic of the Congo',
    'CIV': "Côte d'Ivoire", 'DJI': 'Djibouti', 'GNQ': 'Equatorial Guinea',
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
    'CZE': 'Czech Republic', 'CZSL': 'Czechoslovakia', 'EST': 'Estonia',
    'GDR': 'East Germany', 'HUN': 'Hungary', 'XKX': 'Kosovo', 'LVA': 'Latvia',
    'LTU': 'Lithuania', 'MKD': 'North Macedonia', 'MNE': 'Montenegro', 'POL': 'Poland',
    'ROU': 'Romania', 'SRB': 'Serbia', 'SVK': 'Slovakia', 'SVN': 'Slovenia',
    'YUSL': 'Yugoslavia', 'ARM': 'Armenia', 'AZE': 'Azerbaijan', 'BLR': 'Belarus',
    'GEO': 'Georgia', 'MDA': 'Moldova', 'RUS': 'Russia', 'UKR': 'Ukraine',
    'USSR': 'Soviet Union', 'AUT': 'Austria', 'BEL': 'Belgium', 'CYP': 'Cyprus',
    'DNK': 'Denmark', 'FIN': 'Finland', 'FRA': 'France', 'DEU': 'Germany',
    'GRC': 'Greece', 'ISL': 'Iceland', 'IRL': 'Ireland', 'ITA': 'Italy',
    'LUX': 'Luxembourg', 'MLT': 'Malta', 'NLD': 'Netherlands', 'NOR': 'Norway',
    'PRT': 'Portugal', 'ESP': 'Spain', 'SWE': 'Sweden', 'CHE': 'Switzerland',
    'GBR': 'United Kingdom', 'BHR': 'Bahrain', 'EGY': 'Egypt', 'IRN': 'Iran',
    'IRQ': 'Iraq', 'ISR': 'Israel', 'JOR': 'Jordan', 'KWT': 'Kuwait',
    'LBN': 'Lebanon', 'OMN': 'Oman', 'QAT': 'Qatar', 'SAU': 'Saudi Arabia',
    'SYR': 'Syria', 'TUR': 'Turkey', 'ARE': 'United Arab Emirates',
    'YMD': 'Yemen Democratic', 'YEM': 'Yemen'
}

# Aliases for fuzzy source-name matching (lowercased source name -> ISO code)
_NAME_ALIASES = {
    'türkiye': 'TUR',
    'turkey': 'TUR',
    "côte d'ivoire": 'CIV',
    "cote d'ivoire": 'CIV',
    'ivory coast': 'CIV',
    'congo, dr': 'COD',                          # SIPRI exact name
    'democratic republic of the congo': 'COD',
    'dr congo': 'COD',
    'congo, democratic republic': 'COD',
    'congo (democratic republic)': 'COD',
    'congo-kinshasa': 'COD',
    'republic of the congo': 'COG',
    'congo, republic': 'COG',                    # SIPRI exact name
    'congo-brazzaville': 'COG',
    'south korea': 'KOR',
    'korea, south': 'KOR',
    'korea, republic of': 'KOR',
    'north korea': 'PRK',
    'korea, north': 'PRK',
    "korea, democratic people's republic of": 'PRK',
    'united states': 'USA',
    'united states of america': 'USA',
    'russia': 'RUS',
    'russian federation': 'RUS',
    'iran': 'IRN',
    'iran, islamic republic of': 'IRN',
    'syria': 'SYR',
    'syrian arab republic': 'SYR',
    'vietnam': 'VNM',
    'viet nam': 'VNM',
    'tanzania': 'TZA',
    'united republic of tanzania': 'TZA',
    'moldova': 'MDA',
    'republic of moldova': 'MDA',
    'laos': 'LAO',
    "lao people's democratic republic": 'LAO',
    'bolivia': 'BOL',
    'plurinational state of bolivia': 'BOL',
    'venezuela': 'VEN',
    'bolivarian republic of venezuela': 'VEN',
    'eswatini': 'SWZ',
    'swaziland': 'SWZ',
    'timor leste': 'TLS',                        # SIPRI exact name (no hyphen)
    'timor-leste': 'TLS',
    'east timor': 'TLS',
    'north macedonia': 'MKD',
    'former yugoslav republic of macedonia': 'MKD',
    'czech republic': 'CZE',
    'czechia': 'CZE',
    'czechoslovakia': 'CZSL',
    'yugoslavia': 'YUSL',
    'soviet union': 'USSR',
    'ussr': 'USSR',
    'east germany': 'GDR',
    'german democratic republic': 'GDR',
    'gambia, the': 'GMB',                        # SIPRI exact name
    'the gambia': 'GMB',
    'kyrgyz republic': 'KGZ',                   # SIPRI exact name
    'kyrgyzstan': 'KGZ',
    't\u00fcrkiye': 'TUR',                       # SIPRI encoding variant of Türkiye
    'south sudan': 'SSD',
    'guinea-bissau': 'GNB',
    'equatorial guinea': 'GNQ',
    'cape verde': 'CPV',
    'cabo verde': 'CPV',
    'myanmar': 'MMR',
    'burma': 'MMR',
}

# Build reverse map: canonical name (lowercased) -> ISO code
_CANONICAL_LOWER = {name.lower(): code for code, name in COUNTRY_CODE_MAP.items()}


def resolve_iso(country_name: str) -> str | None:
    """Resolve a source country name to an ISO code. Returns None if not found."""
    key = country_name.strip().lower()
    # 1. Alias lookup (covers variants, special chars, alternate names)
    if key in _NAME_ALIASES:
        return _NAME_ALIASES[key]
    # 2. Canonical name exact match
    if key in _CANONICAL_LOWER:
        return _CANONICAL_LOWER[key]
    # 3. No match — do NOT fall through to substring matching (causes false positives)
    return None


def _parse_period(year: int) -> str:
    """Convert an integer year to the YYYY period string."""
    return str(year)


def _find_excel_files(directory: str) -> list[str]:
    """Recursively find all non-temporary Excel files, skipping the output folder."""
    output_path = os.path.normpath(os.path.join(directory, OUTPUT_DIR))
    files = []
    for root, dirs, names in os.walk(directory):
        # Skip the output folder so we never pick up our own generated files
        dirs[:] = [d for d in dirs if os.path.normpath(os.path.join(root, d)) != output_path]
        for name in names:
            if name.endswith(('.xlsx', '.xls')) and not name.startswith('~'):
                files.append(os.path.join(root, name))
    return files


def _safe_float(value) -> float:
    """Strip commas/symbols and return float. Returns NaN for missing/invalid values."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, str) and value.strip().lower() in MISSING_PLACEHOLDERS:
        return np.nan
    try:
        return float(str(value).replace(',', ''))
    except (ValueError, TypeError):
        return np.nan


def _load_source():
    """
    Locates the SIPRI Excel file, finds the 'Current US$' sheet, detects the
    header row dynamically, and returns a clean DataFrame with columns
    ['Country', year1, year2, ...].
    """
    current_dir = os.getcwd()
    excel_files = _find_excel_files(current_dir)

    if not excel_files:
        print("No Excel files found in current directory and subdirectories")
        return None

    print(f"Found {len(excel_files)} Excel file(s):")
    for i, f in enumerate(excel_files, 1):
        print(f"  {i}. {os.path.relpath(f, current_dir)}")

    # Pick the SIPRI source file (skip our own output files)
    sipri_file = None
    for f in excel_files:
        base = os.path.basename(f).lower()
        if '_mapped' in base or 'milex_data_output' in base:
            continue
        if any(kw in base for kw in ['sipri', 'milex-data', 'military']) or 'downloads' in f.lower():
            sipri_file = f
            break
    if not sipri_file:
        # fallback: first non-output file
        for f in excel_files:
            if '_mapped' not in os.path.basename(f).lower():
                sipri_file = f
                break
    if not sipri_file:
        sipri_file = excel_files[0]

    print(f"Using: {os.path.relpath(sipri_file, current_dir)}")

    try:
        xl = pd.ExcelFile(sipri_file)
        print(f"Sheets: {xl.sheet_names}")

        # Find the target sheet (Current US$), fall back to first sheet
        target_sheet = next(
            (s for s in xl.sheet_names if SIPRI_SHEET.lower() in s.lower()),
            xl.sheet_names[0]
        )
        print(f"Reading sheet: {target_sheet}")

        # Read raw to detect header row (row with 'Country' + year integers)
        raw = pd.read_excel(sipri_file, sheet_name=target_sheet, header=None)

        header_idx = None
        for i in range(min(15, len(raw))):
            row = raw.iloc[i]
            first = str(row.iloc[0]).strip().lower()
            if 'country' not in first:
                continue
            years_found = sum(
                1 for v in row.iloc[1:]
                if (isinstance(v, (int, float)) and not pd.isna(v) and 1900 <= int(v) <= 2100)
                or (isinstance(v, str) and v.isdigit() and 1900 <= int(v) <= 2100)
            )
            if years_found >= 10:
                header_idx = i
                break

        if header_idx is None:
            print("Warning: could not detect header row, defaulting to row 4")
            header_idx = 4

        print(f"Header row detected at index {header_idx}")

        # Read with detected header
        df = pd.read_excel(sipri_file, sheet_name=target_sheet, header=header_idx)

        # Rename first column to 'Country'
        df.rename(columns={df.columns[0]: 'Country'}, inplace=True)

        # Keep only Country + integer year columns; drop notes/unknown columns
        year_cols = []
        cols_to_keep = ['Country']
        for col in df.columns[1:]:
            if isinstance(col, (int, float)) and not pd.isna(col) and 1900 <= int(col) <= 2100:
                year = int(col)
                df.rename(columns={col: year}, inplace=True)
                cols_to_keep.append(year)
                year_cols.append(year)
            elif isinstance(col, str) and col.strip().isdigit():
                year = int(col.strip())
                if 1900 <= year <= 2100:
                    df.rename(columns={col: year}, inplace=True)
                    cols_to_keep.append(year)
                    year_cols.append(year)
            # else: silently drop notes/unknown columns

        df = df[cols_to_keep].copy()

        # Drop rows with no country name or header-repetition rows
        df = df[df['Country'].notna()]
        df = df[df['Country'].astype(str).str.strip() != '']
        df = df[df['Country'].astype(str).str.lower() != 'country']
        df = df.reset_index(drop=True)

        if not year_cols:
            print("Error: no year columns detected — is this a SIPRI expenditure file?")
            return None

        print(f"Loaded {len(df)} countries, years {min(year_cols)}-{max(year_cols)}")
        return df, target_sheet, sipri_file

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None


def _build_iso_lookup(df: pd.DataFrame) -> dict:
    """
    Build a dict: ISO code -> pandas Series (one row of source data).
    Iterates source countries once — O(n).
    Warns on duplicate matches so ambiguity is visible.
    """
    lookup = {}
    unmatched = []

    for _, row in df.iterrows():
        name = str(row['Country']).strip()
        if not name or name.lower() == 'country':
            continue
        iso = resolve_iso(name)
        if iso:
            if iso in lookup:
                print(f"  Duplicate match for {iso}: '{name}' vs existing '{lookup[iso]['Country']}' — keeping first")
            else:
                lookup[iso] = row
        else:
            unmatched.append(name)

    if unmatched:
        print(f"\nUnmatched source countries ({len(unmatched)}) — no ISO code found:")
        for n in unmatched:
            print(f"  - {n}")

    print(f"\nISO lookup built: {len(lookup)} countries matched")
    return lookup


MISSING_PLACEHOLDERS = frozenset({'...', 'xxx', 'x', 'n/a', 'na', '', 'none'})


def _extract_data(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Produces a DataFrame in the MILEX_DATA format:
      - Index: integer years
      - Columns: HARDCODED_COUNTRY_COLUMNS (e.g. 'DZA.MILEX.A')
      - Row 0 (header label row): 'Military expenditure, <Country Name>'
      - Rows 1+: numeric expenditure values (NaN where no data)
    """
    if df is None:
        return None

    year_cols = sorted(c for c in df.columns if isinstance(c, int))
    if not year_cols:
        print("Error: no year columns in source data")
        return None

    print(f"\nBuilding MILEX format: {len(HARDCODED_COUNTRY_COLUMNS)} countries × {len(year_cols)} years "
          f"({min(year_cols)}-{max(year_cols)})")

    # Build source lookup once — O(n)
    iso_lookup = _build_iso_lookup(df)

    # --- Header label row ---
    header = {col: f"Military expenditure, {COUNTRY_CODE_MAP.get(col.split('.')[0], col.split('.')[0])}"
              for col in HARDCODED_COUNTRY_COLUMNS}
    header_row = pd.Series(header, name='label').reindex(HARDCODED_COUNTRY_COLUMNS)

    # --- Data rows: one per year ---
    data_rows = {}
    missing_recent = []

    for year in year_cols:
        row = {}
        for col in HARDCODED_COUNTRY_COLUMNS:
            iso = col.split('.')[0]
            if iso in iso_lookup:
                src_row = iso_lookup[iso]
                row[col] = _safe_float(src_row.get(year, np.nan))
            else:
                row[col] = np.nan
        data_rows[year] = row

    result = pd.DataFrame(data_rows, index=HARDCODED_COUNTRY_COLUMNS).T
    result.index.name = YEAR_COL
    # Enforce fixed column order — pandas can silently reorder when building from dicts
    result = result.reindex(columns=HARDCODED_COUNTRY_COLUMNS)

    # Warn about countries with no recent data (last 5 years)
    recent_years = year_cols[-5:]
    for col in HARDCODED_COUNTRY_COLUMNS:
        iso = col.split('.')[0]
        # Skip dissolved states
        if iso in HISTORICAL_CODES:
            continue
        if iso not in iso_lookup:
            missing_recent.append(iso)
        else:
            recent_vals = [_safe_float(iso_lookup[iso].get(y, np.nan)) for y in recent_years]
            if all(np.isnan(v) for v in recent_vals):
                missing_recent.append(iso)

    if missing_recent:
        print(f"\nCountries with no data in last 5 years ({len(missing_recent)}):")
        for iso in missing_recent:
            print(f"  - {iso} ({COUNTRY_CODE_MAP.get(iso, iso)})")

    print(f"\nMILEX format shape: {result.shape}")
    return result, header_row


def _save_data(result_df: pd.DataFrame, header_row: pd.Series, run_date: str) -> str | None:
    """
    Write DATA Excel file.
    Structure:
      Row 1 (col headers): Year | DZA.MILEX.A | LBY.MILEX.A | ...
      Row 2 (label row):   ''  | Military expenditure, Algeria | ...
      Row 3+:              1949 | 0.0 | 123.4 | ...
    Numeric cells get comma number format (#,##0.##).
    Returns the saved filepath.
    """
    if result_df is None:
        print("No data to save")
        return None

    output_folder = os.path.join(os.getcwd(), OUTPUT_DIR)
    os.makedirs(output_folder, exist_ok=True)
    filepath = os.path.join(output_folder, f"{OUTPUT_PREFIX}_DATA_{run_date}.xlsx")

    counter = 1
    stem = os.path.splitext(filepath)[0]
    while os.path.exists(filepath):
        filepath = f"{stem}_{counter}.xlsx"
        counter += 1

    try:
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Row 1: column header (Year + country codes)
            label_df = pd.DataFrame([header_row], columns=HARDCODED_COUNTRY_COLUMNS)
            label_df.insert(0, YEAR_COL, '')
            label_df.to_excel(writer, sheet_name=SHEET_NAME, index=False, startrow=0)

            # Rows 2+: year data
            data_out = result_df.reset_index()
            data_out = data_out[[YEAR_COL] + HARDCODED_COUNTRY_COLUMNS]
            data_out.to_excel(writer, sheet_name=SHEET_NAME, index=False,
                              startrow=1, header=False)

        # Apply comma number format to all numeric data cells (skip header rows)
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active
        for row in ws.iter_rows(min_row=3, min_col=2):
            for cell in row:
                if isinstance(cell.value, (int, float)):
                    cell.number_format = '#,##0.##'
        wb.save(filepath)

        print(f"DATA saved: {os.path.basename(filepath)}")
        return filepath

    except Exception as e:
        print(f"[ERROR] _save_data: {e}")
        return None


def _save_metadata(run_date: str) -> str | None:
    """
    Write META Excel file with one row per country timeseries.
    Returns the saved filepath.
    """
    output_folder = os.path.join(os.getcwd(), OUTPUT_DIR)
    os.makedirs(output_folder, exist_ok=True)
    filepath = os.path.join(output_folder, f"{OUTPUT_PREFIX}_META_{run_date}.xlsx")

    rows = []
    for col in HARDCODED_COUNTRY_COLUMNS:
        iso = col.split('.')[0]
        name = COUNTRY_CODE_MAP.get(iso, iso)
        rows.append({
            "CODE":              col,
            "DESCRIPTION":       f"Military expenditure, {name}",
            "FREQUENCY":         "Annual",
            "UNIT":              "USD millions (current prices)",
            "SOURCE_NAME":       "SIPRI Military Expenditure Database",
            "SOURCE_URL":        "https://www.sipri.org/databases/milex",
            "DATASET":           DATASET_CODE,
            "NEXT_RELEASE_DATE": "",
        })

    try:
        pd.DataFrame(rows).to_excel(filepath, index=False)
        print(f"META saved: {os.path.basename(filepath)}")
        return filepath
    except Exception as e:
        print(f"[ERROR] _save_metadata: {e}")
        return None


def _create_zip(data_path: str, meta_path: str, run_date: str) -> str | None:
    """
    Package DATA and META files into {OUTPUT_PREFIX}_{YYYYMMDD}.ZIP.
    Returns the zip filepath.
    """
    output_folder = os.path.join(os.getcwd(), OUTPUT_DIR)
    zip_path = os.path.join(output_folder, f"{OUTPUT_PREFIX}_{run_date}.ZIP")

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            if data_path and os.path.exists(data_path):
                zf.write(data_path, os.path.basename(data_path))
            if meta_path and os.path.exists(meta_path):
                zf.write(meta_path, os.path.basename(meta_path))
        print(f"ZIP created: {os.path.basename(zip_path)}")
        return zip_path
    except Exception as e:
        print(f"[ERROR] _create_zip: {e}")
        return None


def scrape() -> tuple:
    """
    Run the full mapping pipeline:
      _load_source → _extract_data → _save_data → _save_metadata → _create_zip
    Returns (data_path, meta_path, zip_path).
    """
    print(f"\n{'='*50}")
    print(f"SIPRI Military Expenditure Mapper — {DATASET_CODE}")
    print(f"{'='*50}")

    result = _load_source()
    if not result:
        return None, None, None

    df, sheet_name, source_file_path = result

    milex_result = _extract_data(df)
    if milex_result is None:
        return None, None, None

    result_df, header_row = milex_result
    run_date = datetime.now().strftime('%Y%m%d')

    data_path = _save_data(result_df, header_row, run_date)
    meta_path = _save_metadata(run_date)
    zip_path  = _create_zip(data_path, meta_path, run_date)

    if result_df is not None:
        years = result_df.index.tolist()
        print(f"\n=== SUMMARY ===")
        print(f"Countries : {len(result_df.columns)}")
        print(f"Years     : {min(years)}-{max(years)} ({len(years)} total)")

        for latest_year in reversed(years):
            ranked = result_df.loc[latest_year].dropna().sort_values(ascending=False)
            if ranked.empty:
                continue
            print(f"\n=== TOP 10 MILITARY SPENDERS IN {latest_year} ===")
            for i, (col, val) in enumerate(ranked.head(10).items(), 1):
                iso  = col.split('.')[0]
                name = COUNTRY_CODE_MAP.get(iso, iso)
                print(f"  {i:2d}. {name}: ${val:,.0f} million")
            break

    return data_path, meta_path, zip_path


def main():
    """Entry point. Supports --all flag (reserved for future backfill)."""
    data_path, meta_path, zip_path = scrape()
    if zip_path:
        print(f"\nDone — {zip_path}")
    else:
        print("\n[ERROR] Mapping failed — check logs above")


if __name__ == "__main__":
    main()

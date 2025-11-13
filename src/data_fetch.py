"""
Fetch U.S. Treasury yield curve data from FRED API.

This module handles downloading daily/monthly Treasury yield data for various
maturities and saving it to CSV format.
"""

import os
import pandas as pd
from datetime import datetime
from fredapi import Fred
import warnings

warnings.filterwarnings('ignore')


# FRED series IDs for U.S. Treasury yields
FRED_SERIES = {
    '1M': 'DGS1MO',
    '3M': 'DGS3MO',
    '6M': 'DGS6MO',
    '1Y': 'DGS1',
    '2Y': 'DGS2',
    '3Y': 'DGS3',
    '5Y': 'DGS5',
    '7Y': 'DGS7',
    '10Y': 'DGS10',
    '20Y': 'DGS20',
    '30Y': 'DGS30',
}


def fetch_yield_data(api_key: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    Fetch U.S. Treasury yield data from FRED API.
    
    Parameters:
    -----------
    api_key : str
        FRED API key (get from https://fred.stlouisfed.org/docs/api/api_key.html)
    start_date : str, optional
        Start date in 'YYYY-MM-DD' format
    end_date : str, optional
        End date in 'YYYY-MM-DD' format
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with dates as index and maturities as columns
    """
    if api_key is None:
        raise ValueError(
            "FRED API key required. Get one from https://fred.stlouisfed.org/docs/api/api_key.html"
        )
    
    fred = Fred(api_key=api_key)
    yield_data = {}
    
    print("Fetching yield curve data from FRED...")
    for maturity, series_id in FRED_SERIES.items():
        try:
            print(f"  Fetching {maturity} yield ({series_id})...")
            data = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
            yield_data[maturity] = data
        except Exception as e:
            print(f"  Warning: Failed to fetch {maturity} ({series_id}): {e}")
            continue
    
    if not yield_data:
        raise ValueError("No yield data could be fetched from FRED")
    
    # Combine into DataFrame
    df = pd.DataFrame(yield_data)
    df.index.name = 'Date'
    
    # Remove rows where all values are NaN
    df = df.dropna(how='all')
    
    print(f"\nFetched {len(df)} observations across {len(df.columns)} maturities")
    print(f"Date range: {df.index.min()} to {df.index.max()}")
    
    return df


def save_yield_data(df: pd.DataFrame, output_path: str) -> None:
    """
    Save yield data to CSV file.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Yield data DataFrame
    output_path : str
        Path to save CSV file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path)
    print(f"Saved yield data to {output_path}")


def load_yield_data(input_path: str) -> pd.DataFrame:
    """
    Load yield data from CSV file.
    
    Parameters:
    -----------
    input_path : str
        Path to CSV file
    
    Returns:
    --------
    pd.DataFrame
        Yield data DataFrame with Date as index
    """
    df = pd.read_csv(input_path, index_col=0, parse_dates=True)
    return df


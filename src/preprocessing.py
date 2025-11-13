"""
Preprocess and clean yield curve data for PCA analysis.

This module handles data alignment, missing value imputation, and standardization.
"""

import pandas as pd
import numpy as np
from typing import Tuple


def align_maturities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure all maturities are present and in correct order.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw yield data
    
    Returns:
    --------
    pd.DataFrame
        Aligned yield data
    """
    expected_maturities = ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
    
    # Reorder columns to match expected order
    available_maturities = [m for m in expected_maturities if m in df.columns]
    df = df[available_maturities]
    
    return df


def handle_missing_data(df: pd.DataFrame, method: str = 'forward_fill') -> pd.DataFrame:
    """
    Handle missing values in yield data.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Yield data with potential missing values
    method : str
        Method for handling missing data:
        - 'forward_fill': Forward fill missing values
        - 'interpolate': Linear interpolation
        - 'drop': Drop rows with any missing values
    
    Returns:
    --------
    pd.DataFrame
        Cleaned yield data
    """
    if method == 'forward_fill':
        df = df.ffill().bfill()
    elif method == 'interpolate':
        df = df.interpolate(method='linear', limit_direction='both')
        # If still missing at edges, forward/backward fill
        df = df.ffill().bfill()
    elif method == 'drop':
        df = df.dropna()
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return df


def standardize_yields(df: pd.DataFrame, method: str = 'demean') -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """
    Standardize yield data for PCA.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Yield data
    method : str
        Standardization method:
        - 'demean': Subtract mean (center only)
        - 'zscore': Z-score normalization (center and scale)
    
    Returns:
    --------
    Tuple[pd.DataFrame, np.ndarray, np.ndarray]
        Standardized data, means, and stds (if applicable)
    """
    if method == 'demean':
        means = df.mean().values
        df_standardized = df - means
        stds = np.ones_like(means)
    elif method == 'zscore':
        means = df.mean().values
        stds = df.std().values
        df_standardized = (df - means) / stds
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return df_standardized, means, stds


def preprocess_yield_data(
    df: pd.DataFrame,
    handle_missing: str = 'forward_fill',
    standardize: str = 'demean'
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """
    Complete preprocessing pipeline for yield curve data.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw yield data
    handle_missing : str
        Method for handling missing data
    standardize : str
        Standardization method
    
    Returns:
    --------
    Tuple[pd.DataFrame, np.ndarray, np.ndarray]
        Preprocessed data, means, and stds
    """
    print("Preprocessing yield curve data...")
    
    # Align maturities
    df = align_maturities(df)
    print(f"  Aligned {len(df.columns)} maturities")
    
    # Handle missing data
    initial_rows = len(df)
    df = handle_missing_data(df, method=handle_missing)
    final_rows = len(df)
    print(f"  Handled missing data: {initial_rows} -> {final_rows} rows")
    
    # Standardize
    df_standardized, means, stds = standardize_yields(df, method=standardize)
    print(f"  Standardized using method: {standardize}")
    
    return df_standardized, means, stds


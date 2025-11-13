"""
Unit tests for preprocessing module.
"""

import pytest
import pandas as pd
import numpy as np
from src.preprocessing import (
    align_maturities,
    handle_missing_data,
    standardize_yields,
    preprocess_yield_data
)


@pytest.fixture
def sample_yield_data():
    """Create sample yield data for testing."""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    data = {
        '1M': np.random.uniform(0.5, 2.0, 100),
        '3M': np.random.uniform(0.6, 2.1, 100),
        '6M': np.random.uniform(0.7, 2.2, 100),
        '1Y': np.random.uniform(0.8, 2.3, 100),
        '2Y': np.random.uniform(1.0, 2.5, 100),
        '10Y': np.random.uniform(1.5, 3.0, 100),
        '30Y': np.random.uniform(2.0, 3.5, 100),
    }
    df = pd.DataFrame(data, index=dates)
    return df


def test_align_maturities(sample_yield_data):
    """Test maturity alignment."""
    df_aligned = align_maturities(sample_yield_data)
    
    # Check that columns are in expected order
    expected_order = ['1M', '3M', '6M', '1Y', '2Y', '10Y', '30Y']
    assert list(df_aligned.columns) == expected_order
    assert len(df_aligned) == len(sample_yield_data)


def test_handle_missing_data_forward_fill(sample_yield_data):
    """Test forward fill missing data handling."""
    # Introduce missing values
    df_with_nan = sample_yield_data.copy()
    df_with_nan.loc[df_with_nan.index[10:20], '1Y'] = np.nan
    
    df_cleaned = handle_missing_data(df_with_nan, method='forward_fill')
    
    # Check no NaN values remain
    assert df_cleaned['1Y'].isna().sum() == 0
    assert len(df_cleaned) == len(df_with_nan)


def test_handle_missing_data_interpolate(sample_yield_data):
    """Test interpolation missing data handling."""
    df_with_nan = sample_yield_data.copy()
    df_with_nan.loc[df_with_nan.index[10:20], '1Y'] = np.nan
    
    df_cleaned = handle_missing_data(df_with_nan, method='interpolate')
    
    assert df_cleaned['1Y'].isna().sum() == 0


def test_handle_missing_data_drop(sample_yield_data):
    """Test drop missing data handling."""
    df_with_nan = sample_yield_data.copy()
    df_with_nan.loc[df_with_nan.index[10:20], '1Y'] = np.nan
    
    df_cleaned = handle_missing_data(df_with_nan, method='drop')
    
    # Should have fewer rows
    assert len(df_cleaned) < len(df_with_nan)
    assert df_cleaned['1Y'].isna().sum() == 0


def test_standardize_yields_demean(sample_yield_data):
    """Test demeaning standardization."""
    df_std, means, stds = standardize_yields(sample_yield_data, method='demean')
    
    # Check means are approximately zero
    assert np.allclose(df_std.mean().values, 0, atol=1e-10)
    
    # Check means shape
    assert len(means) == len(sample_yield_data.columns)
    assert len(stds) == len(sample_yield_data.columns)
    
    # Check stds are all 1 for demean
    assert np.allclose(stds, 1.0)


def test_standardize_yields_zscore(sample_yield_data):
    """Test z-score standardization."""
    df_std, means, stds = standardize_yields(sample_yield_data, method='zscore')
    
    # Check means are approximately zero
    assert np.allclose(df_std.mean().values, 0, atol=1e-10)
    
    # Check stds are approximately one
    assert np.allclose(df_std.std().values, 1.0, atol=1e-10)


def test_preprocess_yield_data(sample_yield_data):
    """Test complete preprocessing pipeline."""
    df_processed, means, stds = preprocess_yield_data(sample_yield_data)
    
    # Check output shapes
    assert df_processed.shape == sample_yield_data.shape
    assert len(means) == len(sample_yield_data.columns)
    assert len(stds) == len(sample_yield_data.columns)
    
    # Check no NaN values
    assert df_processed.isna().sum().sum() == 0
    
    # Check standardized (mean should be close to zero)
    assert np.allclose(df_processed.mean().values, 0, atol=1e-10)


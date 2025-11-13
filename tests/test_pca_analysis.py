"""
Unit tests for PCA analysis module.
"""

import pytest
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from src.pca_analysis import (
    apply_pca,
    interpret_components,
    compute_pca_results
)


@pytest.fixture
def sample_processed_data():
    """Create sample preprocessed yield data for testing."""
    dates = pd.date_range('2020-01-01', periods=200, freq='D')
    n_maturities = 7
    
    # Create correlated data (simulating yield curve)
    np.random.seed(42)
    base_level = np.random.randn(200)
    slope = np.linspace(-1, 1, n_maturities)
    
    data = {}
    for i, maturity in enumerate(['1M', '3M', '6M', '1Y', '2Y', '10Y', '30Y']):
        # Create data with level and slope components
        data[maturity] = base_level + slope[i] * np.random.randn(200) * 0.5
    
    df = pd.DataFrame(data, index=dates)
    
    # Standardize
    df = (df - df.mean()) / df.std()
    
    return df


def test_apply_pca(sample_processed_data):
    """Test PCA application."""
    n_components = 3
    pca, loadings, scores = apply_pca(sample_processed_data, n_components=n_components)
    
    # Check PCA model
    assert isinstance(pca, PCA)
    assert pca.n_components == n_components
    
    # Check loadings shape
    assert loadings.shape == (len(sample_processed_data.columns), n_components)
    assert list(loadings.index) == list(sample_processed_data.columns)
    assert list(loadings.columns) == [f'PC{i+1}' for i in range(n_components)]
    
    # Check scores shape
    assert scores.shape == (len(sample_processed_data), n_components)
    assert len(scores.index) == len(sample_processed_data.index)
    assert list(scores.columns) == [f'PC{i+1}' for i in range(n_components)]


def test_apply_pca_explained_variance(sample_processed_data):
    """Test that explained variance is reasonable."""
    pca, loadings, scores = apply_pca(sample_processed_data, n_components=3)
    
    # Explained variance should be between 0 and 1
    assert np.all(pca.explained_variance_ratio_ >= 0)
    assert np.all(pca.explained_variance_ratio_ <= 1)
    
    # First component should explain most variance
    assert pca.explained_variance_ratio_[0] > pca.explained_variance_ratio_[1]
    assert pca.explained_variance_ratio_[1] > pca.explained_variance_ratio_[2]
    
    # Cumulative variance should be <= 1
    assert np.sum(pca.explained_variance_ratio_) <= 1.0


def test_interpret_components(sample_processed_data):
    """Test component interpretation."""
    pca, loadings, scores = apply_pca(sample_processed_data, n_components=3)
    interpretations = interpret_components(loadings)
    
    # Should have interpretation for each component
    assert len(interpretations) == 3
    assert 'PC1' in interpretations
    assert 'PC2' in interpretations
    assert 'PC3' in interpretations
    
    # Interpretations should be strings
    assert all(isinstance(v, str) for v in interpretations.values())


def test_compute_pca_results(sample_processed_data):
    """Test complete PCA results computation."""
    results = compute_pca_results(sample_processed_data, n_components=3)
    
    # Check all required keys
    required_keys = ['pca_model', 'loadings', 'scores', 'explained_variance',
                    'cumulative_variance', 'interpretations']
    assert all(key in results for key in required_keys)
    
    # Check types
    assert isinstance(results['pca_model'], PCA)
    assert isinstance(results['loadings'], pd.DataFrame)
    assert isinstance(results['scores'], pd.DataFrame)
    assert isinstance(results['explained_variance'], np.ndarray)
    assert isinstance(results['cumulative_variance'], np.ndarray)
    assert isinstance(results['interpretations'], dict)
    
    # Check shapes
    assert results['loadings'].shape[0] == len(sample_processed_data.columns)
    assert results['scores'].shape[0] == len(sample_processed_data)
    assert len(results['explained_variance']) == 3
    assert len(results['cumulative_variance']) == 3


def test_pca_dimensional_integrity(sample_processed_data):
    """Test that PCA maintains dimensional integrity."""
    pca, loadings, scores = apply_pca(sample_processed_data, n_components=3)
    
    # Reconstruct approximation
    reconstructed = scores @ loadings.T
    
    # Should have same shape as original
    assert reconstructed.shape == sample_processed_data.shape
    
    # Reconstruction error should be reasonable
    reconstruction_error = np.mean((sample_processed_data.values - reconstructed.values) ** 2)
    assert reconstruction_error < 1.0  # Should be small for standardized data


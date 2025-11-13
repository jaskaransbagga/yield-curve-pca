"""
Perform Principal Component Analysis on yield curve data.

This module applies PCA to identify the main factors driving yield curve changes:
level, slope, and curvature.
"""

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from typing import Tuple, Dict


def apply_pca(
    df: pd.DataFrame,
    n_components: int = 3,
    random_state: int = 42
) -> Tuple[PCA, pd.DataFrame, pd.DataFrame]:
    """
    Apply PCA to yield curve data.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Preprocessed yield data (standardized)
    n_components : int
        Number of principal components to compute
    random_state : int
        Random state for reproducibility
    
    Returns:
    --------
    Tuple[PCA, pd.DataFrame, pd.DataFrame]
        PCA model, component loadings (as DataFrame), and component scores (as DataFrame)
    """
    print(f"\nApplying PCA with {n_components} components...")
    
    # Fit PCA
    pca = PCA(n_components=n_components, random_state=random_state)
    scores = pca.fit_transform(df.values)
    
    # Create loadings DataFrame (components as rows, maturities as columns)
    loadings = pd.DataFrame(
        pca.components_.T,
        index=df.columns,
        columns=[f'PC{i+1}' for i in range(n_components)]
    )
    
    # Create scores DataFrame (dates as index, components as columns)
    scores_df = pd.DataFrame(
        scores,
        index=df.index,
        columns=[f'PC{i+1}' for i in range(n_components)]
    )
    
    # Print explained variance
    explained_variance = pca.explained_variance_ratio_
    print(f"\nExplained Variance:")
    for i, var in enumerate(explained_variance):
        print(f"  PC{i+1}: {var:.2%}")
    print(f"  Total: {explained_variance.sum():.2%}")
    
    return pca, loadings, scores_df


def interpret_components(loadings: pd.DataFrame) -> Dict[str, str]:
    """
    Interpret PCA components as level, slope, or curvature factors.
    
    Parameters:
    -----------
    loadings : pd.DataFrame
        PCA loadings (maturities x components)
    
    Returns:
    --------
    Dict[str, str]
        Mapping of component names to interpretations
    """
    interpretations = {}
    
    for col in loadings.columns:
        pc_loadings = loadings[col].values
        
        # Level: all loadings have same sign and similar magnitude
        if np.all(np.sign(pc_loadings) == np.sign(pc_loadings[0])):
            if np.std(pc_loadings) < 0.1:
                interpretations[col] = "Level"
            else:
                # Check if monotonic (slope)
                maturities_numeric = np.array([1, 3, 6, 12, 24, 36, 60, 84, 120, 240, 360])[:len(pc_loadings)]
                correlation = np.corrcoef(maturities_numeric, pc_loadings)[0, 1]
                if abs(correlation) > 0.7:
                    interpretations[col] = "Slope"
                else:
                    interpretations[col] = "Level (with variation)"
        else:
            # Curvature: loadings change sign
            sign_changes = np.sum(np.diff(np.sign(pc_loadings)) != 0)
            if sign_changes >= 1:
                interpretations[col] = "Curvature"
            else:
                interpretations[col] = "Mixed"
    
    return interpretations


def compute_pca_results(
    df: pd.DataFrame,
    n_components: int = 3
) -> Dict:
    """
    Complete PCA analysis pipeline.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Preprocessed yield data
    n_components : int
        Number of components
    
    Returns:
    --------
    Dict
        Dictionary containing PCA model, loadings, scores, explained variance, and interpretations
    """
    pca, loadings, scores = apply_pca(df, n_components=n_components)
    interpretations = interpret_components(loadings)
    
    results = {
        'pca_model': pca,
        'loadings': loadings,
        'scores': scores,
        'explained_variance': pca.explained_variance_ratio_,
        'cumulative_variance': np.cumsum(pca.explained_variance_ratio_),
        'interpretations': interpretations
    }
    
    return results


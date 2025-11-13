"""
Visualization functions for yield curve PCA analysis.

This module creates plots for explained variance, PCA loadings, component scores,
and yield curve heatmaps.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from typing import Dict, Optional


# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def plot_explained_variance(
    explained_variance: np.ndarray,
    output_path: Optional[str] = None,
    n_components: int = 10
) -> None:
    """
    Plot explained variance for PCA components.
    
    Parameters:
    -----------
    explained_variance : np.ndarray
        Explained variance ratios
    output_path : str, optional
        Path to save figure
    n_components : int
        Number of components to display
    """
    n_components = min(n_components, len(explained_variance))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    components = [f'PC{i+1}' for i in range(n_components)]
    variance = explained_variance[:n_components]
    cumulative = np.cumsum(explained_variance[:n_components])
    
    x = np.arange(n_components)
    width = 0.6
    
    # Bar plot for individual variance
    bars = ax.bar(x, variance * 100, width, label='Individual', alpha=0.8, color='steelblue')
    
    # Line plot for cumulative variance
    ax2 = ax.twinx()
    ax2.plot(x, cumulative * 100, 'ro-', linewidth=2, markersize=8, label='Cumulative', color='crimson')
    ax2.set_ylabel('Cumulative Explained Variance (%)', fontsize=12, color='crimson')
    ax2.tick_params(axis='y', labelcolor='crimson')
    ax2.set_ylim([0, 105])
    
    ax.set_xlabel('Principal Component', fontsize=12)
    ax.set_ylabel('Explained Variance (%)', fontsize=12)
    ax.set_title('PCA Explained Variance', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(components)
    ax.set_ylim([0, max(variance) * 100 * 1.2])
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, var) in enumerate(zip(bars, variance)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{var*100:.1f}%',
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved explained variance plot to {output_path}")
    
    plt.close()


def plot_pca_loadings(
    loadings: pd.DataFrame,
    output_path: Optional[str] = None,
    n_components: int = 3
) -> None:
    """
    Plot PCA loadings (factor loadings) for each component.
    
    Parameters:
    -----------
    loadings : pd.DataFrame
        PCA loadings (maturities x components)
    output_path : str, optional
        Path to save figure
    n_components : int
        Number of components to plot
    """
    n_components = min(n_components, loadings.shape[1])
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Convert maturity labels to numeric for plotting
    maturity_map = {'1M': 1, '3M': 3, '6M': 6, '1Y': 12, '2Y': 24, '3Y': 36,
                    '5Y': 60, '7Y': 84, '10Y': 120, '20Y': 240, '30Y': 360}
    maturities_numeric = [maturity_map.get(m, i) for i, m in enumerate(loadings.index)]
    
    colors = ['steelblue', 'crimson', 'forestgreen', 'orange', 'purple']
    
    for i, col in enumerate(loadings.columns[:n_components]):
        ax.plot(maturities_numeric, loadings[col].values,
                marker='o', linewidth=2, markersize=8,
                label=col, color=colors[i % len(colors)])
    
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.set_xlabel('Maturity (months)', fontsize=12)
    ax.set_ylabel('Loading', fontsize=12)
    ax.set_title('PCA Component Loadings', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Set x-axis labels
    ax.set_xticks(maturities_numeric)
    ax.set_xticklabels(loadings.index, rotation=45, ha='right')
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved PCA loadings plot to {output_path}")
    
    plt.close()


def plot_component_scores(
    scores: pd.DataFrame,
    output_path: Optional[str] = None,
    n_components: int = 3
) -> None:
    """
    Plot time series of PCA component scores.
    
    Parameters:
    -----------
    scores : pd.DataFrame
        PCA scores (dates x components)
    output_path : str, optional
        Path to save figure
    n_components : int
        Number of components to plot
    """
    n_components = min(n_components, scores.shape[1])
    
    fig, axes = plt.subplots(n_components, 1, figsize=(14, 4 * n_components), sharex=True)
    
    if n_components == 1:
        axes = [axes]
    
    colors = ['steelblue', 'crimson', 'forestgreen', 'orange', 'purple']
    
    for i, col in enumerate(scores.columns[:n_components]):
        axes[i].plot(scores.index, scores[col].values,
                     linewidth=1.5, color=colors[i % len(colors)], alpha=0.8)
        axes[i].axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
        axes[i].set_ylabel(f'{col} Score', fontsize=11)
        axes[i].set_title(f'{col} Time Series', fontsize=12, fontweight='bold')
        axes[i].grid(True, alpha=0.3)
        axes[i].fill_between(scores.index, 0, scores[col].values,
                            alpha=0.2, color=colors[i % len(colors)])
    
    axes[-1].set_xlabel('Date', fontsize=12)
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved component scores plot to {output_path}")
    
    plt.close()


def plot_yield_curve_heatmap(
    df: pd.DataFrame,
    output_path: Optional[str] = None
) -> None:
    """
    Plot heatmap of yield curve over time.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Yield data (dates x maturities)
    output_path : str, optional
        Path to save figure
    """
    # Resample to monthly if daily data
    if len(df) > 500:
        df_plot = df.resample('M').last()
    else:
        df_plot = df.copy()
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Create heatmap
    sns.heatmap(df_plot.T, cmap='YlOrRd', cbar_kws={'label': 'Yield (%)'},
                xticklabels=50, yticklabels=df_plot.columns, ax=ax)
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Maturity', fontsize=12)
    ax.set_title('Yield Curve Heatmap Over Time', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved yield curve heatmap to {output_path}")
    
    plt.close()


def generate_all_plots(
    pca_results: Dict,
    df_original: pd.DataFrame,
    output_dir: str = 'plots'
) -> None:
    """
    Generate all visualization plots.
    
    Parameters:
    -----------
    pca_results : Dict
        Dictionary containing PCA results
    df_original : pd.DataFrame
        Original yield data (for heatmap)
    output_dir : str
        Directory to save plots
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nGenerating visualizations...")
    
    # Explained variance
    plot_explained_variance(
        pca_results['explained_variance'],
        output_path=os.path.join(output_dir, 'explained_variance.png')
    )
    
    # PCA loadings
    plot_pca_loadings(
        pca_results['loadings'],
        output_path=os.path.join(output_dir, 'pca_loadings.png')
    )
    
    # Component scores
    plot_component_scores(
        pca_results['scores'],
        output_path=os.path.join(output_dir, 'component_scores.png')
    )
    
    # Yield curve heatmap
    plot_yield_curve_heatmap(
        df_original,
        output_path=os.path.join(output_dir, 'yield_curve_heatmap.png')
    )
    
    print(f"All plots saved to {output_dir}/")


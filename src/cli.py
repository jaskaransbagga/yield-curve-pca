"""
Command-line interface for yield curve PCA analysis.
"""

import argparse
import os
import sys
from datetime import datetime
import pandas as pd

from .data_fetch import fetch_yield_data, save_yield_data, load_yield_data
from .preprocessing import preprocess_yield_data
from .pca_analysis import compute_pca_results
from .visualizations import generate_all_plots


def save_results(pca_results: dict, output_dir: str = 'data') -> None:
    """
    Save PCA results to CSV files.
    
    Parameters:
    -----------
    pca_results : dict
        Dictionary containing PCA results
    output_dir : str
        Directory to save results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save loadings
    pca_results['loadings'].to_csv(
        os.path.join(output_dir, 'pca_loadings.csv')
    )
    
    # Save scores
    pca_results['scores'].to_csv(
        os.path.join(output_dir, 'pca_scores.csv')
    )
    
    # Save explained variance summary
    variance_df = pd.DataFrame({
        'Component': [f'PC{i+1}' for i in range(len(pca_results['explained_variance']))],
        'Explained_Variance': pca_results['explained_variance'],
        'Cumulative_Variance': pca_results['cumulative_variance'],
        'Interpretation': [pca_results['interpretations'].get(f'PC{i+1}', 'N/A')
                          for i in range(len(pca_results['explained_variance']))]
    })
    variance_df.to_csv(
        os.path.join(output_dir, 'pca_variance_summary.csv'),
        index=False
    )
    
    print(f"\nResults saved to {output_dir}/")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Perform PCA analysis on U.S. Treasury yield curve data'
    )
    parser.add_argument(
        '--start',
        type=str,
        default='2010-01-01',
        help='Start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end',
        type=str,
        default=None,
        help='End date (YYYY-MM-DD). Default: today'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='FRED API key (or set FRED_API_KEY environment variable)'
    )
    parser.add_argument(
        '--data-file',
        type=str,
        default=None,
        help='Use existing data file instead of fetching from FRED'
    )
    parser.add_argument(
        '--n-components',
        type=int,
        default=3,
        help='Number of PCA components (default: 3)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory for results (default: data)'
    )
    parser.add_argument(
        '--plots-dir',
        type=str,
        default='plots',
        help='Output directory for plots (default: plots)'
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('FRED_API_KEY')
    
    # Set end date to today if not provided
    if args.end is None:
        args.end = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Fetch or load data
        if args.data_file:
            print(f"Loading data from {args.data_file}...")
            df_raw = load_yield_data(args.data_file)
        else:
            if not api_key:
                print("Error: FRED API key required. Set FRED_API_KEY environment variable or use --api-key")
                sys.exit(1)
            
            df_raw = fetch_yield_data(api_key, args.start, args.end)
            save_yield_data(df_raw, os.path.join(args.output_dir, 'yield_data.csv'))
        
        # Preprocess
        df_processed, means, stds = preprocess_yield_data(df_raw)
        
        # Apply PCA
        pca_results = compute_pca_results(df_processed, n_components=args.n_components)
        
        # Save results
        save_results(pca_results, output_dir=args.output_dir)
        
        # Generate plots
        generate_all_plots(pca_results, df_raw, output_dir=args.plots_dir)
        
        # Print summary
        print("\n" + "="*60)
        print("PCA ANALYSIS SUMMARY")
        print("="*60)
        print(f"\nData Period: {df_raw.index.min()} to {df_raw.index.max()}")
        print(f"Number of Observations: {len(df_raw)}")
        print(f"Number of Maturities: {len(df_raw.columns)}")
        print(f"\nExplained Variance:")
        for i, (var, cum_var, interp) in enumerate(zip(
            pca_results['explained_variance'],
            pca_results['cumulative_variance'],
            [pca_results['interpretations'].get(f'PC{i+1}', 'N/A')
             for i in range(len(pca_results['explained_variance']))]
        )):
            print(f"  PC{i+1}: {var:.2%} (Cumulative: {cum_var:.2%}) - {interp}")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()


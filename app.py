"""
Streamlit app for interactive yield curve PCA visualization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

from src.data_fetch import fetch_yield_data, load_yield_data
from src.preprocessing import preprocess_yield_data
from src.pca_analysis import compute_pca_results
from src.visualizations import plot_pca_loadings, plot_component_scores

# Page config
st.set_page_config(
    page_title="Yield Curve PCA Analysis",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📈 U.S. Treasury Yield Curve PCA Analysis")
st.markdown("""
This app performs Principal Component Analysis on the U.S. Treasury yield curve
to identify the main factors driving changes: **Level**, **Slope**, and **Curvature**.
""")

# Sidebar
st.sidebar.header("Configuration")

# Data source selection
data_source = st.sidebar.radio(
    "Data Source",
    ["Use Existing Data", "Fetch from FRED API"]
)

df_raw = None
pca_results = None

if data_source == "Use Existing Data":
    data_file = st.sidebar.text_input(
        "Data File Path",
        value="data/yield_data.csv"
    )
    
    if st.sidebar.button("Load Data"):
        try:
            if os.path.exists(data_file):
                df_raw = load_yield_data(data_file)
                st.sidebar.success(f"Loaded {len(df_raw)} observations")
            else:
                st.sidebar.error(f"File not found: {data_file}")
        except Exception as e:
            st.sidebar.error(f"Error loading data: {e}")

else:
    api_key = st.sidebar.text_input(
        "FRED API Key",
        type="password",
        help="Get your API key from https://fred.stlouisfed.org/docs/api/api_key.html"
    )
    
    col1, col2 = st.sidebar.columns(2)
    start_date = col1.text_input("Start Date", value="2010-01-01")
    end_date = col2.text_input("End Date", value=datetime.now().strftime("%Y-%m-%d"))
    
    if st.sidebar.button("Fetch Data"):
        if not api_key:
            st.sidebar.error("Please enter FRED API key")
        else:
            try:
                with st.spinner("Fetching data from FRED..."):
                    df_raw = fetch_yield_data(api_key, start_date, end_date)
                st.sidebar.success(f"Fetched {len(df_raw)} observations")
            except Exception as e:
                st.sidebar.error(f"Error fetching data: {e}")

# Main content
if df_raw is not None:
    # Preprocess and compute PCA
    with st.spinner("Computing PCA..."):
        df_processed, means, stds = preprocess_yield_data(df_raw)
        pca_results = compute_pca_results(df_processed, n_components=3)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🔍 PCA Components",
        "📈 Time Series",
        "🌡️ Yield Curve Heatmap"
    ])
    
    with tab1:
        st.header("Explained Variance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Variance bar chart
            fig, ax = plt.subplots(figsize=(8, 5))
            components = [f'PC{i+1}' for i in range(len(pca_results['explained_variance']))]
            variance = pca_results['explained_variance'] * 100
            cumulative = pca_results['cumulative_variance'] * 100
            
            x = np.arange(len(components))
            bars = ax.bar(x, variance, alpha=0.8, color='steelblue')
            ax.set_xlabel('Principal Component')
            ax.set_ylabel('Explained Variance (%)')
            ax.set_title('Explained Variance by Component')
            ax.set_xticks(x)
            ax.set_xticklabels(components)
            ax.grid(axis='y', alpha=0.3)
            
            for bar, var in zip(bars, variance):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{var:.1f}%', ha='center', va='bottom')
            
            st.pyplot(fig)
        
        with col2:
            # Summary table
            st.subheader("Variance Summary")
            summary_df = pd.DataFrame({
                'Component': components,
                'Explained Variance (%)': variance,
                'Cumulative (%)': cumulative,
                'Interpretation': [pca_results['interpretations'].get(f'PC{i+1}', 'N/A')
                                  for i in range(len(components))]
            })
            st.dataframe(summary_df, use_container_width=True)
            
            st.info(f"""
            **Key Insights:**
            - First 3 components explain **{cumulative[2]:.1f}%** of variance
            - PC1 typically represents **Level** shifts
            - PC2 typically represents **Slope** changes
            - PC3 typically represents **Curvature** effects
            """)
        
        # Data info
        st.subheader("Data Information")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Observations", len(df_raw))
        col2.metric("Maturities", len(df_raw.columns))
        col3.metric("Start Date", df_raw.index.min().strftime("%Y-%m-%d"))
        col4.metric("End Date", df_raw.index.max().strftime("%Y-%m-%d"))
    
    with tab2:
        st.header("PCA Component Loadings")
        
        selected_component = st.selectbox(
            "Select Component",
            [f'PC{i+1}' for i in range(len(pca_results['loadings'].columns))],
            index=0
        )
        
        # Plot loadings
        fig, ax = plt.subplots(figsize=(12, 6))
        
        maturity_map = {'1M': 1, '3M': 3, '6M': 6, '1Y': 12, '2Y': 24, '3Y': 36,
                       '5Y': 60, '7Y': 84, '10Y': 120, '20Y': 240, '30Y': 360}
        maturities_numeric = [maturity_map.get(m, i) for i, m in enumerate(pca_results['loadings'].index)]
        
        colors = ['steelblue', 'crimson', 'forestgreen']
        component_idx = int(selected_component[2]) - 1
        
        for i, col in enumerate(pca_results['loadings'].columns):
            if col == selected_component or i <= component_idx:
                alpha = 1.0 if col == selected_component else 0.3
                linewidth = 2.5 if col == selected_component else 1.5
                ax.plot(maturities_numeric, pca_results['loadings'][col].values,
                       marker='o', linewidth=linewidth, markersize=8,
                       label=col, color=colors[i % len(colors)], alpha=alpha)
        
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
        ax.set_xlabel('Maturity (months)', fontsize=12)
        ax.set_ylabel('Loading', fontsize=12)
        ax.set_title(f'PCA Loadings - {selected_component}', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(maturities_numeric)
        ax.set_xticklabels(pca_results['loadings'].index, rotation=45, ha='right')
        
        st.pyplot(fig)
        
        # Interpretation
        interpretation = pca_results['interpretations'].get(selected_component, 'N/A')
        variance_pct = pca_results['explained_variance'][component_idx] * 100
        
        st.info(f"""
        **{selected_component} Interpretation:** {interpretation}
        
        - Explains **{variance_pct:.2f}%** of yield curve variance
        - Loadings show how each maturity responds to this factor
        """)
    
    with tab3:
        st.header("Component Scores Time Series")
        
        selected_component = st.selectbox(
            "Select Component",
            [f'PC{i+1}' for i in range(len(pca_results['scores'].columns))],
            index=0,
            key='scores_component'
        )
        
        # Plot time series
        fig, ax = plt.subplots(figsize=(14, 6))
        
        colors = ['steelblue', 'crimson', 'forestgreen']
        component_idx = int(selected_component[2]) - 1
        
        ax.plot(pca_results['scores'].index, pca_results['scores'][selected_component].values,
               linewidth=1.5, color=colors[component_idx % len(colors)], alpha=0.8)
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
        ax.fill_between(pca_results['scores'].index, 0,
                        pca_results['scores'][selected_component].values,
                        alpha=0.2, color=colors[component_idx % len(colors)])
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel(f'{selected_component} Score', fontsize=12)
        ax.set_title(f'{selected_component} Time Series', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # Statistics
        scores = pca_results['scores'][selected_component]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean", f"{scores.mean():.4f}")
        col2.metric("Std Dev", f"{scores.std():.4f}")
        col3.metric("Min", f"{scores.min():.4f}")
        col4.metric("Max", f"{scores.max():.4f}")
    
    with tab4:
        st.header("Yield Curve Heatmap")
        
        # Resample if too many dates
        if len(df_raw) > 500:
            df_heatmap = df_raw.resample('M').last()
            st.info("Data resampled to monthly frequency for visualization")
        else:
            df_heatmap = df_raw
        
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.heatmap(df_heatmap.T, cmap='YlOrRd', cbar_kws={'label': 'Yield (%)'},
                   xticklabels=50, yticklabels=df_heatmap.columns, ax=ax)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Maturity', fontsize=12)
        ax.set_title('Yield Curve Over Time', fontsize=14, fontweight='bold')
        
        st.pyplot(fig)

else:
    st.info("👈 Please configure data source in the sidebar to begin analysis.")
    st.markdown("""
    ### Getting Started
    
    1. **Get a FRED API Key** (free): https://fred.stlouisfed.org/docs/api/api_key.html
    2. **Or use existing data**: Place a CSV file with yield data in the `data/` directory
    3. **Run the CLI** to generate initial data:
       ```bash
       python3 -m src.cli --start 2010-01-01 --end 2025-01-01
       ```
    """)


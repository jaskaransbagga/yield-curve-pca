# Yield Curve PCA Analysis

A comprehensive Python project for performing **Principal Component Analysis (PCA)** on the U.S. Treasury yield curve to identify and visualize the main factors driving changes: **Level**, **Slope**, and **Curvature**.

## 📊 Overview

This project analyzes the U.S. Treasury yield curve using PCA to decompose yield changes into interpretable factors. The first three principal components typically explain 95-99% of yield curve variance:

- **PC1 (Level)**: Parallel shifts in the yield curve (all maturities move together)
- **PC2 (Slope)**: Steepening/flattening (short and long rates move in opposite directions)
- **PC3 (Curvature)**: Changes in the middle of the curve relative to the ends

## 🚀 Features

- **Data Fetching**: Automated download of Treasury yield data from FRED API
- **Preprocessing**: Data cleaning, alignment, and standardization
- **PCA Analysis**: Principal component decomposition with variance analysis
- **Visualizations**: Comprehensive plots for loadings, scores, and explained variance
- **Interactive App**: Streamlit web interface for exploration
- **CLI Tool**: Command-line interface for batch processing
- **Jupyter Demo**: Interactive notebook for analysis

## 📁 Project Structure

```
yield-curve-pca/
├── src/
│   ├── __init__.py
│   ├── data_fetch.py        # FRED API data fetching
│   ├── preprocessing.py     # Data cleaning and standardization
│   ├── pca_analysis.py      # PCA computation and interpretation
│   ├── visualizations.py   # Plotting functions
│   └── cli.py              # Command-line interface
├── notebooks/
│   └── yield_curve_pca_demo.ipynb   # Jupyter demo
├── tests/
│   ├── test_preprocessing.py
│   └── test_pca_analysis.py
├── data/                   # Data storage (CSV files)
├── plots/                  # Generated visualizations
├── app.py                  # Streamlit web app
├── requirements.txt
├── README.md
└── .gitignore
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd yield-curve-pca
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Get a FRED API key** (free):
   - Visit: https://fred.stlouisfed.org/docs/api/api_key.html
   - Sign up and get your API key
   - Set as environment variable: `export FRED_API_KEY="your_key_here"`

## 📖 Usage

### Command-Line Interface

Run the complete analysis pipeline:

```bash
python3 -m src.cli --start 2010-01-01 --end 2025-01-01
```

**Options**:
- `--start`: Start date (YYYY-MM-DD)
- `--end`: End date (YYYY-MM-DD), default: today
- `--api-key`: FRED API key (or set `FRED_API_KEY` env var)
- `--data-file`: Use existing CSV file instead of fetching
- `--n-components`: Number of PCA components (default: 3)
- `--output-dir`: Output directory for results (default: `data/`)
- `--plots-dir`: Output directory for plots (default: `plots/`)

**Example**:
```bash
python3 -m src.cli --start 2010-01-01 --end 2024-12-31 --n-components 3
```

This will:
1. Fetch yield data from FRED
2. Preprocess and clean the data
3. Apply PCA analysis
4. Generate visualizations
5. Save results to CSV files
6. Print summary statistics

### Streamlit Web App

Launch the interactive web application:

```bash
streamlit run app.py
```

The app provides:
- Interactive component selection
- Real-time visualization of loadings and scores
- Yield curve heatmap
- Variance explained charts
- Data exploration tools

### Jupyter Notebook

Open the demo notebook:

```bash
jupyter notebook notebooks/yield_curve_pca_demo.ipynb
```

## 📊 Output Files

### Data Files (`data/`)
- `yield_data.csv`: Raw yield curve data
- `pca_loadings.csv`: PCA component loadings (maturities × components)
- `pca_scores.csv`: PCA component scores (dates × components)
- `pca_variance_summary.csv`: Explained variance summary

### Plots (`plots/`)
- `explained_variance.png`: Bar chart of explained variance
- `pca_loadings.png`: Line plot of component loadings
- `component_scores.png`: Time series of component scores
- `yield_curve_heatmap.png`: Heatmap of yield curve over time

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## 📈 Example Output

### Explained Variance

Typically, the first three components explain:
- **PC1**: 80-95% (Level factor)
- **PC2**: 5-15% (Slope factor)
- **PC3**: 1-5% (Curvature factor)
- **Total**: 95-99% of variance

### Component Interpretations

**PC1 (Level)**:
- All loadings have the same sign
- Represents parallel shifts in the yield curve
- All maturities move up or down together

**PC2 (Slope)**:
- Short-term loadings opposite to long-term
- Represents steepening/flattening
- Short rates and long rates move in opposite directions

**PC3 (Curvature)**:
- Middle maturities load differently from ends
- Represents "butterfly" movements
- The curve becomes more or less curved

## 🔧 Technical Details

### Data Source
- **FRED API**: U.S. Treasury constant maturity rates
- **Maturities**: 1M, 3M, 6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y
- **Frequency**: Daily or monthly

### Preprocessing
- Forward fill for missing values
- Demeaning (centering) for PCA
- Optional: Z-score normalization

### PCA Method
- Uses `sklearn.decomposition.PCA`
- Standardized data (demeaned)
- Computes loadings, scores, and explained variance

## 📚 References

- Litterman, R., & Scheinkman, J. (1991). Common factors affecting bond returns. *Journal of Fixed Income*, 1(1), 54-61.
- FRED API Documentation: https://fred.stlouisfed.org/docs/api/
- Scikit-learn PCA: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

Created for quantitative finance analysis and research.

---

**Note**: This project requires a FRED API key for data fetching. The key is free and can be obtained from the Federal Reserve Bank of St. Louis website.


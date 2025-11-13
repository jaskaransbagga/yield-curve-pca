# GitHub Setup Instructions

Your repository is ready to push to GitHub! Follow these steps:

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `yield-curve-pca`
3. Description: `Principal Component Analysis on U.S. Treasury yield curve to identify level, slope, and curvature factors`
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

## Step 2: Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
cd /Users/jaskaranbagga/yield-curve-pca

# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/yield-curve-pca.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Alternative: Using SSH

If you prefer SSH:

```bash
git remote add origin git@github.com:YOUR_USERNAME/yield-curve-pca.git
git branch -M main
git push -u origin main
```

## Quick Push Script

Or run this command (replace YOUR_USERNAME):

```bash
cd /Users/jaskaranbagga/yield-curve-pca && \
git remote add origin https://github.com/YOUR_USERNAME/yield-curve-pca.git && \
git branch -M main && \
git push -u origin main
```

## What's Already Committed

✅ All source code (15 files)
✅ README.md with full documentation
✅ Requirements.txt
✅ .gitignore
✅ Tests (12 tests, all passing)
✅ Jupyter notebook demo
✅ Streamlit app
✅ Project summary

## Repository Stats

- **15 files** committed
- **2,278 lines** of code and documentation
- **Initial commit** ready
- **Main branch** set up

Your project is ready to share! 🚀


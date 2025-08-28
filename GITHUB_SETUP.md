# How to Publish to GitHub

Follow these steps to publish your Guard Shift Analyzer to GitHub:

## Prerequisites
1. Make sure you have a GitHub account at [github.com](https://github.com)
2. Install Git on your computer if you haven't already

## Steps to Publish

### 1. Initialize Git Repository
Open PowerShell in your project directory and run:
```powershell
cd "c:\Users\NoySal\Downloads\GiborZar"
git init
```

### 2. Add Files to Git
```powershell
git add .
git commit -m "Initial commit: Hebrew Guard Shift Analyzer with duplicate removal and top guards dashboard"
```

### 3. Create Repository on GitHub
1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Fill in the repository details:
   - **Repository name**: `guard-shift-analyzer` (or your preferred name)
   - **Description**: `Hebrew Guard Shift Analyzer - Streamlit app for analyzing guard shifts with top performers dashboard`
   - **Visibility**: Select "Public"
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

### 4. Connect Local Repository to GitHub
After creating the repository, GitHub will show you commands. Use these:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/guard-shift-analyzer.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### 5. (Alternative) Using GitHub Desktop
If you prefer a GUI:
1. Download and install [GitHub Desktop](https://desktop.github.com/)
2. Open GitHub Desktop
3. File → Add Local Repository → Browse to your folder
4. Click "Publish repository"
5. Choose name, description, and make it public

## Repository Structure
Your repository will contain:
```
guard-shift-analyzer/
├── .gitignore
├── README.md
├── requirements.txt
├── guard_shift_analyzer.py
└── shifts_structured_long.csv
```

## After Publishing
1. Your repository will be available at: `https://github.com/YOUR_USERNAME/guard-shift-analyzer`
2. Others can clone it with: `git clone https://github.com/YOUR_USERNAME/guard-shift-analyzer.git`
3. You can share the link for others to view the code and documentation

## Future Updates
To update your repository:
```powershell
git add .
git commit -m "Description of changes"
git push
```

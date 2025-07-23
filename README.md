# 💸 Personal Wealth Tracker — Real-Time SoFi Integration + Live Market Data

> **🏦 SoFi Users Quick Start:** Download your portfolio CSV from SoFi.com → Upload to app → Get live tracking instantly!

## 🚀 Project Mission
Welcome to your **personal command center for wealth building** — a fully private, real-time, investment and net worth tracker with **live SoFi integration** built for individuals aiming to become future millionaires, FIRE practitioners, and quant finance professionals.

This system **runs 100% locally** with **real-time market data** and **automatic SoFi account syncing**. No data tracking. No cloud sync. Your entire financial life, modeled and visualized — safely and powerfully.

---

## 📥 **SoFi Users: Get Your Data (2 Minutes)**

### Method 1: Direct CSV Export ✅
1. **Login to SoFi.com** (desktop browser)
2. **Go to:** Invest → Portfolio → Export (or Account → Statements)
3. **Download CSV** → Upload to your tracker → Done!

### Method 2: Need Help Finding Export?
- **📖 Full Guide:** See `sofi_data_guide.md` for screenshots
- **🧹 CSV Cleaner:** Use `data/sofi_cleaner.py` for any format
- **📞 SoFi Support:** 1-855-456-7634 (ask for "CSV portfolio export")

### Method 3: Automated Sync (Advanced)
- **Setup .env file** with Plaid API keys → Auto-sync SoFi account
- **Real-time updates** without manual CSV exports

---

## ⚡️ What It Does
- 📊 **Track all your investments** (VTI, SOFI, BTC, TSLA, etc.) with real-time prices
- 📥 **CSV Import/Export** - Drag & drop your real SoFi/Fidelity/Robinhood exports (100% local)
- 🏦 **SoFi Integration** - Auto-sync your actual SoFi account data via Plaid API
- 💳 **Credit card tracking** with due date alerts, utilization monitoring, and status tracking
- 🧮 **Live portfolio value & daily gains** with automatic calculations
- 🎯 **Enhanced goal tracking** with progress analytics and timeline management
- 📈 **Interactive charts** and analytics using Plotly for portfolio visualization
- 📡 **Live Monitor** - Real-time streaming dashboard with alerts
- 🚀 **Demo mode** with realistic sample data to explore all features
- 🔄 **Auto-refresh** functionality for real-time updates
- ⚡ **Quick actions** for rapid data entry from the sidebar

---

## 🔧 Built With
| Tool        | Why It's Used                           |
|-------------|------------------------------------------|
| Python      | Clean, readable, fintech-native          |
| Streamlit   | Instant dashboard, no front-end dev      |
| pandas      | Track, filter, and calculate clean data  |
| yfinance    | Real-time stock & ETF market data        |
| plotly      | Interactive, zoomable investment charts  |
| GitHub      | Project versioning & career showcase     |

---

## 🛠 Setup (3 Minutes)
```bash
# 1. Clone this repo
git clone https://github.com/your-username/personal-wealth-tracker
cd personal-wealth-tracker

# 2. Install the required packages
pip install -r requirements.txt

# 3. (Optional) Setup SoFi Integration
# Create .env file for real SoFi account sync:
echo "PLAID_CLIENT_ID=your_client_id_here" > .env
echo "PLAID_SECRET=your_secret_here" >> .env
echo "PLAID_ENV=sandbox" >> .env

# 4. Run locally (Choose one method):
# Method A: Simple launch
streamlit run app.py

# Method B: Enhanced launcher (Windows)
start_tracker.bat

# Method C: Python launcher (Cross-platform)
python start_tracker.py
```

### 🏦 SoFi Integration Setup
To connect your actual SoFi account:

1. **Sign up for Plaid** (free for personal use): https://plaid.com/
2. **Get your API keys** from the Plaid dashboard
3. **Create `.env` file** in your project folder:
   ```
   PLAID_CLIENT_ID=your_client_id_here
   PLAID_SECRET=your_secret_here
   PLAID_ENV=sandbox
   ```
4. **Restart the app** - your SoFi data will auto-sync!

**Security:** All credentials stay local. No data sent to cloud.

> 📖 **See [FEATURES.md](FEATURES.md) for complete feature guide and tutorials**

---

## 🛡 Privacy First
- 🔐 **Runs entirely on your machine** — zero cloud dependencies
- 🧠 **All inputs and data stay local** — no leaks, no syncing
- 👨‍💻 Designed for personal wealth safety & clarity

---

## 🤖 **Automated CI/CD Pipeline**

### 🚀 GitHub Actions Automation
Every code push automatically triggers our **enterprise-grade CI/CD pipeline**:

#### **⚡ Quick Tests** (Pull Requests)
- **🧪 Core imports** - Validates all dependencies
- **📊 Data validation** - Tests SoFi CSV processing  
- **🧹 CSV cleaner** - Ensures all formats work
- **⏱️ Duration:** ~2 minutes

#### **🔥 Full Pipeline** (Main Branch)
- **🔍 Code quality** - Black, flake8, isort formatting
- **🛡️ Security scans** - Bandit, safety vulnerability checks
- **🧪 Cross-platform tests** - Ubuntu, Windows, macOS
- **🌐 Streamlit testing** - App startup and health checks
- **💾 CSV validation** - Multiple SoFi format testing
- **🔒 Privacy checks** - Ensures no sensitive data leaks
- **📦 Build & package** - Ready for deployment
- **📢 Notifications** - Success/failure alerts

#### **🎯 Deployment Ready**
```bash
# Manual deployment trigger
# GitHub Actions → Run workflow → Select environment
```

### **📊 Pipeline Status**
[![🚀 Wealth Tracker CI/CD](https://github.com/your-username/personal-wealth-tracker/actions/workflows/wealth-tracker-ci.yml/badge.svg)](https://github.com/your-username/personal-wealth-tracker/actions/workflows/wealth-tracker-ci.yml)
[![⚡ Quick Tests](https://github.com/your-username/personal-wealth-tracker/actions/workflows/quick-test.yml/badge.svg)](https://github.com/your-username/personal-wealth-tracker/actions/workflows/quick-test.yml)

---

## 🔭 Future Power Features (Optional Builds)
- 🔄 Connect to SoFi, Fidelity, Robinhood via CSV/API
- 📲 Mobile-responsive layout with wealth widgets
- 🔔 Trigger alerts when stocks rise/fall past set values
- 🧾 Auto-generate monthly wealth reports (PDF)
- 📊 Monte Carlo simulations — project your financial future
- 🤖 AI mode: natural language insights, trend summaries, and scenario planning

---

## 🧠 Why This Project Matters (Career & Life)
| Area | Benefit |
|------|---------|
| 💼 Job Market | Proof of Python + Finance + Real-World Build |
| 🧠 Discipline | Reinforces savings, tracking, and planning |
| 🚀 Resume | Project shows Streamlit, pandas, yfinance mastery |
| 🔐 Privacy | Unlike Mint or Personal Capital — your data, your rules |

---

## 👨‍💻 Creator
**Tyler Keesee**  
25, building wealth from $0 to $1M+ while in college, using tech and discipline. 
This tracker is part of a larger GitHub showcase for roles in software, quant finance, and fintech.

---

## 💼 License
MIT — Free forever. No login. No lock-in. Just pure financial clarity.

---

## 🧠 Final Words
This is more than a tracker — it's your **daily dashboard to millionaire status**. Whether you're saving for your first truck or running Monte Carlo sims on early retirement, this is where personal finance meets powerful tech.

Built for creators. Designed for discipline. Ready for quant upgrades.

Start building your future — one chart, one dollar, one day at a time.

---

personal-wealth-tracker/
├── 🚀 **Core Application**
│   ├── app.py                    # Enhanced Streamlit app with CSV import/export
│   ├── financial_apis.py         # SoFi/Plaid integration + real-time data  
│   ├── start_tracker.py          # Enhanced launcher with automation info
│   └── requirements.txt          # Python dependencies
├── 🏦 **SoFi Integration**
│   ├── data/sofi_cleaner.py      # SoFi CSV format processor
│   ├── sofi_data_guide.md        # Step-by-step SoFi export guide
│   └── sample_portfolio.csv      # Test file for CSV import
├── 🤖 **GitHub Actions Automation**
│   ├── .github/workflows/
│   │   ├── wealth-tracker-ci.yml # Full CI/CD pipeline
│   │   └── quick-test.yml        # Fast PR testing
│   └── .github/PULL_REQUEST_TEMPLATE.md # PR guidelines
├── 📊 **Data & Security**
│   ├── data/                     # Your real financial data (git-ignored)
│   │   ├── investments.csv       # Your portfolio positions
│   │   ├── credit_cards.csv      # Credit card tracking
│   │   └── goals.csv            # Financial goals
│   └── .gitignore               # Privacy protection
├── 📖 **Documentation**
│   ├── README.md                # Main project guide
│   ├── FEATURES.md              # Complete feature guide
│   ├── DEPLOY.md                # Automation & deployment guide
│   └── LICENSE                  # MIT license
└── 🎯 **Ready for Production**
    ├── ✅ Full CI/CD automation
    ├── ✅ Security scanning
    ├── ✅ Cross-platform testing
    └── ✅ Deployment ready

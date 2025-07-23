# 💸 Personal Wealth Tracker - Feature Guide

## 🚀 Main Features

### 🏠 Dashboard
Your financial command center with real-time overview:
- **Live portfolio value** with gains/losses
- **Net worth calculation** (investments - debt)
- **Credit card alerts** for upcoming due dates
- **Top holdings** display
- **Quick setup guide** with demo data option

### 📊 Investments
Professional-grade portfolio tracking:
- **Real-time price updates** via yfinance
- **CSV Import/Export** - Drag & drop real broker data (100% local & secure)
- **Smart column detection** - Auto-maps Symbol, Shares, Cost columns
- **Quick-add buttons** for popular stocks (VTI, SOFI, BTC, AAPL, TSLA)
- **Current price display** when entering symbols
- **Portfolio allocation charts**
- **Gain/loss tracking** with percentages
- **Holdings table** with live updates

### 💳 Credit Cards
Complete credit card management:
- **Balance tracking** with utilization percentages
- **Due date alerts** (red for 3 days, yellow for 7 days)
- **Status tracking** (active, closing, closed clean)
- **Credit limit monitoring**
- **APR tracking**
- **Overall utilization calculation**

### 🎯 Goals
Advanced goal tracking with analytics:
- **Progress vs time tracking** - are you ahead or behind?
- **Daily/monthly savings targets**
- **Achievability assessment**
- **Auto-update** for portfolio goals
- **Status indicators** (🚀 ahead, ✅ on track, ⚠️ behind)
- **Detailed breakdowns** with recommendations

### 📈 Analytics
Investment performance insights:
- **Portfolio performance charts**
- **Asset allocation analysis**
- **Risk metrics** and diversification scores
- **Historical value tracking**
- **Return calculations**

### 📡 Live Monitor (NEW!)
Real-time streaming dashboard:
- **Live price updates** every 5-60 seconds
- **Color-coded alerts** for significant moves
- **Real-time portfolio value**
- **Live position tracking**
- **Market alerts** for >2% price changes
- **Continuous update counter**
- **Live charts** and breakdowns

## 📥 CSV Import/Export (NEW!)

### What It Does
- **Import real broker data** from SoFi, Fidelity, Robinhood, etc.
- **Smart auto-detection** of Symbol, Shares, Cost columns
- **Multiple merge strategies** (add new, replace all, update existing)
- **Export portfolio** with current values and calculations
- **100% local processing** - your data never leaves your computer

### Supported Brokers
- **SoFi**: Symbol, Shares, Average Cost, Current Value
- **Fidelity**: Symbol, Quantity, Price Paid, Current Price  
- **Robinhood**: Instrument, Quantity, Average Buy Price
- **Charles Schwab**: Symbol, Shares, Price
- **E*TRADE**: Symbol, Qty, Cost Basis
- **Any broker** with Symbol + Shares columns

### How to Use
1. **Export from your broker** (usually under "Portfolio" → "Export")
2. **Go to Investments page** → "📥 Import CSV"
3. **Upload your file** - auto-detection finds the right columns
4. **Review preview** and choose merge strategy
5. **Import** - your real data is now tracked with live prices!

### Quick Import (From Anywhere)
- **Sidebar button**: "📥 Import CSV" works from any page
- **Auto-detection**: Smart mapping of common column names
- **One-click import** for properly formatted files
- **Instant feedback** with success/error messages

### Export Features
- **Real-time values**: Current prices and portfolio value
- **Multiple formats**: Standard CSV with all key data
- **Backup ready**: Save your data anytime
- **Shareable format**: Compatible with Excel, Google Sheets

### Security & Privacy
- ✅ **100% local processing** - files never uploaded to servers
- ✅ **No data tracking** - your financial info stays private
- ✅ **Secure storage** - CSV files stored locally only
- ✅ **Git-ignored** - financial data never committed to version control

## 🏦 SoFi Integration

### What It Does
- **Auto-sync** your SoFi investment account holdings
- **Real-time balance** updates
- **Automatic data import** without manual entry
- **Secure local storage** - no cloud sync

### Setup Process
1. **Sign up for Plaid** at https://plaid.com/ (free)
2. **Get API credentials** from dashboard
3. **Create .env file**:
   ```
   PLAID_CLIENT_ID=your_id
   PLAID_SECRET=your_secret
   PLAID_ENV=sandbox
   ```
4. **Click "Sync SoFi"** in sidebar
5. **Your data auto-imports!**

### Security
- ✅ All credentials stored locally
- ✅ No data sent to cloud
- ✅ Your financial info stays private
- ✅ Uses bank-grade Plaid security

## ⚡ Real-Time Features

### Auto-Refresh
- **30-second updates** for portfolio values
- **Live price feeds** from market data
- **Automatic calculations** of gains/losses
- **Real-time net worth** updates

### Live Mode
- **Streaming updates** without page refresh
- **Live alerts** for market movements
- **Continuous monitoring** of your positions
- **Real-time charts** and metrics

### Caching
- **Smart caching** prevents API overuse
- **30-second cache** for price data
- **Optimized performance** for multiple symbols
- **Error handling** for missing data

## 🎨 User Interface

### Navigation
- **Radio button** navigation (smoother than dropdown)
- **Live sidebar stats** showing key metrics
- **Quick action buttons** for rapid data entry
- **Professional styling** with custom CSS

### Responsive Design
- **Wide layout** for desktop viewing
- **Column layouts** for organized display
- **Color coding** for gains (green) and losses (red)
- **Emojis and icons** for visual appeal

### Alerts & Notifications
- **Due date warnings** for credit cards
- **Price movement alerts** for significant changes
- **Portfolio milestone** notifications
- **Goal progress** status updates

## 🔧 Technical Features

### Data Storage
- **Local CSV files** in `data/` folder
- **Auto-backup** of all financial data
- **No cloud dependencies** - fully private
- **Git-ignored** data files for security

### Performance
- **Caching** for API calls
- **Optimized** data loading
- **Real-time** calculations
- **Error handling** for network issues

### Customization
- **Demo data** for testing features
- **Flexible refresh rates** (5-60 seconds)
- **Customizable alerts** and thresholds
- **Multiple launch options**

## 🚀 Getting Started

### Quick Start (3 minutes)
1. **Clone repo** and install dependencies
2. **Run app**: `python start_tracker.py`
3. **Load demo data** to see all features
4. **Add your real investments**
5. **Setup SoFi integration** (optional)

### Pro Tips
- 💡 **Load demo data first** to explore features
- 🔄 **Enable auto-refresh** for live updates
- 📡 **Try Live Monitor** for real-time tracking
- 🎯 **Set realistic goals** with target dates
- 🏦 **Connect SoFi** for automatic syncing

### Example Workflow
1. **Start app** → Load demo data
2. **Dashboard** → See overview and alerts
3. **Investments** → Add your real holdings
4. **Goals** → Set $100K portfolio target
5. **Live Monitor** → Watch real-time updates
6. **SoFi Sync** → Auto-import positions

---

## 📈 Resume Impact

This project demonstrates:
- **Full-stack development** (Python + Streamlit)
- **Financial APIs** integration (Plaid/yfinance)
- **Real-time data** processing
- **User experience** design
- **Security best practices**
- **Professional documentation**

Perfect for fintech, quant, and software engineering roles!

---

*Built by Tyler Keesee - Your path from $0 to $1M+ starts here* 🚀 
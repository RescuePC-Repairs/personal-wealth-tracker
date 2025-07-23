# 🏦 SoFi Data Export Guide

## 📥 Getting Your Real SoFi Data (No PDF Conversion!)

### Method 1: SoFi Web Platform (Recommended)
**URL:** https://www.sofi.com

1. **Login to SoFi Web** (desktop browser required)
2. **Navigate to Investment Portfolio:**
   - Go to **"Invest"** → **"Portfolio"**
   - Look for **"Export"** or **"Download"** button (usually top-right)
   - Select **"CSV"** or **"Excel"** format

3. **For Banking/Checking:**
   - Go to **"Money"** → **"Transactions"**
   - Select date range → **"Export to CSV"**

4. **For Goals/Vaults:**
   - **"Money"** → **"Vaults"** → **"Export"**

### Method 2: SoFi Mobile (Desktop Mode)
If you only have mobile access:

1. **Open mobile browser** (Safari/Chrome)
2. **Request Desktop Site:**
   - Safari: Press "aA" → "Request Desktop Website"
   - Chrome: Menu → "Desktop site"
3. **Follow Method 1** steps above

### Method 3: SoFi Statements (Direct CSV)
Many users miss this:

1. **Account** → **"Documents & Statements"**
2. Look for **"Account Activity CSV"** or **"Transaction Export"**
3. **Download directly** - no PDF conversion needed!

## 🔧 What SoFi CSV Contains

### Investment Portfolio Export:
```csv
Symbol,Shares,Cost_Basis,Market_Value,Unrealized_GL
VTI,15.5,4378.75,4500.25,121.50
SOFI,100,1250.00,1180.00,-70.00
```

### Banking/Checking Export:
```csv
Date,Description,Amount,Balance,Category
2025-01-15,Transfer to Invest,500.00,2500.00,Transfer
2025-01-14,Paycheck,2000.00,3000.00,Income
```

## 📊 Import Into Your Wealth Tracker

### Option A: Direct Upload
1. **Download SoFi CSV** using methods above
2. **Open your Wealth Tracker** → **Investments page**
3. **"📥 Import Your Real SoFi/Brokerage Data"**
4. **Upload file** → Auto-detection handles SoFi format
5. **Import** → Live prices start tracking!

### Option B: SoFi Cleaner Script
Use the automated cleaner to process SoFi's raw format:

```bash
python data/sofi_cleaner.py your_sofi_export.csv
```

## 🚨 Troubleshooting

### "No Export Button Found"
- **Try different browsers** (Chrome works best)
- **Clear cache/cookies** for SoFi.com
- **Contact SoFi support:** Ask for "CSV export of portfolio holdings"
- **Use SoFi Hub:** https://portal.sofihub.com/ (if you have access)

### "CSV Won't Import"
- **Check column names** - SoFi sometimes uses different headers
- **Remove special characters** from symbol names
- **Use Manual Mapping** in wealth tracker import section

### "Missing Data"
- **Check date range** in SoFi export settings
- **Verify account selection** (Active vs Automated investing)
- **Export separately:** Portfolio + Banking + Goals

## 💡 Pro Tips

### Automatic Updates
Once you have the CSV format working:
1. **Save SoFi export format** as template
2. **Weekly exports** → Keep data fresh
3. **Setup .env file** for Plaid integration (fully automated)

### Data Validation
After import, verify in your tracker:
- **Portfolio value** matches SoFi dashboard
- **Individual positions** are correct
- **Cost basis** aligns with your records

### Privacy & Security
- ✅ **Download directly** from SoFi
- ✅ **Delete raw CSV** after import
- ✅ **Your tracker data** stays local only
- ✅ **No cloud upload** required

## 📞 Still Having Issues?

### Contact SoFi Support:
**Phone:** 1-855-456-7634  
**Request:** "I need to export my investment portfolio as CSV for personal tracking"

### Alternative Data Sources:
- **Plaid API** (automated sync)
- **Manual entry** (one-time setup)
- **Screenshot → Manual** (last resort)

---

**Bottom Line:** SoFi definitely supports CSV exports - it's just a matter of finding the right menu. Most users locate it within 2-3 clicks once they know where to look! 
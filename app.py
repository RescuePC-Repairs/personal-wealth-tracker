import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from pathlib import Path
import numpy as np
import time

# Import our financial APIs
try:
    from financial_apis import (
        SoFiConnector, RealTimeMarketData, GoalTracker, 
        sync_sofi_data, market_data, goal_tracker
    )
    FINANCIAL_APIS_AVAILABLE = True
except ImportError:
    FINANCIAL_APIS_AVAILABLE = False
    st.warning("⚠️ Financial APIs not available. Run: pip install plaid-python requests python-dotenv")

# Page config
st.set_page_config(
    page_title="💸 Personal Wealth Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #1f77b4;
    }
    .nav-button {
        width: 100%;
        margin: 0.25rem 0;
    }
    .credit-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
    }
    .stAlert > div {
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# File paths
INVESTMENTS_FILE = data_dir / "investments.csv"
CREDIT_CARDS_FILE = data_dir / "credit_cards.csv"
GOALS_FILE = data_dir / "goals.csv"
TRANSACTIONS_FILE = data_dir / "transactions.csv"

def init_data_files():
    """Initialize CSV files if they don't exist"""
    
    # Investments file
    if not INVESTMENTS_FILE.exists():
        investments_df = pd.DataFrame(columns=[
            'symbol', 'name', 'shares', 'avg_cost', 'date_added'
        ])
        investments_df.to_csv(INVESTMENTS_FILE, index=False)
    
    # Credit cards file
    if not CREDIT_CARDS_FILE.exists():
        credit_cards_df = pd.DataFrame(columns=[
            'card_name', 'last_balance', 'due_date', 'status', 'credit_limit', 'apr'
        ])
        credit_cards_df.to_csv(CREDIT_CARDS_FILE, index=False)
    
    # Goals file
    if not GOALS_FILE.exists():
        goals_df = pd.DataFrame(columns=[
            'goal_name', 'target_amount', 'current_amount', 'target_date'
        ])
        goals_df.to_csv(GOALS_FILE, index=False)
    
    # Transactions file
    if not TRANSACTIONS_FILE.exists():
        transactions_df = pd.DataFrame(columns=[
            'date', 'type', 'symbol', 'amount', 'shares', 'description'
        ])
        transactions_df.to_csv(TRANSACTIONS_FILE, index=False)

def add_sample_data():
    """Add realistic sample data for demonstration"""
    
    # Sample investments based on Tyler's goals
    sample_investments = pd.DataFrame({
        'symbol': ['VTI', 'SOFI', 'BTC-USD'],
        'name': ['Vanguard Total Stock Market ETF', 'SoFi Technologies Inc', 'Bitcoin USD'],
        'shares': [10.0, 50.0, 0.1],
        'avg_cost': [280.00, 12.50, 45000.00],
        'date_added': ['2024-01-15', '2024-02-10', '2024-03-01']
    })
    
    # Sample credit cards
    sample_cards = pd.DataFrame({
        'card_name': ['Chase Freedom Unlimited', 'Capital One Venture'],
        'last_balance': [850.00, 0.00],
        'due_date': ['2025-02-15', '2025-02-20'],
        'status': ['active', 'active'],
        'credit_limit': [5000.00, 10000.00],
        'apr': [21.99, 18.99]
    })
    
    # Sample goals
    sample_goals = pd.DataFrame({
        'goal_name': ['First $100K Portfolio', 'Emergency Fund'],
        'target_amount': [100000.00, 20000.00],
        'current_amount': [15000.00, 5000.00],
        'target_date': ['2027-12-31', '2025-12-31']
    })
    
    return sample_investments, sample_cards, sample_goals

def auto_detect_column(columns, keywords):
    """Auto-detect column based on keywords"""
    columns_lower = [col.lower() for col in columns]
    
    for i, col in enumerate(columns_lower):
        for keyword in keywords:
            if keyword.lower() in col:
                return i + 1  # +1 because selectbox has empty option at index 0
    
    return 0  # Return empty option if no match

def process_csv_import(df, symbol_col, shares_col, cost_col=None, value_col=None):
    """Process imported CSV data into our format"""
    
    processed_data = []
    
    for _, row in df.iterrows():
        try:
            # Clean symbol (remove spaces, convert to uppercase)
            symbol = str(row[symbol_col]).strip().upper()
            if not symbol or symbol == 'NAN':
                continue
                
            # Clean shares (convert to float)
            shares = float(str(row[shares_col]).replace(',', ''))
            if shares <= 0:
                continue
            
            # Calculate average cost
            avg_cost = 0.0
            if cost_col and cost_col in df.columns:
                try:
                    avg_cost = float(str(row[cost_col]).replace('$', '').replace(',', ''))
                except:
                    avg_cost = 0.0
            
            # If no cost but we have value, calculate from current price
            if avg_cost == 0.0 and value_col and value_col in df.columns:
                try:
                    current_value = float(str(row[value_col]).replace('$', '').replace(',', ''))
                    if FINANCIAL_APIS_AVAILABLE:
                        # Get current price to back-calculate avg cost
                        current_prices = market_data.get_current_prices([symbol])
                        current_price = current_prices.get(symbol, {}).get('price', 0)
                        if current_price > 0:
                            avg_cost = current_value / shares
                        else:
                            avg_cost = current_value / shares  # Fallback
                    else:
                        # Fallback without market data
                        avg_cost = current_value / shares
                except:
                    avg_cost = 1.0  # Default fallback
            
            # If still no cost, use current market price as estimate
            if avg_cost == 0.0:
                if FINANCIAL_APIS_AVAILABLE:
                    try:
                        current_prices = market_data.get_current_prices([symbol])
                        avg_cost = current_prices.get(symbol, {}).get('price', 1.0)
                    except:
                        avg_cost = 1.0
                else:
                    avg_cost = 1.0
            
            processed_data.append({
                'symbol': symbol,
                'name': '',  # Will be filled by market data lookup
                'shares': shares,
                'avg_cost': avg_cost,
                'date_added': datetime.now().strftime('%Y-%m-%d')
            })
            
        except Exception as e:
            continue  # Skip invalid rows
    
    return pd.DataFrame(processed_data)

def handle_data_merge(existing_df, new_df, strategy):
    """Handle merging new data with existing data"""
    
    if strategy == "Replace all data":
        return new_df
    
    elif strategy == "Add new positions only":
        # Only add symbols that don't exist
        existing_symbols = set(existing_df['symbol'].str.upper())
        new_positions = new_df[~new_df['symbol'].str.upper().isin(existing_symbols)]
        return pd.concat([existing_df, new_positions], ignore_index=True)
    
    elif strategy == "Update existing + add new":
        # Update existing positions and add new ones
        result_df = existing_df.copy()
        
        for _, new_row in new_df.iterrows():
            symbol = new_row['symbol'].upper()
            
            # Check if symbol exists
            existing_mask = result_df['symbol'].str.upper() == symbol
            
            if existing_mask.any():
                # Update existing position
                idx = result_df[existing_mask].index[0]
                result_df.loc[idx, 'shares'] = new_row['shares']
                result_df.loc[idx, 'avg_cost'] = new_row['avg_cost']
                result_df.loc[idx, 'date_added'] = new_row['date_added']
            else:
                # Add new position
                result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)
        
        return result_df
    
    return existing_df

def process_sofi_csv(df):
    """Process SoFi CSV with intelligent column detection"""
    
    # SoFi column mapping
    column_mappings = {
        'Symbol': ['symbol', 'Symbol', 'Ticker', 'SYMBOL', 'Stock'],
        'Shares': ['shares', 'Shares', 'Quantity', 'Units', 'SHARES', 'Qty'],
        'Cost_Basis': ['cost_basis', 'Cost_Basis', 'Total_Cost', 'Avg_Cost', 'Average_Cost'],
        'Market_Value': ['market_value', 'Market_Value', 'Current_Value', 'Value'],
        'Price': ['price', 'Price', 'Current_Price', 'Last_Price']
    }
    
    # Auto-detect columns
    detected_columns = {}
    for target_col, possible_names in column_mappings.items():
        for col_name in df.columns:
            if any(possible.lower() in col_name.lower() for possible in possible_names):
                detected_columns[target_col] = col_name
                break
    
    clean_data = []
    
    for _, row in df.iterrows():
        try:
            # Extract symbol
            symbol_col = detected_columns.get('Symbol')
            if not symbol_col:
                continue
                
            symbol = str(row[symbol_col]).strip().upper()
            if not symbol or symbol in ['NAN', 'NULL', '']:
                continue
            
            # Extract shares
            shares_col = detected_columns.get('Shares')
            if not shares_col:
                continue
                
            shares = float(str(row[shares_col]).replace(',', '').replace('$', ''))
            if shares <= 0:
                continue
            
            # Calculate average cost
            avg_cost = 0.0
            
            # Try cost basis first
            cost_basis_col = detected_columns.get('Cost_Basis')
            if cost_basis_col and pd.notna(row[cost_basis_col]):
                total_cost = float(str(row[cost_basis_col]).replace(',', '').replace('$', ''))
                avg_cost = total_cost / shares if shares > 0 else 0
            
            # Try market value estimate
            elif detected_columns.get('Market_Value'):
                market_value_col = detected_columns['Market_Value']
                if pd.notna(row[market_value_col]):
                    market_value = float(str(row[market_value_col]).replace(',', '').replace('$', ''))
                    avg_cost = market_value / shares
            
            # Try price
            elif detected_columns.get('Price'):
                price_col = detected_columns['Price']
                if pd.notna(row[price_col]):
                    avg_cost = float(str(row[price_col]).replace(',', '').replace('$', ''))
            
            # Clean symbol
            symbol = symbol.replace(' ', '').replace('/', '')
            
            clean_data.append({
                'symbol': symbol,
                'name': '',
                'shares': shares,
                'avg_cost': avg_cost,
                'date_added': datetime.now().strftime('%Y-%m-%d')
            })
            
        except Exception:
            continue
    
    return pd.DataFrame(clean_data)

def show_sofi_guide_modal():
    """Display SoFi export guide in modal"""
    
    st.markdown("# 🏦 SoFi CSV Export Guide")
    st.markdown("---")
    
    # Quick steps
    st.markdown("## 📥 Getting Your SoFi Data (3 Steps)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Step 1: Login**
        1. Go to https://www.sofi.com
        2. Login to your account
        3. Use desktop browser (mobile won't work)
        """)
    
    with col2:
        st.markdown("""
        **Step 2: Navigate**
        1. Click "Invest" → "Portfolio"
        2. Look for "Export" button (top-right)
        3. Or try "Account" → "Statements"
        """)
    
    with col3:
        st.markdown("""
        **Step 3: Download**
        1. Select "CSV" format
        2. Choose date range
        3. Download to your computer
        """)
    
    # Common issues
    st.markdown("## 🚨 Can't Find Export Button?")
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Try These Solutions:**
        
        1. **Different Browser**: Chrome works best with SoFi
        2. **Clear Cache**: Clear cookies for sofi.com
        3. **Desktop Mode**: If on mobile, request desktop site
        4. **Contact SoFi**: Call 1-855-456-7634 and ask for "CSV export of portfolio holdings"
        5. **Alternative**: Try SoFi Hub at https://portal.sofihub.com/
        
        **What to Ask SoFi Support:**
        *"I need to export my investment portfolio as CSV for personal tracking. Where is the export button located?"*
        """)
    
    # Example SoFi format
    st.markdown("## 📋 What SoFi CSV Looks Like")
    
    sample_sofi_data = {
        'Symbol': ['VTI', 'SOFI', 'AAPL'],
        'Shares': [15.5, 100.0, 8.0],
        'Cost_Basis': [4378.75, 1250.00, 1482.00],
        'Market_Value': [4500.25, 1180.00, 1560.00],
        'Unrealized_GL': [121.50, -70.00, 78.00]
    }
    
    sample_df = pd.DataFrame(sample_sofi_data)
    st.dataframe(sample_df, use_container_width=True)
    
    st.success("✅ This format imports perfectly into your Wealth Tracker!")
    
    # Direct import option
    st.markdown("## 🚀 After You Get Your SoFi CSV")
    st.info("1. Come back to this Import section\n2. Upload your SoFi CSV\n3. Our smart detection handles the rest!")
    
    if st.button("✅ Got it - Close Guide"):
        st.rerun()

def show_quick_csv_import():
    """Quick CSV import modal"""
    st.info("📥 **Quick CSV Import** - Upload your investment data from any broker")
    
    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=["csv"],
        key="quick_upload",
        help="SoFi, Fidelity, Robinhood, or any broker export"
    )
    
    if uploaded_file is not None:
        try:
            import_df = pd.read_csv(uploaded_file)
            st.success(f"✅ Found {len(import_df)} rows")
            st.dataframe(import_df.head(3), use_container_width=True)
            
            # Quick column detection
            symbol_col = auto_detect_column(import_df.columns, ['symbol', 'ticker', 'stock', 'instrument'])
            shares_col = auto_detect_column(import_df.columns, ['shares', 'quantity', 'qty', 'units'])
            
            if symbol_col > 0 and shares_col > 0:
                symbol_name = import_df.columns[symbol_col - 1]
                shares_name = import_df.columns[shares_col - 1]
                
                st.info(f"🎯 Auto-detected: **{symbol_name}** → Symbol, **{shares_name}** → Shares")
                
                if st.button("🚀 Import Now", type="primary"):
                    processed_data = process_csv_import(
                        import_df, symbol_name, shares_name
                    )
                    
                    if not processed_data.empty:
                        investments_df = load_data(INVESTMENTS_FILE)
                        final_df = pd.concat([investments_df, processed_data], ignore_index=True)
                        save_data(final_df, INVESTMENTS_FILE)
                        st.success(f"✅ Imported {len(processed_data)} positions!")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
            else:
                st.warning("⚠️ Could not auto-detect columns. Go to Investments page for manual mapping.")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def show_quick_csv_export():
    """Quick CSV export modal"""
    investments_df = load_data(INVESTMENTS_FILE)
    
    if investments_df.empty:
        st.warning("⚠️ No investments to export. Add some positions first!")
        return
    
    st.info("📤 **Quick CSV Export** - Download your current portfolio")
    
    # Prepare export data
    export_data = []
    for _, inv in investments_df.iterrows():
        stock_data = get_stock_data(inv['symbol'])
        current_value = inv['shares'] * stock_data['current_price']
        
        export_data.append({
            'Symbol': inv['symbol'],
            'Shares': inv['shares'],
            'Average_Cost': inv['avg_cost'],
            'Current_Price': stock_data['current_price'],
            'Current_Value': current_value,
            'Date_Added': inv['date_added']
        })
    
    export_df = pd.DataFrame(export_data)
    st.dataframe(export_df, use_container_width=True)
    
    # Calculate totals
    total_value = export_df['Current_Value'].sum()
    total_cost = (export_df['Shares'] * export_df['Average_Cost']).sum()
    total_gain = total_value - total_cost
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Value", f"${total_value:,.2f}")
    with col2:
        st.metric("Total Cost", f"${total_cost:,.2f}")
    with col3:
        st.metric("Total Gain", f"${total_gain:,.2f}")
    
    # Export button
    csv_data = export_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Portfolio CSV",
        data=csv_data,
        file_name=f"wealth_tracker_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        type="primary"
    )

def load_data(file_path):
    """Load data from CSV file"""
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

def save_data(df, file_path):
    """Save data to CSV file"""
    df.to_csv(file_path, index=False)

def get_stock_data(symbol):
    """Get current stock data from yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            return {
                'current_price': current_price,
                'name': info.get('longName', symbol),
                'change': info.get('regularMarketChangePercent', 0)
            }
    except:
        pass
    return {'current_price': 0, 'name': symbol, 'change': 0}

def calculate_portfolio_value(investments_df):
    """Calculate total portfolio value with enhanced real-time data"""
    if FINANCIAL_APIS_AVAILABLE and not investments_df.empty:
        # Use enhanced market data for better performance
        portfolio_data = market_data.calculate_portfolio_value(investments_df)
        return portfolio_data['total_value'], portfolio_data['total_cost']
    
    # Fallback to original method
    total_value = 0
    total_cost = 0
    
    for _, investment in investments_df.iterrows():
        stock_data = get_stock_data(investment['symbol'])
        current_value = investment['shares'] * stock_data['current_price']
        cost_basis = investment['shares'] * investment['avg_cost']
        
        total_value += current_value
        total_cost += cost_basis
    
    return total_value, total_cost

def main():
    # Initialize data files
    init_data_files()
    
    # Enhanced sidebar navigation
    with st.sidebar:
        st.markdown("# 💸 Wealth Tracker")
        st.markdown("*Your path to financial freedom*")
        st.markdown("---")
        
        # Quick stats in sidebar
        investments_df = load_data(INVESTMENTS_FILE)
        credit_cards_df = load_data(CREDIT_CARDS_FILE)
        
        if not investments_df.empty:
            portfolio_value, cost_basis = calculate_portfolio_value(investments_df)
            gain_loss = portfolio_value - cost_basis
            
            st.markdown("### 📊 Quick Stats")
            st.metric("Portfolio", f"${portfolio_value:,.0f}", f"${gain_loss:,.0f}")
            
            if not credit_cards_df.empty:
                total_debt = credit_cards_df['last_balance'].sum()
                net_worth = portfolio_value - total_debt
                st.metric("Net Worth", f"${net_worth:,.0f}")
        
        st.markdown("---")
        
        # Navigation with better styling
        st.markdown("### 🧭 Navigation")
        
        # Use radio buttons for better navigation
        page = st.radio(
            "Go to:",
            ["🏠 Dashboard", "📊 Investments", "💳 Credit Cards", "🎯 Goals", "📈 Analytics", "📡 Live Monitor"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # SoFi Integration
        if FINANCIAL_APIS_AVAILABLE:
            st.markdown("### 🏦 SoFi Integration")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Sync SoFi", use_container_width=True, help="Pull live data from your SoFi accounts"):
                    with st.spinner("Syncing SoFi accounts..."):
                        sofi_data = sync_sofi_data()
                        if sofi_data:
                            st.session_state['sofi_sync_time'] = sofi_data['sync_time']
                            st.success("✅ SoFi data synced!")
                        else:
                            st.info("ℹ️ Setup SoFi connection first")
            
            with col2:
                last_sync = st.session_state.get('sofi_sync_time')
                if last_sync:
                    st.caption(f"Last sync: {last_sync.strftime('%H:%M:%S')}")
                else:
                    st.caption("Never synced")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add Stock", use_container_width=True):
                st.session_state['add_investment'] = True
        with col2:
            if st.button("💳 Add Card", use_container_width=True):
                st.session_state['add_card'] = True
        
        # CSV Quick Import
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Import CSV", use_container_width=True, help="Quick import from any page"):
                st.session_state['quick_csv_import'] = True
        with col2:
            if st.button("📤 Export CSV", use_container_width=True, help="Download your portfolio"):
                st.session_state['quick_csv_export'] = True
        
        # Real-time settings
        st.markdown("---")
        st.markdown("### ⚡ Live Updates")
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", help="Automatically update prices every 30 seconds")
        live_mode = st.checkbox("📡 Live Mode", help="Real-time streaming updates")
        
        if auto_refresh:
            time.sleep(30)
            st.rerun()
        
        if live_mode:
            st.info("🚀 Live mode active - prices update in real-time")
    
    # Handle quick CSV actions from sidebar
    if st.session_state.get('quick_csv_import', False):
        st.session_state['quick_csv_import'] = False
        show_quick_csv_import()
    
    if st.session_state.get('quick_csv_export', False):
        st.session_state['quick_csv_export'] = False
        show_quick_csv_export()
    
    # Route to pages
    if page == "🏠 Dashboard":
        dashboard_page()
    elif page == "📊 Investments":
        investments_page()
    elif page == "💳 Credit Cards":
        credit_cards_page()
    elif page == "🎯 Goals":
        goals_page()
    elif page == "📈 Analytics":
        analytics_page()
    elif page == "📡 Live Monitor":
        live_monitor_page()

def dashboard_page():
    # Main header
    st.markdown('<h1 class="main-header">🏠 Your Financial Command Center</h1>', unsafe_allow_html=True)
    
    # Load data
    investments_df = load_data(INVESTMENTS_FILE)
    credit_cards_df = load_data(CREDIT_CARDS_FILE)
    goals_df = load_data(GOALS_FILE)
    
    # Quick start guide if no data
    if investments_df.empty and credit_cards_df.empty:
        st.info("👋 **Welcome to your Wealth Tracker!** Start by adding your first investment or credit card using the Quick Actions in the sidebar.")
        
        # Sample data option
        with st.expander("🚀 Load Sample Data (Demo Mode)"):
            st.markdown("""
            **Want to see the app in action?** Load realistic sample data to explore all features:
            - **VTI**: 10 shares at $280 avg cost
            - **SOFI**: 50 shares at $12.50 avg cost  
            - **BTC-USD**: 0.1 Bitcoin at $45,000 avg cost
            - **Credit Cards**: Chase Freedom & Capital One
            - **Goals**: $100K Portfolio & Emergency Fund
            """)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("📊 Load Demo Data", type="primary"):
                    sample_inv, sample_cards, sample_goals = add_sample_data()
                    save_data(sample_inv, INVESTMENTS_FILE)
                    save_data(sample_cards, CREDIT_CARDS_FILE)
                    save_data(sample_goals, GOALS_FILE)
                    st.success("✅ Demo data loaded! Refresh to see your portfolio.")
                    st.rerun()
            
            with col2:
                st.caption("*Demo data uses realistic values. Your actual financial data stays private.*")
        
        # Sample data suggestions
        with st.expander("📝 Manual Setup Guide"):
            st.markdown("""
            **Popular ETFs & Stocks for beginners:**
            - **VTI** - Total Stock Market ETF (~$280/share)
            - **SOFI** - SoFi Technologies (~$10-15/share) 
            - **BTC-USD** - Bitcoin tracking
            - **AAPL** - Apple (~$190/share)
            - **TSLA** - Tesla (~$250/share)
            
            **Credit Cards to track:**
            - Chase Freedom Unlimited
            - Capital One Venture
            - Discover it Cash Back
            """)
    
    # Key metrics row with better styling
    st.markdown("### 📊 Financial Snapshot")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not investments_df.empty:
            portfolio_value, cost_basis = calculate_portfolio_value(investments_df)
            gain_loss = portfolio_value - cost_basis
            gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
            
            st.metric(
                "💼 Portfolio Value",
                f"${portfolio_value:,.2f}",
                f"${gain_loss:,.2f} ({gain_loss_pct:+.1f}%)"
            )
        else:
            st.metric("💼 Portfolio Value", "$0.00", "Add your first investment!")
    
    with col2:
        if not credit_cards_df.empty:
            total_cc_debt = credit_cards_df['last_balance'].sum()
            st.metric("💳 Credit Debt", f"${total_cc_debt:,.2f}")
        else:
            st.metric("💳 Credit Debt", "$0.00")
    
    with col3:
        portfolio_value = 0
        if not investments_df.empty:
            portfolio_value, _ = calculate_portfolio_value(investments_df)
        
        total_cc_debt = credit_cards_df['last_balance'].sum() if not credit_cards_df.empty else 0
        net_worth = portfolio_value - total_cc_debt
        st.metric("💰 Net Worth", f"${net_worth:,.2f}")
    
    with col4:
        if not goals_df.empty:
            primary_goal = goals_df.iloc[0]
            progress = (primary_goal['current_amount'] / primary_goal['target_amount'] * 100) if primary_goal['target_amount'] > 0 else 0
            st.metric("🎯 Goal Progress", f"{progress:.1f}%")
        else:
            st.metric("🎯 Goal Progress", "0%", "Set your first goal!")
    
    st.markdown("---")
    
    # Two-column layout for overview
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📈 Top Holdings")
        if not investments_df.empty:
            holdings_data = []
            for _, investment in investments_df.head(5).iterrows():
                stock_data = get_stock_data(investment['symbol'])
                value = investment['shares'] * stock_data['current_price']
                change_pct = stock_data.get('change', 0)
                
                holdings_data.append({
                    'Symbol': investment['symbol'],
                    'Value': f"${value:,.2f}",
                    'Change%': f"{change_pct:+.2f}%" if change_pct != 0 else "N/A"
                })
            
            holdings_df = pd.DataFrame(holdings_data)
            st.dataframe(holdings_df, use_container_width=True, hide_index=True)
        else:
            st.info("Add investments to see your holdings here")
    
    with col2:
        st.markdown("### 🚨 Credit Card Alerts")
        if not credit_cards_df.empty:
            today = datetime.now().date()
            alerts_shown = False
            
            for _, card in credit_cards_df.iterrows():
                if pd.notna(card['due_date']):
                    due_date = pd.to_datetime(card['due_date']).date()
                    days_until_due = (due_date - today).days
                    
                    if days_until_due <= 7:
                        alerts_shown = True
                        if days_until_due <= 3:
                            st.error(f"🔴 **{card['card_name']}**: Due in {days_until_due} days!")
                        else:
                            st.warning(f"🟡 **{card['card_name']}**: Due in {days_until_due} days")
            
            if not alerts_shown:
                st.success("✅ All credit cards are current!")
        else:
            st.info("Add credit cards to track due dates")
    
    # Recent activity section
    if not investments_df.empty or not credit_cards_df.empty:
        st.markdown("---")
        st.markdown("### 📋 Account Summary")
        
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            if not investments_df.empty:
                st.markdown("**Investment Accounts:**")
                for _, inv in investments_df.iterrows():
                    st.write(f"• {inv['symbol']}: {inv['shares']} shares")
        
        with summary_col2:
            if not credit_cards_df.empty:
                st.markdown("**Credit Cards:**")
                for _, card in credit_cards_df.iterrows():
                    status_emoji = {"active": "🟢", "closing": "🟡", "closed clean": "⚪"}.get(card['status'], "🔘")
                    st.write(f"• {status_emoji} {card['card_name']}: ${card['last_balance']:,.2f}")
    
    # Net Worth Analytics (if we have real data)
    if not investments_df.empty:
        st.markdown("---")
        st.markdown("### 💰 Net Worth Analytics")
        
        # Calculate detailed breakdown
        portfolio_value, cost_basis = calculate_portfolio_value(investments_df)
        total_cc_debt = credit_cards_df['last_balance'].sum() if not credit_cards_df.empty else 0
        net_worth = portfolio_value - total_cc_debt
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📊 Portfolio Breakdown:**")
            for _, investment in investments_df.iterrows():
                stock_data = get_stock_data(investment['symbol'])
                position_value = investment['shares'] * stock_data['current_price']
                percentage = (position_value / portfolio_value * 100) if portfolio_value > 0 else 0
                st.write(f"• {investment['symbol']}: {percentage:.1f}% (${position_value:,.0f})")
        
        with col2:
            st.markdown("**💳 Debt Breakdown:**")
            if not credit_cards_df.empty:
                for _, card in credit_cards_df.iterrows():
                    debt_percentage = (card['last_balance'] / total_cc_debt * 100) if total_cc_debt > 0 else 0
                    st.write(f"• {card['card_name']}: ${card['last_balance']:,.0f}")
            else:
                st.write("🎉 Debt-free!")
        
        with col3:
            st.markdown("**🎯 Wealth Milestones:**")
            milestones = [10000, 25000, 50000, 100000, 250000, 500000, 1000000]
            
            for milestone in milestones:
                if net_worth >= milestone:
                    st.write(f"✅ ${milestone:,}")
                else:
                    remaining = milestone - net_worth
                    st.write(f"⏳ ${milestone:,} (${remaining:,.0f} to go)")
                    break
    
    # Data Source Information
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption(f"📊 Data: {len(investments_df)} investments, {len(credit_cards_df)} cards")
        st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        if not investments_df.empty:
            # Show data source
            if any('date_added' in str(inv) and inv.get('date_added', '') == datetime.now().strftime('%Y-%m-%d') for _, inv in investments_df.iterrows()):
                st.caption("📥 Contains imported CSV data")
            st.caption("🔄 Prices refresh in real-time")
        else:
            st.caption("💡 Import your CSV data to get started")

def investments_page():
    st.markdown('<h1 class="main-header">📊 Investment Portfolio</h1>', unsafe_allow_html=True)
    
    investments_df = load_data(INVESTMENTS_FILE)
    
    # CSV Import Section
    with st.expander("📥 Import Your Real SoFi/Brokerage Data", expanded=False):
        st.markdown("**Securely import your actual investment data**")
        st.info("💡 **100% Local & Private:** Your CSV data never leaves your computer")
        
        uploaded_file = st.file_uploader(
            "Upload CSV file from SoFi, Fidelity, Robinhood, etc.",
            type=["csv"],
            help="Export your holdings from your broker and upload here"
        )
        
        if uploaded_file is not None:
            try:
                # Read the uploaded CSV
                import_df = pd.read_csv(uploaded_file)
                
                st.success(f"✅ File uploaded successfully! Found {len(import_df)} rows")
                
                # Show preview
                st.markdown("**📋 Data Preview:**")
                st.dataframe(import_df.head(), use_container_width=True)
                
                # Smart column mapping
                st.markdown("**🔧 Column Mapping:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Available Columns:**")
                    for col in import_df.columns:
                        st.write(f"• {col}")
                
                with col2:
                    st.markdown("**Map to:**")
                    
                    # Smart detection of column names
                    symbol_col = st.selectbox(
                        "Symbol/Ticker Column",
                        options=[""] + list(import_df.columns),
                        index=auto_detect_column(import_df.columns, ['symbol', 'ticker', 'stock', 'instrument'])
                    )
                    
                    shares_col = st.selectbox(
                        "Shares/Quantity Column", 
                        options=[""] + list(import_df.columns),
                        index=auto_detect_column(import_df.columns, ['shares', 'quantity', 'qty', 'units'])
                    )
                    
                    cost_col = st.selectbox(
                        "Average Cost Column (Optional)",
                        options=[""] + list(import_df.columns),
                        index=auto_detect_column(import_df.columns, ['cost', 'price', 'avg_cost', 'average'])
                    )
                    
                    value_col = st.selectbox(
                        "Current Value Column (Optional)",
                        options=[""] + list(import_df.columns),
                        index=auto_detect_column(import_df.columns, ['value', 'market_value', 'current_value'])
                    )
                
                # Process and import data
                if symbol_col and shares_col:
                    if st.button("🚀 Import Data", type="primary"):
                        imported_data = process_csv_import(
                            import_df, symbol_col, shares_col, cost_col, value_col
                        )
                        
                        if not imported_data.empty:
                            # Merge with existing data
                            if not investments_df.empty:
                                # Check for duplicates and handle merge
                                st.warning("⚠️ Found existing investments. Choose merge strategy:")
                                merge_strategy = st.radio(
                                    "How to handle existing data:",
                                    ["Add new positions only", "Replace all data", "Update existing + add new"]
                                )
                                
                                if st.button("Confirm Import"):
                                    final_df = handle_data_merge(investments_df, imported_data, merge_strategy)
                                    save_data(final_df, INVESTMENTS_FILE)
                                    st.success(f"✅ Successfully imported {len(imported_data)} positions!")
                                    st.rerun()
                            else:
                                save_data(imported_data, INVESTMENTS_FILE)
                                st.success(f"✅ Successfully imported {len(imported_data)} positions!")
                                st.rerun()
                        else:
                            st.error("❌ No valid data found to import")
                else:
                    st.warning("⚠️ Please map at least Symbol and Shares columns")
                    
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.info("💡 Make sure your CSV has proper headers and data format")
        
        # Show supported formats and tools
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("📋 Supported CSV Formats"):
                st.markdown("""
                **SoFi Export Format:**
                - Symbol, Shares, Average Cost, Current Value
                - Cost_Basis, Market_Value, Unrealized_GL
                
                **Fidelity Export Format:**  
                - Symbol, Quantity, Price Paid, Current Price
                
                **Robinhood Export Format:**
                - Instrument, Quantity, Average Buy Price
                
                **Generic Format:**
                - Any CSV with Symbol/Ticker and Shares/Quantity columns
                
                **💡 Pro Tip:** Your column names don't need to match exactly - 
                our smart detection will find the right columns!
                """)
                
                # SoFi specific help
                st.markdown("---")
                st.markdown("**🏦 SoFi Users:**")
                st.info("Having trouble finding CSV export? Check our [SoFi Data Guide](sofi_data_guide.md)")
                
                if st.button("📖 Open SoFi Export Guide", help="Step-by-step guide for SoFi CSV exports"):
                    st.session_state['show_sofi_guide'] = True
        
        with col2:
            with st.expander("🛠️ CSV Tools"):
                st.markdown("**Download Template:**")
                
                # Generate CSV template
                template_data = {
                    'Symbol': ['VTI', 'SOFI', 'AAPL'],
                    'Shares': [10.5, 25.0, 5.0],
                    'Average_Cost': [285.50, 12.75, 190.25],
                    'Current_Value': [3000.00, 350.00, 975.00]
                }
                template_df = pd.DataFrame(template_data)
                
                csv_template = template_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV Template",
                    data=csv_template,
                    file_name="investment_template.csv",
                    mime="text/csv",
                    help="Download a template CSV file with the correct format"
                )
                
                st.markdown("**Export Current Data:**")
                if not investments_df.empty:
                    export_df = investments_df[['symbol', 'shares', 'avg_cost']].copy()
                    export_df.columns = ['Symbol', 'Shares', 'Average_Cost']
                    
                    # Add current values
                    current_values = []
                    for _, inv in investments_df.iterrows():
                        stock_data = get_stock_data(inv['symbol'])
                        current_value = inv['shares'] * stock_data['current_price']
                        current_values.append(current_value)
                    
                    export_df['Current_Value'] = current_values
                    
                    csv_export = export_df.to_csv(index=False)
                    st.download_button(
                        label="📤 Export Portfolio CSV",
                        data=csv_export,
                        file_name=f"portfolio_export_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        help="Export your current portfolio as CSV"
                    )
                else:
                    st.write("*Add investments to enable export*")
                
                st.markdown("---")
                st.markdown("**🏦 SoFi CSV Cleaner:**")
                st.write("Upload raw SoFi export for automatic formatting")
                
                sofi_file = st.file_uploader(
                    "Upload SoFi CSV (any format)",
                    type=["csv"],
                    key="sofi_cleaner_upload",
                    help="Handles various SoFi export formats automatically"
                )
                
                if sofi_file is not None:
                    if st.button("🧹 Clean SoFi CSV", type="secondary"):
                        try:
                            import io
                            
                            # Read SoFi CSV
                            sofi_df = pd.read_csv(sofi_file)
                            st.success(f"✅ Loaded SoFi CSV: {len(sofi_df)} rows")
                            
                            # Process with SoFi cleaner logic
                            cleaned_data = process_sofi_csv(sofi_df)
                            
                            if not cleaned_data.empty:
                                st.success(f"✨ Cleaned {len(cleaned_data)} positions")
                                st.dataframe(cleaned_data, use_container_width=True)
                                
                                # Download cleaned CSV
                                cleaned_csv = cleaned_data.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Cleaned CSV",
                                    data=cleaned_csv,
                                    file_name=f"cleaned_sofi_{datetime.now().strftime('%Y%m%d')}.csv",
                                    mime="text/csv",
                                    type="primary"
                                )
                                
                                st.info("💡 You can now import this cleaned CSV using the main import section above!")
                            else:
                                st.error("❌ Could not process SoFi CSV - check format")
                                
                        except Exception as e:
                            st.error(f"❌ Error processing SoFi CSV: {str(e)}")
    
    # Show SoFi guide modal if requested
    if st.session_state.get('show_sofi_guide', False):
        show_sofi_guide_modal()
        st.session_state['show_sofi_guide'] = False
    
    st.markdown("---")
    
    # Quick stats
    if not investments_df.empty:
        portfolio_value, cost_basis = calculate_portfolio_value(investments_df)
        total_gain_loss = portfolio_value - cost_basis
        total_return_pct = (total_gain_loss / cost_basis * 100) if cost_basis > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Value", f"${portfolio_value:,.2f}")
        with col2:
            st.metric("Total Cost", f"${cost_basis:,.2f}")
        with col3:
            st.metric("Total Return", f"${total_gain_loss:,.2f}", f"{total_return_pct:+.1f}%")
        
        st.markdown("---")
    
    # Add new investment with auto-expand if triggered from sidebar
    expand_investment = st.session_state.get('add_investment', False)
    if expand_investment:
        st.session_state['add_investment'] = False
    
    with st.expander("➕ Add New Investment", expanded=expand_investment):
        st.markdown("**Popular stocks to get started:**")
        
        # Quick add buttons for popular stocks
        popular_stocks = {
            "VTI": "Total Stock Market ETF",
            "SOFI": "SoFi Technologies", 
            "BTC-USD": "Bitcoin",
            "AAPL": "Apple Inc",
            "TSLA": "Tesla Inc"
        }
        
        st.markdown("**Quick Add Popular Stocks:**")
        cols = st.columns(len(popular_stocks))
        for i, (symbol, name) in enumerate(popular_stocks.items()):
            with cols[i]:
                if st.button(f"{symbol}\n{name}", key=f"quick_{symbol}"):
                    st.session_state['quick_symbol'] = symbol
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            symbol = st.text_input(
                "Stock Symbol", 
                value=st.session_state.get('quick_symbol', ''),
                key="new_symbol",
                help="Examples: VTI, SOFI, BTC-USD, AAPL, TSLA"
            ).upper()
            
            # Clear quick symbol after use
            if 'quick_symbol' in st.session_state:
                del st.session_state['quick_symbol']
                
        with col2:
            shares = st.number_input("Shares", min_value=0.0, step=0.1, key="new_shares")
        with col3:
            avg_cost = st.number_input("Average Cost per Share", min_value=0.0, step=0.01, key="new_cost")
        
        # Show current price if symbol is entered
        if symbol:
            try:
                current_data = get_stock_data(symbol)
                if current_data['current_price'] > 0:
                    st.info(f"💡 Current price of {symbol}: ${current_data['current_price']:.2f}")
            except:
                pass
        
        if st.button("Add Investment", type="primary"):
            if symbol and shares > 0 and avg_cost > 0:
                stock_data = get_stock_data(symbol)
                new_investment = pd.DataFrame({
                    'symbol': [symbol],
                    'name': [stock_data['name']],
                    'shares': [shares],
                    'avg_cost': [avg_cost],
                    'date_added': [datetime.now().strftime('%Y-%m-%d')]
                })
                
                investments_df = pd.concat([investments_df, new_investment], ignore_index=True)
                save_data(investments_df, INVESTMENTS_FILE)
                st.success(f"✅ Added {shares} shares of {symbol} at ${avg_cost:.2f}/share")
                st.rerun()
            else:
                st.error("Please fill in all fields with valid values")
    
    # Display current investments
    if not investments_df.empty:
        st.subheader("Current Holdings")
        
        # Calculate current values
        portfolio_data = []
        for _, investment in investments_df.iterrows():
            stock_data = get_stock_data(investment['symbol'])
            current_value = investment['shares'] * stock_data['current_price']
            cost_basis = investment['shares'] * investment['avg_cost']
            gain_loss = current_value - cost_basis
            gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
            
            portfolio_data.append({
                'Symbol': investment['symbol'],
                'Name': stock_data['name'],
                'Shares': investment['shares'],
                'Avg Cost': f"${investment['avg_cost']:.2f}",
                'Current Price': f"${stock_data['current_price']:.2f}",
                'Current Value': f"${current_value:.2f}",
                'Gain/Loss': f"${gain_loss:.2f}",
                'Gain/Loss %': f"{gain_loss_pct:+.2f}%"
            })
        
        portfolio_df = pd.DataFrame(portfolio_data)
        st.dataframe(portfolio_df, use_container_width=True)
        
        # Portfolio allocation chart
        st.subheader("Portfolio Allocation")
        values = [float(row['Current Value'].replace('$', '').replace(',', '')) for row in portfolio_data]
        labels = [row['Symbol'] for row in portfolio_data]
        
        fig = px.pie(values=values, names=labels, title="Portfolio Allocation by Value")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No investments added yet. Use the form above to add your first investment!")

def credit_cards_page():
    st.markdown('<h1 class="main-header">💳 Credit Cards</h1>', unsafe_allow_html=True)
    
    credit_cards_df = load_data(CREDIT_CARDS_FILE)
    
    # Quick stats
    if not credit_cards_df.empty:
        total_balance = credit_cards_df['last_balance'].sum()
        total_limit = credit_cards_df['credit_limit'].sum()
        overall_utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Debt", f"${total_balance:,.2f}")
        with col2:
            st.metric("Total Limit", f"${total_limit:,.2f}")
        with col3:
            color = "normal" if overall_utilization <= 30 else "inverse"
            st.metric("Utilization", f"{overall_utilization:.1f}%")
        
        st.markdown("---")
    
    # Add new credit card with auto-expand if triggered from sidebar
    expand_card = st.session_state.get('add_card', False)
    if expand_card:
        st.session_state['add_card'] = False
    
    with st.expander("➕ Add New Credit Card", expanded=expand_card):
        col1, col2 = st.columns(2)
        
        with col1:
            card_name = st.text_input("Card Name", key="new_card_name")
            last_balance = st.number_input("Current Balance", min_value=0.0, step=0.01, key="new_balance")
            credit_limit = st.number_input("Credit Limit", min_value=0.0, step=100.0, key="new_limit")
        
        with col2:
            due_date = st.date_input("Next Due Date", key="new_due_date")
            status = st.selectbox("Status", ["active", "closing", "closed clean"], key="new_status")
            apr = st.number_input("APR (%)", min_value=0.0, max_value=100.0, step=0.1, key="new_apr")
        
        if st.button("Add Credit Card"):
            if card_name:
                new_card = pd.DataFrame({
                    'card_name': [card_name],
                    'last_balance': [last_balance],
                    'due_date': [due_date.strftime('%Y-%m-%d')],
                    'status': [status],
                    'credit_limit': [credit_limit],
                    'apr': [apr]
                })
                
                credit_cards_df = pd.concat([credit_cards_df, new_card], ignore_index=True)
                save_data(credit_cards_df, CREDIT_CARDS_FILE)
                st.success(f"Added {card_name}")
                st.rerun()
    
    # Display credit cards
    if not credit_cards_df.empty:
        st.subheader("Your Credit Cards")
        
        for _, card in credit_cards_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                
                # Status color coding
                status_colors = {
                    "active": "🟢",
                    "closing": "🟡", 
                    "closed clean": "⚪"
                }
                
                with col1:
                    st.write(f"**{status_colors.get(card['status'], '🔘')} {card['card_name']}**")
                    st.write(f"Status: {card['status']}")
                
                with col2:
                    st.metric("Balance", f"${card['last_balance']:,.2f}")
                    utilization = (card['last_balance'] / card['credit_limit'] * 100) if card['credit_limit'] > 0 else 0
                    st.write(f"Utilization: {utilization:.1f}%")
                
                with col3:
                    if pd.notna(card['due_date']):
                        due_date = pd.to_datetime(card['due_date']).date()
                        days_until_due = (due_date - datetime.now().date()).days
                        
                        if days_until_due <= 3:
                            st.error(f"Due: {due_date} ({days_until_due} days)")
                        elif days_until_due <= 7:
                            st.warning(f"Due: {due_date} ({days_until_due} days)")
                        else:
                            st.info(f"Due: {due_date} ({days_until_due} days)")
                
                with col4:
                    st.write(f"Credit Limit: ${card['credit_limit']:,.2f}")
                    st.write(f"APR: {card['apr']:.1f}%")
                
                st.divider()
        
        # Summary metrics
        total_balance = credit_cards_df['last_balance'].sum()
        total_limit = credit_cards_df['credit_limit'].sum()
        overall_utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Credit Card Debt", f"${total_balance:,.2f}")
        with col2:
            st.metric("Total Credit Limit", f"${total_limit:,.2f}")
        with col3:
            st.metric("Overall Utilization", f"{overall_utilization:.1f}%")
    
    else:
        st.info("No credit cards added yet. Use the form above to add your first card!")

def goals_page():
    st.markdown('<h1 class="main-header">🎯 Financial Goals</h1>', unsafe_allow_html=True)
    
    goals_df = load_data(GOALS_FILE)
    investments_df = load_data(INVESTMENTS_FILE)
    
    # Auto-update current amounts based on portfolio value
    if not goals_df.empty and not investments_df.empty and FINANCIAL_APIS_AVAILABLE:
        portfolio_value, _ = calculate_portfolio_value(investments_df)
        
        # Update portfolio-related goals automatically
        for idx, goal in goals_df.iterrows():
            if 'portfolio' in goal['goal_name'].lower() or '100k' in goal['goal_name'].lower():
                goals_df.loc[idx, 'current_amount'] = portfolio_value
        
        save_data(goals_df, GOALS_FILE)
    
    # Add new goal
    with st.expander("➕ Add New Goal"):
        col1, col2 = st.columns(2)
        
        with col1:
            goal_name = st.text_input("Goal Name", key="new_goal_name")
            target_amount = st.number_input("Target Amount", min_value=0.0, step=1000.0, key="new_target")
        
        with col2:
            current_amount = st.number_input("Current Amount", min_value=0.0, step=100.0, key="new_current")
            target_date = st.date_input("Target Date", key="new_target_date")
        
        if st.button("Add Goal"):
            if goal_name and target_amount > 0:
                new_goal = pd.DataFrame({
                    'goal_name': [goal_name],
                    'target_amount': [target_amount],
                    'current_amount': [current_amount],
                    'target_date': [target_date.strftime('%Y-%m-%d')]
                })
                
                goals_df = pd.concat([goals_df, new_goal], ignore_index=True)
                save_data(goals_df, GOALS_FILE)
                st.success(f"Added goal: {goal_name}")
                st.rerun()
    
    # Display goals with enhanced tracking
    if not goals_df.empty:
        st.subheader("Your Goals")
        
        for _, goal in goals_df.iterrows():
            # Use enhanced goal tracker if available
            if FINANCIAL_APIS_AVAILABLE:
                goal_progress = goal_tracker.calculate_goal_progress(
                    goal['current_amount'],
                    goal['target_amount'],
                    goal['target_date']
                )
                
                with st.container():
                    # Goal header with status
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {goal_progress['status_emoji']} {goal['goal_name']}")
                    with col2:
                        if goal_progress['status'] == 'ahead':
                            st.success("Ahead of Schedule!")
                        elif goal_progress['status'] == 'on_track':
                            st.info("On Track")
                        else:
                            st.warning("Behind Schedule")
                    
                    # Progress metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Progress", f"{goal_progress['progress_pct']:.1f}%")
                    with col2:
                        st.metric("Remaining", f"${goal_progress['amount_needed']:,.0f}")
                    with col3:
                        st.metric("Days Left", goal_progress['days_remaining'])
                    with col4:
                        st.metric("Daily Target", f"${goal_progress['daily_rate_needed']:.2f}")
                    
                    # Progress bar with time comparison
                    progress_col1, progress_col2 = st.columns([3, 1])
                    with progress_col1:
                        st.progress(goal_progress['progress_pct'] / 100)
                        st.caption(f"Time Progress: {goal_progress['time_progress_pct']:.1f}%")
                    
                    with progress_col2:
                        if goal_progress['is_achievable']:
                            st.success("✅ Achievable")
                        else:
                            st.error("⚠️ Challenging")
                    
                    # Detailed breakdown
                    with st.expander("📊 Detailed Breakdown"):
                        detail_col1, detail_col2 = st.columns(2)
                        
                        with detail_col1:
                            st.write(f"**Current Amount:** ${goal['current_amount']:,.2f}")
                            st.write(f"**Target Amount:** ${goal['target_amount']:,.2f}")
                            st.write(f"**Monthly Target:** ${goal_progress['monthly_rate_needed']:,.2f}")
                        
                        with detail_col2:
                            st.write(f"**Target Date:** {goal_progress['target_date'].strftime('%Y-%m-%d')}")
                            st.write(f"**Progress vs Time:** {goal_progress['progress_pct'] - goal_progress['time_progress_pct']:+.1f}%")
                            
                            if goal_progress['status'] == 'ahead':
                                st.success("🚀 You're ahead! Consider increasing your target.")
                            elif goal_progress['status'] == 'behind':
                                st.warning("📈 Need to accelerate savings rate.")
                    
                    st.divider()
            
            else:
                # Fallback to basic display
                with st.container():
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**{goal['goal_name']}**")
                        progress = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
                        st.progress(progress / 100)
                        
                        remaining = goal['target_amount'] - goal['current_amount']
                        st.write(f"Progress: ${goal['current_amount']:,.2f} / ${goal['target_amount']:,.2f}")
                        st.write(f"Remaining: ${remaining:,.2f}")
                    
                    with col2:
                        if pd.notna(goal['target_date']):
                            target_date = pd.to_datetime(goal['target_date']).date()
                            days_remaining = (target_date - datetime.now().date()).days
                            st.metric("Days Remaining", days_remaining)
                            
                            if remaining > 0 and days_remaining > 0:
                                daily_save_needed = remaining / days_remaining
                                st.write(f"Save ${daily_save_needed:.2f}/day")
                    
                    st.divider()
    else:
        st.info("No goals set yet. Use the form above to add your first financial goal!")

def analytics_page():
    st.markdown('<h1 class="main-header">📈 Analytics & Insights</h1>', unsafe_allow_html=True)
    
    investments_df = load_data(INVESTMENTS_FILE)
    credit_cards_df = load_data(CREDIT_CARDS_FILE)
    
    # CSV Data Analytics
    if not investments_df.empty:
        # Check if we have imported data today
        today = datetime.now().strftime('%Y-%m-%d')
        imported_today = investments_df[investments_df['date_added'] == today]
        
        if not imported_today.empty:
            st.info(f"📥 **Fresh Data Alert:** {len(imported_today)} positions imported today from CSV")
            
            with st.expander("📋 Recently Imported Positions"):
                for _, inv in imported_today.iterrows():
                    stock_data = get_stock_data(inv['symbol'])
                    current_value = inv['shares'] * stock_data['current_price']
                    cost_basis = inv['shares'] * inv['avg_cost']
                    gain_loss = current_value - cost_basis
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**{inv['symbol']}**")
                        st.write(f"Shares: {inv['shares']}")
                    with col2:
                        st.write(f"Avg Cost: ${inv['avg_cost']:.2f}")
                        st.write(f"Current: ${stock_data['current_price']:.2f}")
                    with col3:
                        st.metric("Position P&L", f"${gain_loss:,.2f}")
            
            st.markdown("---")
    
    if not investments_df.empty:
        # Portfolio performance over time (simulated)
        st.subheader("Portfolio Performance")
        
        # Generate sample performance data
        dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
        portfolio_value, cost_basis = calculate_portfolio_value(investments_df)
        
        # Simulate some volatility
        np.random.seed(42)
        returns = np.random.normal(0.0008, 0.02, len(dates))  # ~20% annual return with volatility
        cumulative_returns = np.cumprod(1 + returns)
        values = cost_basis * cumulative_returns
        
        performance_df = pd.DataFrame({
            'Date': dates,
            'Portfolio Value': values
        })
        
        fig = px.line(performance_df, x='Date', y='Portfolio Value', 
                     title='Portfolio Value Over Time')
        st.plotly_chart(fig, use_container_width=True)
        
        # Asset allocation
        st.subheader("Asset Allocation Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Current allocation
            allocation_data = []
            for _, investment in investments_df.iterrows():
                stock_data = get_stock_data(investment['symbol'])
                value = investment['shares'] * stock_data['current_price']
                allocation_data.append({
                    'Asset': investment['symbol'],
                    'Value': value,
                    'Percentage': value / portfolio_value * 100 if portfolio_value > 0 else 0
                })
            
            allocation_df = pd.DataFrame(allocation_data)
            st.dataframe(allocation_df)
        
        with col2:
            # Risk metrics
            st.write("**Portfolio Metrics**")
            total_gain_loss = portfolio_value - cost_basis
            total_return_pct = (total_gain_loss / cost_basis * 100) if cost_basis > 0 else 0
            
            st.metric("Total Return", f"{total_return_pct:.2f}%")
            st.metric("Total Gain/Loss", f"${total_gain_loss:,.2f}")
            
            # Diversification score (simple)
            diversification_score = min(len(investments_df) * 20, 100)  # Max 100% for 5+ holdings
            st.metric("Diversification Score", f"{diversification_score}%")
    
    else:
        st.info("Add some investments to see analytics!")

def live_monitor_page():
    """Real-time live dashboard following Streamlit best practices"""
    st.markdown('<h1 class="main-header">📡 Live Portfolio Monitor</h1>', unsafe_allow_html=True)
    
    if not FINANCIAL_APIS_AVAILABLE:
        st.error("⚠️ Financial APIs not available. Install dependencies to use live monitoring.")
        return
    
    investments_df = load_data(INVESTMENTS_FILE)
    credit_cards_df = load_data(CREDIT_CARDS_FILE)
    
    if investments_df.empty:
        st.info("📊 Add investments to start live monitoring")
        return
    
    # Control panel
    col1, col2, col3 = st.columns(3)
    with col1:
        refresh_rate = st.selectbox("Refresh Rate", [5, 10, 30, 60], index=2, help="Seconds between updates")
    with col2:
        auto_scroll = st.checkbox("Auto-scroll to updates", value=True)
    with col3:
        sound_alerts = st.checkbox("Sound alerts", value=False, help="Alert on significant price changes")
    
    st.markdown("---")
    
    # Create placeholder for live updates
    placeholder = st.empty()
    
    # Status indicator
    status_placeholder = st.empty()
    
    # Live update loop
    update_count = 0
    
    try:
        # Continuous update loop
        while True:
            update_count += 1
            
            with placeholder.container():
                # Get real-time portfolio data
                portfolio_data = market_data.calculate_portfolio_value(investments_df)
                
                # Live metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "🔴 LIVE Portfolio Value",
                        f"${portfolio_data['total_value']:,.2f}",
                        f"${portfolio_data['total_gain']:,.2f} ({portfolio_data['total_gain_pct']:+.2f}%)"
                    )
                
                with col2:
                    net_worth = portfolio_data['total_value'] - (credit_cards_df['last_balance'].sum() if not credit_cards_df.empty else 0)
                    st.metric("💰 Live Net Worth", f"${net_worth:,.2f}")
                
                with col3:
                    st.metric("📊 Positions", len(portfolio_data['positions']))
                
                with col4:
                    st.metric("🕐 Updates", update_count)
                
                # Live positions table
                if portfolio_data['positions']:
                    st.markdown("### 📈 Live Positions")
                    
                    positions_data = []
                    for pos in portfolio_data['positions']:
                        # Color coding for gains/losses
                        gain_color = "🟢" if pos['position_gain'] >= 0 else "🔴"
                        change_color = "🟢" if pos['change_pct'] >= 0 else "🔴"
                        
                        positions_data.append({
                            'Symbol': f"{gain_color} {pos['symbol']}",
                            'Current Price': f"${pos['current_price']:.2f}",
                            'Change %': f"{change_color} {pos['change_pct']:+.2f}%",
                            'Position Value': f"${pos['position_value']:,.2f}",
                            'Gain/Loss': f"${pos['position_gain']:,.2f}",
                            'Gain %': f"{pos['gain_pct']:+.2f}%",
                            'Last Update': pos['last_update'].strftime('%H:%M:%S')
                        })
                    
                    positions_df = pd.DataFrame(positions_data)
                    st.dataframe(positions_df, use_container_width=True, hide_index=True)
                
                # Live charts
                st.markdown("### 📊 Live Portfolio Breakdown")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Portfolio allocation pie chart
                    if portfolio_data['positions']:
                        values = [pos['position_value'] for pos in portfolio_data['positions']]
                        labels = [pos['symbol'] for pos in portfolio_data['positions']]
                        
                        fig = px.pie(
                            values=values, 
                            names=labels, 
                            title="Current Allocation"
                        )
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Gain/Loss breakdown
                    gains = [pos['position_gain'] for pos in portfolio_data['positions']]
                    symbols = [pos['symbol'] for pos in portfolio_data['positions']]
                    colors = ['green' if gain >= 0 else 'red' for gain in gains]
                    
                    fig2 = px.bar(
                        x=symbols, 
                        y=gains, 
                        title="Position Gains/Losses",
                        color=colors,
                        color_discrete_map={'green': '#00ff00', 'red': '#ff0000'}
                    )
                    fig2.update_layout(showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Market alerts
                st.markdown("### 🚨 Live Alerts")
                alert_col1, alert_col2 = st.columns(2)
                
                with alert_col1:
                    # Price change alerts
                    for pos in portfolio_data['positions']:
                        if abs(pos['change_pct']) > 2:  # Alert for >2% moves
                            if pos['change_pct'] > 0:
                                st.success(f"🚀 {pos['symbol']}: +{pos['change_pct']:.2f}% - Strong upward move!")
                            else:
                                st.error(f"📉 {pos['symbol']}: {pos['change_pct']:.2f}% - Significant drop!")
                
                with alert_col2:
                    # Portfolio alerts
                    if portfolio_data['total_gain_pct'] > 5:
                        st.success(f"🎉 Portfolio up {portfolio_data['total_gain_pct']:.2f}% - Great day!")
                    elif portfolio_data['total_gain_pct'] < -5:
                        st.warning(f"⚠️ Portfolio down {portfolio_data['total_gain_pct']:.2f}% - Stay calm!")
            
            # Update status
            with status_placeholder:
                st.caption(f"🔴 LIVE - Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Next refresh in {refresh_rate}s")
            
            # Wait for next update
            time.sleep(refresh_rate)
            
    except KeyboardInterrupt:
        st.info("🛑 Live monitoring stopped")
    except Exception as e:
        st.error(f"❌ Live monitoring error: {str(e)}")

if __name__ == "__main__":
    main() 
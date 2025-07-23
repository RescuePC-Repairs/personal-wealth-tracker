#!/usr/bin/env python3
"""
🏦 SoFi CSV Cleaner
Automatically processes SoFi CSV exports and formats them for your Wealth Tracker

Usage:
    python data/sofi_cleaner.py your_sofi_export.csv
    python data/sofi_cleaner.py sofi_portfolio.csv --output clean_portfolio.csv
"""

import pandas as pd
import sys
import argparse
from datetime import datetime
from pathlib import Path

def clean_sofi_investment_csv(file_path, output_path=None):
    """Clean SoFi investment portfolio CSV export"""
    
    print(f"🔄 Processing SoFi CSV: {file_path}")
    
    try:
        # Read the SoFi CSV
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {len(df)} rows")
        
        # Display original columns for debugging
        print(f"📋 Original columns: {list(df.columns)}")
        
        # SoFi column mapping (handles various SoFi export formats)
        column_mappings = {
            # Common SoFi Investment formats
            'Symbol': ['symbol', 'Symbol', 'Ticker', 'SYMBOL'],
            'Shares': ['shares', 'Shares', 'Quantity', 'Units', 'SHARES'],
            'Cost_Basis': ['cost_basis', 'Cost_Basis', 'Total_Cost', 'Avg_Cost', 'Average_Cost'],
            'Market_Value': ['market_value', 'Market_Value', 'Current_Value', 'Value'],
            'Price': ['price', 'Price', 'Current_Price', 'Last_Price']
        }
        
        # Auto-detect SoFi columns
        detected_columns = {}
        for target_col, possible_names in column_mappings.items():
            for col_name in df.columns:
                if any(possible.lower() in col_name.lower() for possible in possible_names):
                    detected_columns[target_col] = col_name
                    break
        
        print(f"🎯 Detected columns: {detected_columns}")
        
        # Create clean DataFrame
        clean_data = []
        
        for _, row in df.iterrows():
            try:
                # Extract symbol
                symbol_col = detected_columns.get('Symbol')
                if not symbol_col:
                    print("❌ Could not find Symbol column")
                    continue
                    
                symbol = str(row[symbol_col]).strip().upper()
                if not symbol or symbol in ['NAN', 'NULL', '']:
                    continue
                
                # Extract shares
                shares_col = detected_columns.get('Shares')
                if not shares_col:
                    print("❌ Could not find Shares column")
                    continue
                    
                shares = float(str(row[shares_col]).replace(',', '').replace('$', ''))
                if shares <= 0:
                    continue
                
                # Calculate average cost
                avg_cost = 0.0
                
                # Try to get from cost basis (this could be per-share or total cost)
                cost_basis_col = detected_columns.get('Cost_Basis')
                if cost_basis_col and pd.notna(row[cost_basis_col]):
                    cost_value = float(str(row[cost_basis_col]).replace(',', '').replace('$', ''))
                    # Check if this looks like per-share cost or total cost
                    if cost_value > shares * 10:  # Likely total cost basis
                        avg_cost = cost_value / shares if shares > 0 else 0
                    else:  # Likely per-share average cost
                        avg_cost = cost_value
                
                # If no cost basis, try market value / shares (rough estimate)
                elif detected_columns.get('Market_Value'):
                    market_value_col = detected_columns['Market_Value']
                    if pd.notna(row[market_value_col]):
                        market_value = float(str(row[market_value_col]).replace(',', '').replace('$', ''))
                        avg_cost = market_value / shares  # Approximation - not ideal but fallback
                
                # If still no cost, try individual price
                elif detected_columns.get('Price'):
                    price_col = detected_columns['Price']
                    if pd.notna(row[price_col]):
                        avg_cost = float(str(row[price_col]).replace(',', '').replace('$', ''))
                
                # Clean up symbol (handle common SoFi quirks)
                symbol = symbol.replace(' ', '')  # Remove spaces
                if '/' in symbol:  # Handle fractional shares display
                    symbol = symbol.split('/')[0]
                
                clean_data.append({
                    'symbol': symbol,
                    'name': '',  # Will be filled by market data
                    'shares': shares,
                    'avg_cost': avg_cost,
                    'date_added': datetime.now().strftime('%Y-%m-%d')
                })
                
            except Exception as e:
                print(f"⚠️ Skipping row due to error: {str(e)}")
                continue
        
        # Create clean DataFrame
        clean_df = pd.DataFrame(clean_data)
        
        if clean_df.empty:
            print("❌ No valid data found in CSV")
            return None
        
        # Remove duplicates
        clean_df = clean_df.drop_duplicates(subset=['symbol'])
        
        print(f"✨ Cleaned data: {len(clean_df)} positions")
        print("\n📊 Summary:")
        for _, row in clean_df.iterrows():
            print(f"  • {row['symbol']}: {row['shares']} shares @ ${row['avg_cost']:.2f}")
        
        # Save cleaned CSV
        if not output_path:
            output_path = f"cleaned_sofi_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        
        clean_df.to_csv(output_path, index=False)
        print(f"\n✅ Saved clean CSV: {output_path}")
        print(f"🚀 Ready to import into your Wealth Tracker!")
        
        return clean_df
        
    except Exception as e:
        print(f"❌ Error processing CSV: {str(e)}")
        return None

def clean_sofi_banking_csv(file_path, output_path=None):
    """Clean SoFi banking/transaction CSV export"""
    
    print(f"💳 Processing SoFi Banking CSV: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        
        # Common banking transaction patterns
        transaction_data = []
        
        for _, row in df.iterrows():
            # Look for investment-related transactions
            description = str(row.get('Description', '')).lower()
            
            if any(keyword in description for keyword in [
                'invest', 'buy', 'sell', 'dividend', 'transfer to invest'
            ]):
                amount = float(str(row.get('Amount', 0)).replace(',', '').replace('$', ''))
                
                transaction_data.append({
                    'date': row.get('Date', ''),
                    'description': row.get('Description', ''),
                    'amount': amount,
                    'type': 'investment_related'
                })
        
        if transaction_data:
            trans_df = pd.DataFrame(transaction_data)
            if not output_path:
                output_path = f"sofi_investment_transactions_{datetime.now().strftime('%Y%m%d')}.csv"
            
            trans_df.to_csv(output_path, index=False)
            print(f"✅ Saved investment transactions: {output_path}")
            
        return transaction_data
        
    except Exception as e:
        print(f"❌ Error processing banking CSV: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Clean SoFi CSV exports for Wealth Tracker')
    parser.add_argument('input_file', help='Path to SoFi CSV export')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    parser.add_argument('--type', '-t', choices=['investment', 'banking', 'auto'], 
                       default='auto', help='CSV type to process')
    
    args = parser.parse_args()
    
    if not Path(args.input_file).exists():
        print(f"❌ File not found: {args.input_file}")
        sys.exit(1)
    
    print("🏦 SoFi CSV Cleaner")
    print("=" * 40)
    
    # Auto-detect CSV type if not specified
    if args.type == 'auto':
        with open(args.input_file, 'r') as f:
            first_line = f.readline().lower()
            if any(col in first_line for col in ['symbol', 'shares', 'portfolio']):
                csv_type = 'investment'
            elif any(col in first_line for col in ['transaction', 'amount', 'description']):
                csv_type = 'banking'
            else:
                csv_type = 'investment'  # Default
    else:
        csv_type = args.type
    
    print(f"📋 Detected CSV type: {csv_type}")
    
    # Process based on type
    if csv_type == 'investment':
        result = clean_sofi_investment_csv(args.input_file, args.output)
    elif csv_type == 'banking':
        result = clean_sofi_banking_csv(args.input_file, args.output)
    
    if result is not None:
        print("\n🎉 Processing complete!")
        print("📥 You can now import the cleaned CSV into your Wealth Tracker")
    else:
        print("\n❌ Processing failed - check your CSV format")
        sys.exit(1)

if __name__ == "__main__":
    main() 
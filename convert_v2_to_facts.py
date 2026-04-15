#!/usr/bin/env python3
"""
Convert V2 output to PRD facts format with milestone_benefits_amount column
"""
import pandas as pd
import uuid
from datetime import datetime

def convert_v2_to_facts(input_file='results_1000_v2.xlsx', output_file='facts_1000_v2.xlsx'):
    """Convert V2 wide format to PRD facts format"""
    
    # Read V2 output
    df = pd.read_excel(input_file)
    
    # Generate batch metadata
    batch_id = str(uuid.uuid4())
    as_of_date = datetime.now().strftime('%Y-%m-%d')
    
    # Build facts list
    facts = []
    
    for idx, row in df.iterrows():
        # Get user_id
        user_id = str(row.get('userid', 'UNKNOWN'))
        
        # Process each rank (top1 through top10)
        for rank in range(1, 11):
            # Column names for this rank
            card_cols = {
                'card_name': f'top{rank}_card_name',
                'total_savings_yearly': f'top{rank}_total_savings_yearly',
                'net_savings': f'top{rank}_net_savings',
                'joining_fees': f'top{rank}_joining_fees',
                'amazon_breakdown': f'top{rank}_amazon_breakdown',
                'flipkart_breakdown': f'top{rank}_flipkart_breakdown',
                'grocery_breakdown': f'top{rank}_grocery_breakdown',
                'other_online_breakdown': f'top{rank}_other_online_breakdown'
            }
            
            # Skip if no card for this rank
            if pd.isna(row.get(card_cols['card_name'])):
                continue
            
            # Create facts row
            fact_row = {
                'as_of_date': as_of_date,
                'batch_id': batch_id,
                'user_id': user_id,
                'rank': rank,
                'card_id': f'CARD_{rank}',  # Placeholder - should map to actual card_id
                'report_store_name': row.get(card_cols['card_name'], ''),
                'total_savings_yearly': row.get(card_cols['total_savings_yearly'], 0),
                'joining_fees': row.get(card_cols['joining_fees'], 0),
                'milestone_benefits_amount': 0.00,  # Always 0.00 per requirement
                'net_savings': row.get(card_cols['net_savings'], 0),
                'amazon_savings': row.get(card_cols['amazon_breakdown'], 0),
                'flipkart_savings': row.get(card_cols['flipkart_breakdown'], 0),
                'grocery_savings': row.get(card_cols['grocery_breakdown'], 0),
                'other_online_savings': row.get(card_cols['other_online_breakdown'], 0),
                'store_link': '',  # Could be populated from catalog
                'bank': '',  # Could be populated from catalog
                'ltf_tag': '',  # Could be populated from catalog
                'schema_version': 'v2.3',
                'cardgenius_error': row.get('cardgenius_error', ''),
                'catalog_version': 'catalog_v1',
                'alias_version': 'alias_v1',
                'milestone_version': 'milestone_v1',
                'record_timestamp': datetime.now().isoformat() + 'Z'
            }
            
            facts.append(fact_row)
    
    # Create DataFrame
    facts_df = pd.DataFrame(facts)
    
    # Save to Excel
    facts_df.to_excel(output_file, index=False)
    
    print(f"✅ Generated {len(facts)} facts rows from {len(df)} users")
    print(f"✅ Saved to: {output_file}")
    
    # Show sample
    print("\n📊 Sample output:")
    print(facts_df.head(3).to_string())
    
    return output_file

if __name__ == '__main__':
    convert_v2_to_facts()


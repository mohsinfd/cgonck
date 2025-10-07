#!/usr/bin/env python3
"""
Integrate Card Name Mapping into CardGenius Processing Pipeline
"""

import pandas as pd
import json
from card_mapping_integration import ProductionCardMapper

def add_card_mapping_to_output(output_file: str, mapper: ProductionCardMapper):
    """
    Add card name mapping validation to existing CardGenius output
    
    Args:
        output_file: Path to CardGenius output Excel file
        mapper: ProductionCardMapper instance
    """
    print(f"📊 Adding card name mapping to {output_file}...")
    
    # Read the output file
    df = pd.read_excel(output_file)
    
    # Add mapping validation columns for each top card
    for i in range(1, 11):  # Top 10 cards
        card_col = f'top{i}_card_name'
        
        if card_col in df.columns:
            # Add new columns for mapping validation
            df[f'top{i}_mapping_confidence'] = ''
            df[f'top{i}_mapping_method'] = ''
            df[f'top{i}_needs_review'] = False
            
            # Process each row
            for idx, row in df.iterrows():
                cardgenius_name = row.get(card_col, '')
                
                if cardgenius_name and str(cardgenius_name).strip():
                    # For now, we don't have the CashKaro name in the output
                    # So we'll just mark if this CardGenius name is in our manual mappings
                    
                    # Check if this CardGenius name is a known mapped card
                    is_known = any(
                        mapper.normalize_name(cg_name) == mapper.normalize_name(cardgenius_name)
                        for cg_name in mapper.manual_mappings.values()
                    )
                    
                    if is_known:
                        df.at[idx, f'top{i}_mapping_confidence'] = 'VERIFIED'
                        df.at[idx, f'top{i}_mapping_method'] = 'manual_mapping'
                        df.at[idx, f'top{i}_needs_review'] = False
                    else:
                        df.at[idx, f'top{i}_mapping_confidence'] = 'UNVERIFIED'
                        df.at[idx, f'top{i}_mapping_method'] = 'none'
                        df.at[idx, f'top{i}_needs_review'] = True
    
    # Save updated file
    output_with_mapping = output_file.replace('.xlsx', '_with_mapping.xlsx')
    df.to_excel(output_with_mapping, index=False)
    
    # Print summary
    verified_count = df[[col for col in df.columns if 'mapping_confidence' in col and col.endswith('_mapping_confidence')]].apply(lambda x: (x == 'VERIFIED').sum()).sum()
    unverified_count = df[[col for col in df.columns if 'mapping_confidence' in col and col.endswith('_mapping_confidence')]].apply(lambda x: (x == 'UNVERIFIED').sum()).sum()
    
    print(f"\n📊 Mapping Summary:")
    print(f"✅ Verified cards: {verified_count}")
    print(f"⚠️  Unverified cards (need review): {unverified_count}")
    print(f"\n💾 Saved to: {output_with_mapping}")
    
    return output_with_mapping

def create_comprehensive_mapping_file():
    """Create a comprehensive mapping file for manual review"""
    print("📋 Creating Comprehensive Mapping File...")
    
    # Load CardGenius cards
    try:
        with open('cardgenius_all_cards.json', 'r') as f:
            cardgenius_cards = json.load(f)
    except:
        print("❌ Please run validate_card_mapping.py first to fetch CardGenius cards")
        return
    
    # Load CashKaro cards
    cashkaro_cards = [
        "Hsbc Bank Travel One Credit Card", "Hsbc Bank Rupay Cashback Credit Card",
        # ... (your full list)
    ]
    
    # Create mapping template
    mapping_data = []
    
    mapper = ProductionCardMapper()
    
    for ck_name in cashkaro_cards:
        expected_cg_name = mapper.get_expected_cardgenius_name(ck_name)
        
        mapping_data.append({
            'cashkaro_name': ck_name,
            'expected_cardgenius_name': expected_cg_name if expected_cg_name else 'NEEDS_MAPPING',
            'mapping_status': 'VERIFIED' if expected_cg_name else 'NEEDS_MANUAL_MAPPING',
            'notes': ''
        })
    
    df = pd.DataFrame(mapping_data)
    df.to_excel('comprehensive_card_mapping.xlsx', index=False)
    
    print(f"✅ Created comprehensive_card_mapping.xlsx")
    print(f"   {len([m for m in mapping_data if m['mapping_status'] == 'VERIFIED'])} cards already mapped")
    print(f"   {len([m for m in mapping_data if m['mapping_status'] == 'NEEDS_MANUAL_MAPPING'])} cards need manual mapping")

if __name__ == "__main__":
    create_comprehensive_mapping_file()



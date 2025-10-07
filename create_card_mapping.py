#!/usr/bin/env python3
"""
Create card name mapping between CashKaro and CardGenius
"""

import pandas as pd
import json
from card_name_mapper import CardNameMapper

# CashKaro card names from your list
cashkaro_cards = [
    "Hsbc Bank Travel One Credit Card", "Hsbc Bank Rupay Cashback Credit Card",
    "Idfc First Bank Power Plus Credit Card", "Idfc First Bank Power Plus Rupay Credit Card",
    "Idfc First Bank Classic Credit Card", "Idfc First Bank Wow Credit Card",
    "Indusind Bank Platinum Aura Edge Credit Card", "Axis Bank Credit Card",
    "Axis Bank Shoppers Stop Mastercard Credit Card", "Sbi Bank Pulse Credit Card",
    "Sbi Apollo Credit Card", "Axis Bank Magnus Burgundy Credit Card",
    "Idfc First Bank Family Credit Card", "Axis Bank Lic Platinum Credit Card",
    "Axis Bank Supermoney Rupay Credit Card", "American Express Platinum Travel Credit Card",
    "Hsbc Bank Taj Card Credit Card", "Regalia Gold",
    "Sbi Bpcl Credit Card", "Sbi Elite Credit Card",
    "Hdfc Bank Business Regalia Gold Credit Card", "Hdfc Bank Pixel Credit Card",
    "Hdfc Millenia Credit Card", "Upi Credit Card On Kiwi",
    "Rbl Bank Shoprite Credit Card", "Hdfc Vc Biz Power Card",
    "Sbi Irctc Platinum Credit Card", "Sbi Prime Credit Card",
    "Axis Bank Indianoil Rupay Credit Card", "Axis Bank Airtel Rupay Credit Card",
    "Axis Bank Samsung Signature Credit Card", "Idfc First Bank Credit Card",
    "Indusind Bank Platinum Rupay Credit Card", "Indusind Bank Platinum Credit Card",
    "American Express Membership Rewards Credit Card", "Axis Bank Atlas Credit Card",
    "Indusind Bank Eazydiner Platinum Credit Card", "Indusind Bank Qatar Airways Avios Visa Infinite Credit Card",
    "Au Bank Vetta Credit Card", "Card Not Selected Yet",
    "Axis Bank Spicejet Voyage Black Credit Card", "American Express Gold Credit Card",
    "Indusind Bank British Airways Avios Visa Infinite Credit Card", "Au Bank Zenith+ Credit Card",
    "Au Bank Altura Credit Card", "Au Bank Credit Card",
    "Sbi Irctc Rupay Credit Card", "Hdfc Bank Credit Card",
    "Hdfc Moneyback Credit Card", "Freedom Credit Card",
    "Pixel Go", "Hdfc Bank Bonvoy Marriott Credit Card",
    "Hdfc Bank Indianoil Credit Card", "Hdfc Business Moneyback Credit Card",
    "Rbl Bank Indianoil Xtra Credit Card", "Indusind Tiger Credit Card",
    "Tata Neu Hdfc Bank Credit Card", "Au Bank Business Cashback Credit Card",
    "Axis Bank Magnus Credit Card", "Axis Bank Neo Rupay Credit Card",
    "Axis Bank Indianoil Credit Card", "Indusind Bank Credit Card",
    "Axis Bank Privilege Credit Card", "Indusind Bank Eazydiner Credit Card",
    "Axis Bank Select Credit Card", "Sbi Bpcl Octane Credit Card",
    "Axis Bank Spicejet Voyage Credit Card", "Axis Bank Fibe Credit Card",
    "Idfc First Bank Lic Classic Credit Card", "Sbi Irctc Premier Credit Card",
    "Indusind Bank Pinnacle Credit Card", "Indusind Bank Samman Credit Card",
    "Sbi Simply Click Credit Card", "Sbi Cashback Credit Card",
    "Hdfc Irctc Platinum Credit Card", "Tata Neu Infinity Hdfc Bank Credit Card",
    "Hdfc Biz First Credit Card", "Hdfc Infinia Credit Card",
    "Hdfc Diners Privilege Credit Card", "Hdfc Vc Biz Grow Card",
    "Yes Bank Pop-Club Credit Card", "Giga Business Card",
    "Hdfc Shoppers Stop Credit Card", "Axis Bank Airtel Credit Card",
    "Axis Bank Horizon Visa Credit Card", "Axis Bank Cashback Mastercard Credit Card",
    "Axis Bank Neo Credit Card", "Axis Bank Shoppers Stop Credit Card",
    "Hsbc Bank Rupay Platinum Credit Card", "Idfc First Bank Millennia Credit Card",
    "Idfc First Bank Select Credit Card", "Idfc First Bank Wealth Credit Card",
    "Idfc Bank Credit Card", "Indusind Bank Legend Credit Card",
    "American Express Smartearn Credit Card", "Hsbc Bank Hsbc Live+Plus Credit Credit Card",
    "Idfc Bank Rupay Upgrade Credit Card", "Hdfc Biz Black Credit Card",
    "Axis Bank Lic Signature Credit Card", "Regalia Activ Card",
    "Au Bank Instapay Credit Card", "Axis Bank Pride Platinum Card",
    "Hdfc Shoppers Stop Black Credit Card", "Sbi Simply Save Credit Card",
    "Hdfc Swiggy Credit Card", "Hdfc Tata Neu Plus Credit Card",
    "Hdfc Bank Freedom Credit Card", "Rbl Bank Indianoil Credit Card",
    "Visa Bizfirst Card", "Au Bank Lit Credit Card",
    "Axis Bank Flipkart Credit Card", "Axis Bank Amex Privilege Credit Card",
    "Axis Bank My Zone Credit Card", "Axis Bank Cashback Visa Credit Card",
    "Axis Bank Rewards Credit Card", "Hsbc Bank Visa Platinum Credit Card",
    "Hsbc Bank Cash Back Credit Card"
]

# CardGenius names (sample from your earlier data)
# You'll need to provide the complete list from CardGenius API
cardgenius_cards_sample = [
    "MRCC", "AMEX SMART EARN", "AMEX GOLD", "AXIS MAGNUS", "AXIS FLIPKART",
    "HSBC Live+", "ICICI Amazon Pay", "HDFC Regalia Gold Credit Card",
    "HDFC Millenia", "SBI Cashback", "IDFC CLUB VISTARA",
    "HDFC  Diners Black Credit Card"
]

def create_mapping():
    """Create comprehensive card name mapping"""
    mapper = CardNameMapper()
    
    # Add known manual mappings
    mapper.add_manual_mapping("American Express Membership Rewards Credit Card", "MRCC")
    mapper.add_manual_mapping("American Express Smartearn Credit Card", "AMEX SMART EARN")
    mapper.add_manual_mapping("American Express Gold Credit Card", "AMEX GOLD")
    mapper.add_manual_mapping("Axis Bank Magnus Credit Card", "AXIS MAGNUS")
    mapper.add_manual_mapping("Axis Bank Flipkart Credit Card", "AXIS FLIPKART")
    mapper.add_manual_mapping("Hsbc Bank Hsbc Live+Plus Credit Credit Card", "HSBC Live+")
    mapper.add_manual_mapping("Icici Amazon Pay", "ICICI Amazon Pay")
    mapper.add_manual_mapping("Regalia Gold", "HDFC Regalia Gold Credit Card")
    mapper.add_manual_mapping("Hdfc Millenia Credit Card", "HDFC Millenia")
    mapper.add_manual_mapping("Sbi Cashback Credit Card", "SBI Cashback")
    
    print("🔍 Creating Card Name Mapping...\n")
    print("Manual Mappings:")
    for ck, cg in mapper.manual_mappings.items():
        print(f"  {ck} → {cg}")
    
    print("\n📊 Fuzzy Matching for Remaining Cards:")
    print("="*80)
    
    # Create mappings for all cards
    mappings = {}
    unmatched = []
    
    for ck_name in cashkaro_cards:
        match = mapper.find_best_match(ck_name, cardgenius_cards_sample, threshold=0.6)
        
        if match:
            mappings[ck_name] = {
                "cardgenius_name": match[0],
                "similarity_score": match[1],
                "match_type": "manual" if ck_name in mapper.manual_mappings else "fuzzy"
            }
            print(f"✅ {ck_name}")
            print(f"   → {match[0]} (score: {match[1]:.2f}, type: {mappings[ck_name]['match_type']})")
        else:
            unmatched.append(ck_name)
            print(f"❌ {ck_name} - No match found")
    
    # Save mappings to JSON
    with open('card_name_mappings.json', 'w') as f:
        json.dump(mappings, f, indent=2)
    
    # Save unmatched to file for manual review
    with open('unmatched_cards.txt', 'w') as f:
        for card in unmatched:
            f.write(f"{card}\n")
    
    # Print summary
    print("\n" + "="*80)
    print(f"\n📊 Mapping Summary:")
    print(f"Total CashKaro cards: {len(cashkaro_cards)}")
    print(f"Matched cards: {len(mappings)}")
    print(f"Unmatched cards: {len(unmatched)}")
    print(f"\n💾 Saved to:")
    print(f"  - card_name_mappings.json (matched cards)")
    print(f"  - unmatched_cards.txt (cards needing manual mapping)")
    
    return mappings, unmatched


if __name__ == "__main__":
    mappings, unmatched = create_mapping()
    
    if unmatched:
        print(f"\n⚠️  {len(unmatched)} cards need manual mapping or CardGenius names list update")
        print(f"   Check unmatched_cards.txt for the list")


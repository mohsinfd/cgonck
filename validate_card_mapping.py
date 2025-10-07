#!/usr/bin/env python3
"""
Card Name Mapping Validation System
Helps validate and review card mappings with similar names
"""

import pandas as pd
import json
from typing import List, Tuple
from card_name_mapper import CardNameMapper
from difflib import SequenceMatcher

def get_all_cardgenius_cards():
    """Get all unique card names from CardGenius API"""
    import requests
    
    print("📡 Fetching all CardGenius card names...")
    
    try:
        response = requests.post(
            'https://card-recommendation-api-v2.bankkaro.com/cg/api/pro',
            json={
                'amazon_spends': 10000,
                'flipkart_spends': 10000,
                'grocery_spends_online': 10000,
                'other_online_spends': 10000,
                'selected_card_id': None
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            cards = data.get('savings', [])
            card_names = [card['card_name'] for card in cards]
            unique_names = sorted(set(card_names))
            
            print(f"✅ Found {len(unique_names)} unique CardGenius card names\n")
            return unique_names
        else:
            print(f"❌ API returned status {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return []

def find_similar_cards(card_name: str, card_list: List[str], similarity_threshold: float = 0.8) -> List[Tuple[str, float]]:
    """Find cards with similar names that might be confused"""
    similar = []
    
    for other_card in card_list:
        if card_name != other_card:
            # Calculate similarity
            similarity = SequenceMatcher(None, card_name.lower(), other_card.lower()).ratio()
            
            if similarity >= similarity_threshold:
                similar.append((other_card, similarity))
    
    # Sort by similarity (highest first)
    similar.sort(key=lambda x: x[1], reverse=True)
    return similar

def validate_mappings():
    """Validate card mappings and identify potential conflicts"""
    
    # Get all CardGenius cards
    cardgenius_cards = get_all_cardgenius_cards()
    
    if not cardgenius_cards:
        print("❌ Could not fetch CardGenius cards. Using cached data if available.")
        try:
            with open('cardgenius_all_cards.json', 'r') as f:
                cardgenius_cards = json.load(f)
            print(f"✅ Loaded {len(cardgenius_cards)} cards from cache")
        except:
            print("❌ No cached data available")
            return
    else:
        # Save for future use
        with open('cardgenius_all_cards.json', 'w') as f:
            json.dump(cardgenius_cards, f, indent=2)
        print("💾 Saved CardGenius card names to cardgenius_all_cards.json\n")
    
    # Display all CardGenius cards
    print("="*80)
    print("📋 ALL CARDGENIUS CARD NAMES:")
    print("="*80)
    for i, name in enumerate(cardgenius_cards, 1):
        print(f"{i:3}. {name}")
    print("="*80)
    print()
    
    # Find cards with similar names (potential confusion)
    print("⚠️  CARDS WITH SIMILAR NAMES (Potential Confusion):")
    print("="*80)
    
    conflicts_found = False
    for i, card in enumerate(cardgenius_cards):
        similar = find_similar_cards(card, cardgenius_cards, similarity_threshold=0.75)
        if similar:
            conflicts_found = True
            print(f"\n🔍 '{card}'")
            print(f"   Similar to:")
            for similar_card, score in similar:
                print(f"   • '{similar_card}' (similarity: {score:.2f})")
    
    if not conflicts_found:
        print("✅ No similar card names found")
    
    print("\n" + "="*80)
    
    # Save all card names to Excel for manual review
    df = pd.DataFrame({
        'cardgenius_name': cardgenius_cards,
        'cashkaro_name': [''] * len(cardgenius_cards),
        'notes': [''] * len(cardgenius_cards)
    })
    
    df.to_excel('card_name_mapping_template.xlsx', index=False)
    print(f"\n💾 Created card_name_mapping_template.xlsx")
    print(f"   You can manually fill in the CashKaro names for each CardGenius card")
    
    return cardgenius_cards

def create_validation_report(cashkaro_cards, cardgenius_cards):
    """Create a detailed validation report"""
    mapper = CardNameMapper()
    
    print("\n📊 VALIDATION REPORT")
    print("="*80)
    
    # Test each mapping
    results = []
    
    for ck_name in cashkaro_cards:
        match = mapper.find_best_match(ck_name, cardgenius_cards, threshold=0.5)
        
        if match:
            cg_name, score = match
            
            # Find similar CardGenius cards (potential conflicts)
            similar = find_similar_cards(cg_name, cardgenius_cards, similarity_threshold=0.75)
            
            result = {
                'cashkaro_name': ck_name,
                'matched_cardgenius_name': cg_name,
                'similarity_score': score,
                'potential_conflicts': len(similar),
                'conflict_details': [s[0] for s in similar[:3]],  # Top 3 similar cards
                'confidence': 'HIGH' if score >= 0.9 and len(similar) == 0 else 
                             'MEDIUM' if score >= 0.7 else 'LOW'
            }
        else:
            result = {
                'cashkaro_name': ck_name,
                'matched_cardgenius_name': 'NO_MATCH',
                'similarity_score': 0,
                'potential_conflicts': 0,
                'conflict_details': [],
                'confidence': 'UNMAPPED'
            }
        
        results.append(result)
    
    # Save to Excel for review
    df = pd.DataFrame(results)
    df.to_excel('card_mapping_validation_report.xlsx', index=False)
    
    # Print summary
    high_confidence = sum(1 for r in results if r['confidence'] == 'HIGH')
    medium_confidence = sum(1 for r in results if r['confidence'] == 'MEDIUM')
    low_confidence = sum(1 for r in results if r['confidence'] == 'LOW')
    unmapped = sum(1 for r in results if r['confidence'] == 'UNMAPPED')
    
    print(f"\n✅ HIGH Confidence: {high_confidence} cards")
    print(f"⚠️  MEDIUM Confidence: {medium_confidence} cards (review recommended)")
    print(f"❌ LOW Confidence: {low_confidence} cards (manual review required)")
    print(f"❓ UNMAPPED: {unmapped} cards (need CardGenius names)")
    
    print(f"\n💾 Saved validation report to: card_mapping_validation_report.xlsx")
    print(f"   Review the MEDIUM and LOW confidence mappings manually")
    
    return results

if __name__ == "__main__":
    # Get all CardGenius cards
    cardgenius_cards = validate_mappings()

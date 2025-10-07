#!/usr/bin/env python3
"""
Card Name Mapping Integration for Processing Pipeline
Uses a conservative approach to avoid incorrect mappings
"""

import json
import pandas as pd
from typing import Optional, Dict
from difflib import SequenceMatcher

class ProductionCardMapper:
    """Conservative card name mapper for production use"""
    
    def __init__(self, manual_mapping_file: str = 'manual_card_mappings.json'):
        """
        Initialize with manual mapping file
        
        Args:
            manual_mapping_file: Path to JSON file with verified mappings
        """
        self.manual_mappings = self._load_manual_mappings(manual_mapping_file)
        self.strict_similarity_threshold = 0.95  # Very high threshold to avoid false matches
        
    def _load_manual_mappings(self, file_path: str) -> Dict[str, str]:
        """Load manual mappings from JSON file"""
        try:
            with open(file_path, 'r') as f:
                mappings = json.load(f)
                print(f"✅ Loaded {len(mappings)} manual card mappings")
                return mappings
        except FileNotFoundError:
            print(f"⚠️  No manual mappings file found at {file_path}")
            print(f"   Creating default mappings...")
            return self._create_default_mappings()
    
    def _create_default_mappings(self) -> Dict[str, str]:
        """Create default mappings for known card aliases"""
        # Verified mappings based on your confirmation
        default_mappings = {
            # CashKaro Name → CardGenius Name
            "American Express Membership Rewards Credit Card": "MRCC",
            "American Express Smartearn Credit Card": "AMEX SMART EARN",
            "American Express Gold Credit Card": "AMEX GOLD CREDIT CARD",
            "American Express Platinum Travel Credit Card": "AMEX PLATINUM TRAVEL",
            "Axis Bank Magnus Credit Card": "AXIS MAGNUS",
            "Axis Bank Flipkart Credit Card": "AXIS FLIPKART",
            "Axis Bank Airtel Credit Card": "AXIS AIRTEL CC",
            "Axis Bank Atlas Credit Card": "AXIS ATLAS CC",
            "Hsbc Bank Hsbc Live+Plus Credit Credit Card": "HSBC Live+ Credit Card",
            "Regalia Gold": "HDFC Regalia Gold Credit Card",
            "Hdfc Millenia Credit Card": "HDFC MILLENIA",
            "Sbi Cashback Credit Card": "SBI CASHBACK",
            "Sbi Elite Credit Card": "SBI ELITE CREDIT CARD",  # Your confirmation: SBI Elite is same card
            "Icici Amazon Pay": "ICICI Amazon Pay Credit Card",
            "Hdfc Infinia Credit Card": "HDFC INFINIA",
            "Hdfc Swiggy Credit Card": "HDFC SWIGGY",
            "Idfc First Bank Power Plus Credit Card": "IDFC POWER PLUS",
            "Idfc First Bank Power Plus Rupay Credit Card": "IDFC POWER PLUS",  # Assuming RuPay variant maps to same
            "Au Bank Zenith+ Credit Card": "AU ZENITH PLUS",
            "Au Bank Altura Credit Card": "AU ALTURA",
            # Add more as you verify them
        }
        
        # Save default mappings
        with open('manual_card_mappings.json', 'w') as f:
            json.dump(default_mappings, f, indent=2)
        print(f"💾 Created default manual_card_mappings.json with {len(default_mappings)} mappings")
        
        return default_mappings
    
    def normalize_name(self, name: str) -> str:
        """Normalize card name for exact matching"""
        if not name:
            return ""
        # Convert to lowercase and strip whitespace
        normalized = name.lower().strip()
        # Normalize multiple spaces to single space
        normalized = ' '.join(normalized.split())
        return normalized
    
    def map_card_name(self, cashkaro_name: str, cardgenius_name: str, strict: bool = True) -> Dict[str, any]:
        """
        Validate if CashKaro card matches CardGenius card
        
        Args:
            cashkaro_name: Card name from CashKaro
            cardgenius_name: Card name from CardGenius API response
            strict: If True, only use manual mappings. If False, allow fuzzy matching
            
        Returns:
            Dict with mapping result and confidence level
        """
        result = {
            'cashkaro_name': cashkaro_name,
            'cardgenius_name': cardgenius_name,
            'matched': False,
            'confidence': 'NONE',
            'method': None
        }
        
        # 1. Check manual mappings first (highest confidence)
        if cashkaro_name in self.manual_mappings:
            expected_cg_name = self.manual_mappings[cashkaro_name]
            if self.normalize_name(expected_cg_name) == self.normalize_name(cardgenius_name):
                result['matched'] = True
                result['confidence'] = 'MANUAL'
                result['method'] = 'manual_mapping'
                return result
        
        # 2. Exact match (case-insensitive)
        if self.normalize_name(cashkaro_name) == self.normalize_name(cardgenius_name):
            result['matched'] = True
            result['confidence'] = 'EXACT'
            result['method'] = 'exact_match'
            return result
        
        # 3. Fuzzy matching (only if strict=False and very high similarity)
        if not strict:
            similarity = SequenceMatcher(
                None,
                self.normalize_name(cashkaro_name),
                self.normalize_name(cardgenius_name)
            ).ratio()
            
            if similarity >= self.strict_similarity_threshold:
                result['matched'] = True
                result['confidence'] = 'FUZZY_HIGH'
                result['method'] = f'fuzzy_match_{similarity:.2f}'
                result['similarity_score'] = similarity
                return result
        
        # No match found
        return result
    
    def get_expected_cardgenius_name(self, cashkaro_name: str) -> Optional[str]:
        """Get the expected CardGenius name for a CashKaro card"""
        return self.manual_mappings.get(cashkaro_name)
    
    def add_mapping(self, cashkaro_name: str, cardgenius_name: str):
        """Add a new manual mapping"""
        self.manual_mappings[cashkaro_name] = cardgenius_name
    
    def save_mappings(self, file_path: str = 'manual_card_mappings.json'):
        """Save current mappings to file"""
        with open(file_path, 'w') as f:
            json.dump(self.manual_mappings, f, indent=2)
        print(f"💾 Saved {len(self.manual_mappings)} mappings to {file_path}")


def test_mapper():
    """Test the production mapper"""
    mapper = ProductionCardMapper()
    
    print("\n🧪 Testing Production Card Mapper\n")
    print("="*80)
    
    # Test cases
    test_cases = [
        ("American Express Membership Rewards Credit Card", "MRCC", True),
        ("Sbi Elite Credit Card", "SBI ELITE CREDIT CARD", True),
        ("Sbi Elite Credit Card", "SBI ELITE Card", True),  # Should also match
        ("Au Bank Zenith+ Credit Card", "AU ZENITH", False),  # Different cards!
        ("Au Bank Zenith+ Credit Card", "AU ZENITH PLUS", True),  # Correct match
        ("Idfc First Bank Power Plus Credit Card", "IDFC POWER", False),  # Different!
        ("Idfc First Bank Power Plus Credit Card", "IDFC POWER PLUS", True),  # Correct
    ]
    
    for ck_name, cg_name, should_match in test_cases:
        result = mapper.map_card_name(ck_name, cg_name, strict=True)
        
        status = "✅" if result['matched'] == should_match else "❌"
        print(f"{status} CashKaro: '{ck_name}'")
        print(f"   CardGenius: '{cg_name}'")
        print(f"   Result: Matched={result['matched']}, Confidence={result['confidence']}, Method={result['method']}")
        print(f"   Expected: {should_match}")
        print()

if __name__ == "__main__":
    test_mapper()



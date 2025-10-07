#!/usr/bin/env python3
"""
Card Name Mapping System
Maps CashKaro card names to CardGenius card names using fuzzy matching
"""

import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional

class CardNameMapper:
    """Maps CashKaro card names to CardGenius card names"""
    
    # Known abbreviations and aliases
    ABBREVIATIONS = {
        'AMEX': 'American Express',
        'MRCC': 'Membership Rewards',
        'HSBC': 'Hsbc',
        'HDFC': 'Hdfc',
        'ICICI': 'Icici',
        'SBI': 'Sbi',
        'AXIS': 'Axis',
        'IDFC': 'Idfc',
        'RBL': 'Rbl',
        'AU': 'Au',
        'INDUSIND': 'Indusind',
        'YES': 'Yes'
    }
    
    # Words to remove during normalization
    STOP_WORDS = {
        'bank', 'credit', 'card', 'visa', 'mastercard', 'rupay',
        'first', 'the', 'new', 'plus'
    }
    
    def __init__(self):
        self.manual_mappings = {}
    
    def normalize_name(self, name: str) -> str:
        """Normalize card name for comparison"""
        if not name:
            return ""
        
        # Convert to lowercase
        normalized = name.lower().strip()
        
        # Remove special characters but keep spaces
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        
        # Remove stop words
        words = normalized.split()
        words = [w for w in words if w not in self.STOP_WORDS]
        
        # Join back
        normalized = ' '.join(words)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def expand_abbreviations(self, name: str) -> str:
        """Expand known abbreviations"""
        expanded = name
        for abbr, full in self.ABBREVIATIONS.items():
            # Case-insensitive replacement
            expanded = re.sub(rf'\b{abbr}\b', full, expanded, flags=re.IGNORECASE)
        return expanded
    
    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity score between two names (0-1)"""
        # Normalize both names
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        # Expand abbreviations
        norm1 = self.expand_abbreviations(norm1)
        norm2 = self.expand_abbreviations(norm2)
        
        # Calculate sequence similarity
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_best_match(self, cashkaro_name: str, cardgenius_names: List[str], threshold: float = 0.6) -> Optional[Tuple[str, float]]:
        """
        Find the best matching CardGenius name for a CashKaro name
        
        Args:
            cashkaro_name: Name from CashKaro
            cardgenius_names: List of names from CardGenius
            threshold: Minimum similarity score to consider a match
            
        Returns:
            Tuple of (best_match, similarity_score) or None if no match found
        """
        # Check manual mappings first
        if cashkaro_name in self.manual_mappings:
            manual_match = self.manual_mappings[cashkaro_name]
            if manual_match in cardgenius_names:
                return (manual_match, 1.0)
        
        # Find best fuzzy match
        best_match = None
        best_score = 0.0
        
        for cg_name in cardgenius_names:
            score = self.calculate_similarity(cashkaro_name, cg_name)
            if score > best_score:
                best_score = score
                best_match = cg_name
        
        # Only return if above threshold
        if best_score >= threshold:
            return (best_match, best_score)
        else:
            return None
    
    def add_manual_mapping(self, cashkaro_name: str, cardgenius_name: str):
        """Add a manual mapping override"""
        self.manual_mappings[cashkaro_name] = cardgenius_name
    
    def map_all_cards(self, cashkaro_names: List[str], cardgenius_names: List[str], threshold: float = 0.6) -> Dict[str, Tuple[str, float]]:
        """
        Map all CashKaro names to CardGenius names
        
        Returns:
            Dictionary of {cashkaro_name: (cardgenius_name, similarity_score)}
        """
        mappings = {}
        
        for ck_name in cashkaro_names:
            match = self.find_best_match(ck_name, cardgenius_names, threshold)
            if match:
                mappings[ck_name] = match
        
        return mappings


def test_mapper():
    """Test the card name mapper"""
    mapper = CardNameMapper()
    
    # Test cases
    test_cases = [
        ("American Express Membership Rewards Credit Card", "MRCC"),
        ("Hsbc Bank Travel One Credit Card", "HSBC Travel One"),
        ("Hdfc Millenia Credit Card", "HDFC Millenia"),
        ("Axis Bank Flipkart Credit Card", "AXIS FLIPKART"),
        ("Sbi Cashback Credit Card", "SBI Cashback"),
    ]
    
    print("🧪 Testing Card Name Mapper\n")
    
    for ck_name, expected_cg_name in test_cases:
        # Simulate finding best match
        cg_names = [expected_cg_name, "Other Card 1", "Other Card 2"]
        match = mapper.find_best_match(ck_name, cg_names)
        
        if match:
            print(f"✅ '{ck_name}'")
            print(f"   → '{match[0]}' (similarity: {match[1]:.2f})")
        else:
            print(f"❌ '{ck_name}' - No match found")
        print()


if __name__ == "__main__":
    test_mapper()


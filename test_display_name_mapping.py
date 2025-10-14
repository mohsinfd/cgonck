#!/usr/bin/env python3
"""
Test script to verify display name mapping works correctly
"""

import json

def load_display_names():
    """Load display name mappings"""
    try:
        with open('cashkaro_display_names.json', 'r') as f:
            config = json.load(f)
            return config.get('name_mappings', {})
    except Exception as e:
        print(f"Error loading cashkaro_display_names.json: {e}")
        return None

def get_display_name(cardgenius_name, mappings):
    """Get the display name for a CardGenius card name"""
    return mappings.get(cardgenius_name, cardgenius_name)

def test_display_name_mapping():
    """Test the display name mapping functionality"""
    print("Testing CashKaro Display Name Mapping")
    print("=" * 70)
    
    # Load mappings
    mappings = load_display_names()
    if not mappings:
        print("FAILED: Could not load cashkaro_display_names.json")
        return False
    
    print(f"Loaded {len(mappings)} display name mappings\n")
    
    # Expected CashKaro Report Store Names
    expected_display_names = [
        "HDFC Pixel Play Credit Card",
        "Axis Airtel Credit Card",
        "Axis Indian Oil Rupay Credit Card",
        "Axis Flipkart Credit Card",
        "Axis MyZone Credit Card",
        "HDFC Swiggy Credit Card",
        "IDFC First Power Plus Credit Card",
        "HDFC RuPay Credit Card",
        "Tata Neu HDFC Bank Credit Card",
        "IDFC First Credit Card",
        "Indusind Tiger Credit Card",
        "HSBC Live Plus Credit Card",
        "Federal Bank Scapia Credit Card",
        "HSBC Platinum Credit Card",
        "RBL Bank Shoprite Credit Card",
        "Indian Oil RBL Bank XTRA Credit Card",
        "HSBC Travel One Credit Card",
        "SBI BPCL Credit Card",
        "SBI Cashback Credit Card",
        "SBI IRCTC Rupay Credit Card",
        "SBI Simply Click Credit Card",
        "SBI Simply Save Credit Card",
        "Rio Rupay Credit Card",
        "Axis Cashback Credit Card",
        "HDFC Millennia Credit Card",
        "IndiGo IDFC FIRST Dual Credit Cards",
        "RBL Bank BookMyShow Play Credit Card",
        "HDFC Bank Diners Club Credit Card",
        "HDFC Bank Indian Oil Credit Card",
        "HDFC Bank Regalia Gold Credit Card",
        "Axis Privilege Visa Credit Card",
        "UPI Credit Card on KIWI",
        "Yes Bank Pop-Club Credit Card"
    ]
    
    # Test common CardGenius names that should map
    test_cases = [
        ("PIXEL Play Credit Card", "HDFC Pixel Play Credit Card"),
        ("AXIS AIRTEL CC", "Axis Airtel Credit Card"),
        ("AXIS FLIPKART", "Axis Flipkart Credit Card"),
        ("AXIS MY ZONE", "Axis MyZone Credit Card"),
        ("HDFC SWIGGY ", "HDFC Swiggy Credit Card"),
        ("IDFC POWER PLUS", "IDFC First Power Plus Credit Card"),
        ("HDFC MILLENIA", "HDFC Millennia Credit Card"),
        ("IDFC FIRST SELECT", "IDFC First Credit Card"),
        ("IndusInd Tiger Credit Card", "Indusind Tiger Credit Card"),
        ("HSBC Live+ Credit Card", "HSBC Live Plus Credit Card"),
        ("Federal Scapia Credit Card", "Federal Bank Scapia Credit Card"),
        ("SBI CASHBACK ", "SBI Cashback Credit Card"),
        ("SBI SIMPLY CLICK", "SBI Simply Click Credit Card"),
        ("Kiwi", "UPI Credit Card on KIWI"),
        ("YES BANK POP-CLUB Credit Card", "Yes Bank Pop-Club Credit Card"),
        # Cards that shouldn't map (should return original name)
        ("AXIS MAGNUS", "AXIS MAGNUS"),
        ("AU ALTURA", "AU ALTURA"),
        ("AMEX PLATINUM TRAVEL", "AMEX PLATINUM TRAVEL")
    ]
    
    print("Testing name transformations:")
    print("-" * 70)
    
    passed = 0
    failed = 0
    
    for cardgenius_name, expected_display_name in test_cases:
        actual_display_name = get_display_name(cardgenius_name, mappings)
        status = "PASS" if actual_display_name == expected_display_name else "FAIL"
        
        if actual_display_name == expected_display_name:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | {cardgenius_name}")
        if actual_display_name != expected_display_name:
            print(f"      Expected: {expected_display_name}")
            print(f"      Got:      {actual_display_name}")
        else:
            print(f"      -> {actual_display_name}")
        print()
    
    print("=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed\n")
    
    # Verify all expected display names can be produced
    print("Checking coverage of required CashKaro display names:")
    print("-" * 70)
    
    # Get all unique display names from mappings
    mapped_display_names = set(mappings.values())
    
    covered = 0
    not_covered = 0
    
    for expected_name in expected_display_names:
        if expected_name in mapped_display_names:
            covered += 1
            print(f"COVERED: {expected_name}")
        else:
            not_covered += 1
            print(f"MISSING: {expected_name}")
    
    print()
    print("=" * 70)
    print(f"Coverage: {covered}/{len(expected_display_names)} required names can be produced")
    
    if not_covered > 0:
        print(f"WARNING: {not_covered} required display names are not mapped yet")
        print("This may be because:")
        print("  1. The CardGenius API uses a different name we haven't mapped")
        print("  2. The card doesn't exist in CardGenius")
        print("  3. We need to add more mapping variations")
    
    if failed == 0:
        print("\nALL TESTS PASSED! Name mapping logic works correctly.")
        return True
    else:
        print(f"\n{failed} TESTS FAILED! Please check the mapping configuration.")
        return False

if __name__ == "__main__":
    success = test_display_name_mapping()
    exit(0 if success else 1)

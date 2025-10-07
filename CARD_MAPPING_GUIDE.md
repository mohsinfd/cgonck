# Card Name Mapping Guide

## Overview

The CardGenius dashboard now includes a built-in Card Name Mapping admin interface that allows you to:
- Auto-generate initial mappings using fuzzy matching
- Review and validate suggested mappings
- Manually add/edit/delete mappings
- Export mappings for backup

## How to Use

### Step 1: Access the Mapping Interface

1. Run the dashboard: `streamlit run cardgenius_dashboard.py`
2. In the sidebar, select **"Card Name Mapping"** tab

### Step 2: Auto-Generate Initial Mappings

1. Click **"Auto-Generate Mappings"** button
2. The system will create initial mappings using fuzzy matching (threshold: 0.7)
3. Review the generated mappings in the table below

### Step 3: Validate and Correct

**Important**: Auto-generated mappings may be incorrect for similar cards!

**Cards to Review Carefully**:
- AU ZENITH vs AU ZENITH PLUS (Different cards!)
- AXIS AIRTEL CC vs AXIS ATLAS CC (Different cards!)
- IDFC POWER vs IDFC POWER PLUS (Different cards!)
- Indian Oil RBL XTRA vs IndianOil RBL (Different cards!)
- Samsung Infinite vs Samsung Signature (Different cards!)

**Already Verified**:
- SBI ELITE CREDIT CARD = SBI ELITE Card (Same card)

### Step 4: Edit Mappings

**To Add a New Mapping**:
1. Enter the CashKaro card name in the text box
2. Select the corresponding CardGenius card from the dropdown
3. Click "Save Mapping"

**To Delete a Mapping**:
1. Find the mapping in the table
2. Click the 🗑️ button next to it

### Step 5: Export Mappings

Click "📥 Download manual_card_mappings.json" to export your verified mappings

## Mapping Rules

1. **Exact Matches**: If names are identical (case-insensitive), they're automatically matched
2. **Manual Mappings**: Use `manual_card_mappings.json` for verified aliases
3. **Fuzzy Matching**: Only used for >0.95 similarity (very conservative)
4. **Flag for Review**: Unknown cards are flagged for manual review

## Files

- **`manual_card_mappings.json`**: Your verified card name mappings
- **`cardgenius_all_cards.json`**: Complete list of CardGenius cards (auto-fetched)
- **`card_name_mapping_template.xlsx`**: Template for bulk mapping (optional)

## Production Use

Once your mappings are validated:
1. The processing pipeline will use these mappings automatically
2. Unverified cards will be flagged in the output
3. You can continue to add/update mappings as new cards are added

## Tips

- Start with the most common cards
- Verify similar card names manually
- Export your mappings regularly for backup
- Review auto-generated mappings before processing production data



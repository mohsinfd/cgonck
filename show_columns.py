#!/usr/bin/env python3
"""Show all output columns"""

import pandas as pd
import json

# Create a sample result to show all columns
sample_data = {
    'userid': 'test_user',
    'top1_card_name': 'AMEX PLATINUM TRAVEL',
    'top1_joining_fees': 5000,
    'top1_total_savings_yearly': 8040,
    'top1_total_extra_benefits': 36800,
    'top1_total_extra_benefits_explanation': 'Includes: ₹6700 welcome bonus, ₹16750 milestone rewards',
    'top1_net_savings': 39840,
    'top1_recommended_redemption_method': 'Hotels',
    'top1_recommended_redemption_brand': 'Marriott',
    'top1_recommended_redemption_conversion_rate': 0.25,
    'top1_recommended_redemption_note': '',
    'top1_redemption_options': json.dumps([{'method': 'Hotels', 'brand': 'Marriott', 'conversion_rate': 0.25}]),
    'top1_all_conversion_rates': 'Hotels: 0.25 (Marriott)',
    'top1_highest_conversion_rate': 0.67,
    'top1_network_url': 'https://secure.traqkarr.com/click?pid=10&offer_id=1395&sub2=',
    'top1_amazon_spends_points': 500,
    'top1_amazon_spends_rupees': 335,
    'top1_amazon_spends_explanation': 'On monthly spend of ₹25K on Amazon you get 1 RP for every ₹50, so you will receive 500 RP.',
    'top1_flipkart_spends_points': 500,
    'top1_flipkart_spends_rupees': 335,
    'top1_flipkart_spends_explanation': 'On monthly spend of ₹25K on Flipkart you get 1 RP for every ₹50, so you will receive 500 RP.',
    'top1_grocery_spends_online_points': 0,
    'top1_grocery_spends_online_rupees': 0,
    'top1_grocery_spends_online_explanation': 'On monthly spend of ₹0 on eligible brands you get 1 RP for every ₹50, so you will receive 0 RP.',
    'top1_other_online_spends_points': 0,
    'top1_other_online_spends_rupees': 0,
    'top1_other_online_spends_explanation': 'On monthly spend of ₹0 on eligible brands you get 1 RP for every ₹50, so you will receive 0 RP.',
    'cardgenius_error': ''
}

df = pd.DataFrame([sample_data])

print('=' * 80)
print('COMPLETE OUTPUT COLUMNS LIST')
print('=' * 80)
print()

print('CORE CARD INFORMATION:')
core_cols = ['userid', 'top1_card_name', 'top1_joining_fees', 'top1_total_savings_yearly', 
             'top1_total_extra_benefits', 'top1_total_extra_benefits_explanation', 'top1_net_savings']
for col in core_cols:
    print(f'  {col}')

print()
print('REDEMPTION INFORMATION:')
redemption_cols = ['top1_recommended_redemption_method', 'top1_recommended_redemption_brand', 
                   'top1_recommended_redemption_conversion_rate', 'top1_recommended_redemption_note',
                   'top1_redemption_options', 'top1_all_conversion_rates', 'top1_highest_conversion_rate']
for col in redemption_cols:
    print(f'  {col}')

print()
print('SPENDING BREAKDOWN (Points + Rupees + Explanation):')
spend_cols = ['top1_amazon_spends_points', 'top1_amazon_spends_rupees', 'top1_amazon_spends_explanation',
              'top1_flipkart_spends_points', 'top1_flipkart_spends_rupees', 'top1_flipkart_spends_explanation',
              'top1_grocery_spends_online_points', 'top1_grocery_spends_online_rupees', 'top1_grocery_spends_online_explanation',
              'top1_other_online_spends_points', 'top1_other_online_spends_rupees', 'top1_other_online_spends_explanation']
for col in spend_cols:
    print(f'  {col}')

print()
print('OTHER:')
other_cols = ['top1_network_url', 'cardgenius_error']
for col in other_cols:
    print(f'  {col}')

print()
print('=' * 80)
print(f'TOTAL COLUMNS: {len(df.columns)}')
print('=' * 80)

print()
print('SAMPLE VALUES:')
print('-' * 40)
for col in df.columns:
    value = df[col].iloc[0]
    if isinstance(value, str) and len(value) > 50:
        value = value[:50] + '...'
    print(f'{col}: {value}')

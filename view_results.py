#!/usr/bin/env python3
"""View detailed results from processing"""

import pandas as pd

# Load results
df = pd.read_excel('results_5k_users.xlsx')

print('=' * 70)
print('DETAILED RESULTS - 134 USERS PROCESSED')
print('=' * 70)
print()

# Overall stats
total = len(df)
success = df['top1_card_name'].notna().sum()
errors = df['cardgenius_error'].notna().sum()

print(f'SUMMARY:')
print(f'   Total users: {total}')
print(f'   Successfully processed: {success} ({success/total*100:.1f}%)')
print(f'   Errors: {errors}')
print()

# Top cards distribution
print(f'TOP CARDS RECOMMENDED:')
top_cards = df['top1_card_name'].value_counts().head(10)
for card, count in top_cards.items():
    pct = count/total*100
    print(f'   {card}: {count} users ({pct:.1f}%)')
print()

# Net savings stats
print(f'NET SAVINGS STATISTICS:')
print(f'   Average: Rs.{df["top1_net_savings"].mean():,.2f}')
print(f'   Median: Rs.{df["top1_net_savings"].median():,.2f}')
print(f'   Min: Rs.{df["top1_net_savings"].min():,.2f}')
print(f'   Max: Rs.{df["top1_net_savings"].max():,.2f}')
print()

# Sample detailed results
print(f'SAMPLE RESULTS (First 10 users):')
print()
sample = df[['userid', 'top1_card_name', 'top1_net_savings', 'top2_card_name', 'top2_net_savings']].head(10)
print(sample.to_string(index=False))
print()

print('=' * 70)
print(f'Full results saved in: results_5k_users.xlsx')
print('=' * 70)



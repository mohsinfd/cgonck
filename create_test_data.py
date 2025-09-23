#!/usr/bin/env python3
"""
Create test data with sample spending values
"""

import pandas as pd
import numpy as np

# Create test data with realistic spending values
test_data = {
    'userid': [12345, 12346, 12347, 12348, 12349],
    ' avg_amazon_gmv ': [5000, 12000, 8000, 15000, 3000],
    ' avg_flipkart_gmv ': [3000, 8000, 5000, 10000, 2000],
    ' avg_myntra_gmv ': [2000, 5000, 3000, 7000, 1500],
    ' avg_ajio_gmv ': [1000, 3000, 2000, 4000, 800],
    ' avg_confirmed_gmv ': [5000, 10000, 6000, 12000, 2500],
    ' avg_grocery_gmv ': [8000, 15000, 10000, 20000, 5000],
    ' total_gmv ': [25000, 53000, 34000, 68000, 12800]
}

df = pd.DataFrame(test_data)
df.to_excel('test_data_with_spending.xlsx', index=False)

print("✅ Created test_data_with_spending.xlsx with sample spending data")
print("\nSample data:")
print(df)



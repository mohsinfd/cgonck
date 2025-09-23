import pandas as pd

# Test the payload preparation
df = pd.read_excel('Card Recommendation avg gmv dump.xlsx')
row = df.iloc[0]
print('Sample row data:')
print(f'userid: {row["userid"]}')
print(f'amazon: {row[" avg_amazon_gmv "]}')
print(f'flipkart: {row[" avg_flipkart_gmv "]}')
print(f'confirmed: {row[" avg_confirmed_gmv "]}')
print(f'grocery: {row[" avg_grocery_gmv "]}')



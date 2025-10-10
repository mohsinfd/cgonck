#!/usr/bin/env python3
"""
Real-world test data generator for CardGenius API testing
Simulates CashKaro user spending patterns based on actual data distributions
"""

import pandas as pd
import numpy as np
import json
import random
from datetime import datetime
import uuid

class TestDataGenerator:
    def __init__(self):
        # Realistic spending patterns based on CashKaro data
        self.spending_patterns = {
            'high_spender': {
                'amazon': (50000, 200000),  # ₹50k-2L monthly
                'flipkart': (30000, 150000),
                'myntra': (5000, 30000),
                'ajio': (3000, 20000),
                'grocery': (10000, 50000),
                'confirmed_gmv': (100000, 500000),
                'probability': 0.15  # 15% high spenders
            },
            'medium_spender': {
                'amazon': (10000, 50000),   # ₹10k-50k monthly
                'flipkart': (5000, 30000),
                'myntra': (1000, 10000),
                'ajio': (500, 5000),
                'grocery': (3000, 15000),
                'confirmed_gmv': (20000, 100000),
                'probability': 0.35  # 35% medium spenders
            },
            'low_spender': {
                'amazon': (1000, 10000),    # ₹1k-10k monthly
                'flipkart': (500, 5000),
                'myntra': (0, 2000),
                'ajio': (0, 1000),
                'grocery': (500, 5000),
                'confirmed_gmv': (2000, 20000),
                'probability': 0.50  # 50% low spenders
            }
        }
        
        # Realistic user ID patterns
        self.user_id_prefixes = ['CK', 'USER', 'CUST']
        
    def generate_user_batch(self, batch_size=200):
        """Generate a realistic batch of users"""
        users = []
        
        for i in range(batch_size):
            # Determine user type based on probabilities
            rand = random.random()
            if rand < self.spending_patterns['high_spender']['probability']:
                user_type = 'high_spender'
            elif rand < (self.spending_patterns['high_spender']['probability'] + 
                        self.spending_patterns['medium_spender']['probability']):
                user_type = 'medium_spender'
            else:
                user_type = 'low_spender'
            
            pattern = self.spending_patterns[user_type]
            
            # Generate realistic spending data
            user_data = {
                'user_id': f"{random.choice(self.user_id_prefixes)}{random.randint(1000000, 9999999)}",
                'avg_amazon_gmv': self._generate_spend(pattern['amazon']),
                'avg_flipkart_gmv': self._generate_spend(pattern['flipkart']),
                'avg_myntra_gmv': self._generate_spend(pattern['myntra']),
                'avg_ajio_gmv': self._generate_spend(pattern['ajio']),
                'avg_grocery_gmv': self._generate_spend(pattern['grocery']),
                'avg_confirmed_gmv': self._generate_spend(pattern['confirmed_gmv'])
            }
            
            # Add some realistic variations (some users don't shop certain categories)
            if random.random() < 0.1:  # 10% don't shop Myntra
                user_data['avg_myntra_gmv'] = 0
            if random.random() < 0.15:  # 15% don't shop Ajio
                user_data['avg_ajio_gmv'] = 0
            if random.random() < 0.05:  # 5% don't shop grocery online
                user_data['avg_grocery_gmv'] = 0
                
            users.append(user_data)
        
        return users
    
    def _generate_spend(self, range_tuple):
        """Generate spending amount within realistic range"""
        min_val, max_val = range_tuple
        
        # Handle zero case
        if min_val == 0 and max_val == 0:
            return 0
        if min_val == 0:
            min_val = 1  # Avoid division by zero
        
        # Use log-normal distribution for more realistic spending patterns
        mean = np.log((min_val + max_val) / 2)
        std = np.log(max_val / min_val) / 4
        amount = np.random.lognormal(mean, std)
        return round(max(min_val, min(amount, max_val)), 2)
    
    def generate_excel_file(self, batch_size=200, filename=None):
        """Generate Excel file with test data"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_batch_{batch_size}_{timestamp}.xlsx"
        
        users = self.generate_user_batch(batch_size)
        df = pd.DataFrame(users)
        
        # Add some metadata
        df['generated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df['batch_id'] = str(uuid.uuid4())[:8]
        
        df.to_excel(filename, index=False)
        print(f"Generated test Excel file: {filename}")
        print(f"Batch size: {batch_size} users")
        print(f"Total GMV range: {df['avg_confirmed_gmv'].min():,.0f} - {df['avg_confirmed_gmv'].max():,.0f}")
        
        return filename, df
    
    def generate_api_payload(self, batch_size=200):
        """Generate API payload for testing"""
        users = self.generate_user_batch(batch_size)
        
        payload = {
            "users": users,
            "top_n_cards": 10
        }
        
        return payload
    
    def save_test_scenarios(self):
        """Save various test scenarios for comprehensive testing"""
        scenarios = [
            {"name": "small_batch", "size": 10, "description": "Small batch for quick testing"},
            {"name": "medium_batch", "size": 50, "description": "Medium batch for performance testing"},
            {"name": "large_batch", "size": 200, "description": "Large batch for production simulation"},
            {"name": "stress_test", "size": 500, "description": "Stress test for API limits"}
        ]
        
        for scenario in scenarios:
            filename, df = self.generate_excel_file(scenario['size'], f"test_{scenario['name']}.xlsx")
            
            # Also generate API payload
            payload = self.generate_api_payload(scenario['size'])
            payload_file = f"test_{scenario['name']}_payload.json"
            
            with open(payload_file, 'w') as f:
                json.dump(payload, f, indent=2)
            
            print(f"Generated {scenario['name']}: {filename} + {payload_file}")

if __name__ == "__main__":
    generator = TestDataGenerator()
    
    print("Generating comprehensive test data...")
    generator.save_test_scenarios()
    
    print("\nSample data preview:")
    sample_df = generator.generate_user_batch(5)
    print(pd.DataFrame(sample_df).to_string(index=False))

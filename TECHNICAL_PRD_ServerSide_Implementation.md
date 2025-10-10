# Technical PRD: Server-Side Card Recommendation Engine

**Document Version:** 1.0  
**Date:** October 7, 2025  
**Type:** Technical Specification  
**Audience:** Engineering Team  
**Priority:** High

---

## 1. Executive Summary

### Objective
Build an internal server-side recommendation engine that replicates CardGenius API functionality without external API calls.

### Problem Statement
Current dependency on CardGenius external API creates:
- Performance bottleneck (2.7s per user)
- External dependency risk
- Scalability limitations
- Processing time: 6 days for 1M users

### Solution
Implement server-side calculation engine that:
- Processes users in < 0.05s per user (50x faster)
- Eliminates external API dependency
- Enables processing 1M users in < 8 hours

### Success Criteria
- [ ] Match CardGenius API accuracy: >95% match rate
- [ ] Process 200K users in < 1 hour
- [ ] Zero external API dependencies
- [ ] Maintainable card catalog system

---

## 2. Input Specification

### 2.1 Data Team Input Format

**File Type:** Excel (.xlsx) or CSV  
**Structure:** One row per user

#### Required Columns

| Column Name | Data Type | Description | Example | Constraints |
|-------------|-----------|-------------|---------|-------------|
| `user_id` | string | Unique user identifier | "CK7186246" | Required, unique |
| `avg_amazon_gmv` | float | Monthly Amazon spending | 50000.00 | >= 0 |
| `avg_flipkart_gmv` | float | Monthly Flipkart spending | 30000.00 | >= 0 |
| `avg_myntra_gmv` | float | Monthly Myntra spending | 10000.00 | >= 0 |
| `avg_ajio_gmv` | float | Monthly Ajio spending | 5000.00 | >= 0 |
| `avg_grocery_gmv` | float | Monthly grocery spending | 15000.00 | >= 0 |
| `avg_confirmed_gmv` | float | Total confirmed monthly GMV | 100000.00 | >= 0 |

#### Optional Columns (Future Enhancement)
- `active_months` - Number of active months
- `credit_score` - User credit score
- `income_range` - Income bracket
- `location` - City/State for location-specific offers

#### Sample Input Data
```csv
user_id,avg_amazon_gmv,avg_flipkart_gmv,avg_myntra_gmv,avg_ajio_gmv,avg_grocery_gmv,avg_confirmed_gmv
CK7186246,50000,30000,10000,5000,15000,100000
USER4188152,120000,20000,5000,2000,8000,150000
CUST3267595,10000,5000,2000,1000,3000,20000
```

#### Data Validation Rules
```python
# Validation rules to implement
def validate_input(user_data):
    """
    Validation rules for input data
    """
    rules = {
        'user_id': {
            'required': True,
            'type': str,
            'max_length': 50
        },
        'spending_fields': [
            'avg_amazon_gmv',
            'avg_flipkart_gmv', 
            'avg_myntra_gmv',
            'avg_ajio_gmv',
            'avg_grocery_gmv',
            'avg_confirmed_gmv'
        ],
        'spending_constraints': {
            'type': float,
            'min': 0,
            'max': 10000000,  # 1 crore max
            'default': 0
        }
    }
    
    # All spending fields default to 0 if missing
    # Negative values should be rejected
    # Non-numeric values should be rejected
    
    return validated_data, errors
```

---

## 3. Output Specification

### 3.1 Expected Output Format

**File Type:** Excel (.xlsx) or CSV  
**Structure:** One row per user per recommended card

#### Output Columns

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `user_id` | string | User identifier (from input) | "CK7186246" |
| `rank` | integer | Card rank (1-10) | 1 |
| `card_name` | string | Credit card name | "ICICI Amazon Pay Credit Card" |
| `total_savings_yearly` | float | Annual savings from rewards | 25000.00 |
| `joining_fees` | float | Card joining/annual fees | 500.00 |
| `total_extra_benefits` | float | Additional benefits value | 1000.00 |
| `net_savings` | float | Net annual savings | 25500.00 |
| `amazon_points` | float | Points from Amazon spends | 5000.00 |
| `flipkart_points` | float | Points from Flipkart spends | 3000.00 |
| `myntra_points` | float | Points from Myntra spends | 1000.00 |
| `ajio_points` | float | Points from Ajio spends | 500.00 |
| `grocery_points` | float | Points from Grocery spends | 1500.00 |
| `other_online_points` | float | Points from other online spends | 2000.00 |
| `redemption_method` | string | Best redemption option | "Vouchers" |
| `redemption_rate` | float | Conversion rate used | 1.0 |

#### Sample Output Data
```csv
user_id,rank,card_name,total_savings_yearly,joining_fees,total_extra_benefits,net_savings,redemption_method
CK7186246,1,ICICI Amazon Pay,25000,500,1000,25500,Vouchers
CK7186246,2,Axis Magnus,22000,10000,15000,27000,Vouchers
CK7186246,3,HDFC Regalia,18000,2500,5000,20500,Cashback
...
```

#### Sorting Rules
- **Primary Sort:** `net_savings` (descending)
- **Secondary Sort:** `total_savings_yearly` (descending)
- **Tertiary Sort:** `card_name` (alphabetical)

Top 10 cards per user only.

---

## 4. Reverse-Engineering CardGenius API Logic

### 4.1 Understanding Current API Behavior

We will treat CardGenius API as a **black box** and reverse-engineer its logic by:

1. **API Request Analysis** - What we send
2. **API Response Analysis** - What we receive
3. **Pattern Recognition** - Identify calculation patterns
4. **Validation** - Test against known outputs

#### 4.1.1 API Request Structure (Input)
```json
{
  "user_id": "CK7186246",
  "avg_amazon_gmv": 50000,
  "avg_flipkart_gmv": 30000,
  "avg_myntra_gmv": 10000,
  "avg_ajio_gmv": 5000,
  "avg_grocery_gmv": 15000,
  "avg_confirmed_gmv": 100000,
  "active_months": 12
}
```

#### 4.1.2 API Response Structure (Output)
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "card_name": "ICICI Amazon Pay Credit Card",
        "total_savings_yearly": 25000,
        "joining_fees": 500,
        "total_extra_benefits": 1000,
        "category_wise_points": {
          "amazon": 5000,
          "flipkart": 300,
          "myntra": 100,
          "ajio": 50,
          "grocery": 150,
          "other_online": 2000
        },
        "redemption_options": [
          {
            "method": "Vouchers",
            "conversion_rate": 1.0,
            "opt_type": "Vouchers"
          },
          {
            "method": "Cashback",
            "conversion_rate": 0.9,
            "opt_type": "Cashback"
          }
        ]
      }
    ]
  }
}
```

### 4.2 Reverse Engineering Methodology

#### Step 1: Data Collection (Week 1)
**Objective:** Collect API request-response pairs to understand patterns

**Tasks:**
1. **Sample API Calls** (n=1000 users)
   - Diverse spending patterns (high/medium/low spenders)
   - Various category combinations
   - Edge cases (zero spends, extreme spends)

2. **Data Collection Script**
```python
# collect_api_patterns.py
import pandas as pd
import requests
import json

def collect_api_samples(users_df, n_samples=1000):
    """
    Call CardGenius API for n_samples users and save:
    - Input data
    - Output recommendations
    - Timestamp
    """
    samples = []
    
    for idx, user in users_df.head(n_samples).iterrows():
        # Call API
        response = call_cardgenius_api(user)
        
        # Store request-response pair
        samples.append({
            'request': user.to_dict(),
            'response': response,
            'timestamp': datetime.now()
        })
    
    # Save to JSON for analysis
    with open('api_samples.json', 'w') as f:
        json.dump(samples, f, indent=2)
    
    return samples
```

3. **Store Data for Analysis**
   - Format: JSON lines file
   - Location: `data/api_samples/`
   - Size: ~1000 request-response pairs

#### Step 2: Pattern Analysis (Week 1-2)
**Objective:** Identify calculation rules from API behavior

**Analysis Tasks:**

1. **Points Calculation Rules**
```python
# analyze_points_patterns.py

def analyze_points_calculation(samples):
    """
    For each card, determine:
    - Reward rate per category (% or flat rate)
    - Point caps per category
    - Spending thresholds for bonus points
    """
    
    patterns = {}
    
    for sample in samples:
        for card in sample['response']['recommendations']:
            card_name = card['card_name']
            
            # Calculate implied reward rates
            amazon_rate = card['amazon_points'] / sample['request']['avg_amazon_gmv']
            flipkart_rate = card['flipkart_points'] / sample['request']['avg_flipkart_gmv']
            
            # Store patterns
            if card_name not in patterns:
                patterns[card_name] = {
                    'amazon_rates': [],
                    'flipkart_rates': [],
                    # ... other categories
                }
            
            patterns[card_name]['amazon_rates'].append(amazon_rate)
            patterns[card_name]['flipkart_rates'].append(flipkart_rate)
    
    # Calculate average/median rates
    for card_name, data in patterns.items():
        data['amazon_rate_avg'] = np.mean(data['amazon_rates'])
        data['amazon_rate_std'] = np.std(data['amazon_rates'])
    
    return patterns
```

**Expected Patterns to Identify:**

| Card | Amazon Rate | Flipkart Rate | Other Online | Notes |
|------|------------|---------------|--------------|-------|
| ICICI Amazon Pay | 5% | 1% | 1% | Capped at 5000 pts/month |
| Axis Flipkart | 1% | 4% | 1% | Capped at 4000 pts/month |
| HDFC Regalia | 4 pts/₹150 | 4 pts/₹150 | 4 pts/₹150 | Uniform rate |

2. **Redemption Value Rules**
```python
def analyze_redemption_patterns(samples):
    """
    Identify:
    - Redemption methods available per card
    - Conversion rates (points to rupees)
    - Which method is selected as "best"
    """
    
    redemption_rules = {}
    
    for sample in samples:
        for card in sample['response']['recommendations']:
            card_name = card['card_name']
            
            # Extract redemption logic
            best_method = card.get('best_redemption_method')
            best_rate = card.get('best_redemption_rate')
            
            # Calculate implied conversion
            total_points = sum([
                card['amazon_points'],
                card['flipkart_points'],
                # ... other categories
            ])
            
            implied_rate = card['total_savings_yearly'] / total_points
            
            redemption_rules[card_name] = {
                'methods': card['redemption_options'],
                'best_method': best_method,
                'implied_rate': implied_rate
            }
    
    return redemption_rules
```

3. **Net Savings Formula**
```python
def verify_net_savings_formula(samples):
    """
    Confirm formula:
    net_savings = total_savings_yearly - joining_fees + total_extra_benefits
    
    Validate across all samples
    """
    
    formula_matches = 0
    total_samples = 0
    
    for sample in samples:
        for card in sample['response']['recommendations']:
            calculated_net_savings = (
                card['total_savings_yearly'] 
                - card['joining_fees'] 
                + card['total_extra_benefits']
            )
            
            api_net_savings = card.get('net_savings')
            
            if abs(calculated_net_savings - api_net_savings) < 0.01:
                formula_matches += 1
            
            total_samples += 1
    
    accuracy = formula_matches / total_samples * 100
    print(f"Net savings formula accuracy: {accuracy:.2f}%")
    
    return accuracy >= 99  # Must be 99%+ accurate
```

#### Step 3: Card Catalog Creation (Week 2)
**Objective:** Build comprehensive card database

**Card Catalog Schema:**
```json
{
  "cards": [
    {
      "card_id": "icici_amazon_pay",
      "card_name": "ICICI Amazon Pay Credit Card",
      "issuer": "ICICI Bank",
      "network": "Visa",
      
      "fees": {
        "joining_fees": 500,
        "annual_fees": 500,
        "renewal_waiver_condition": "Spend 1L annually"
      },
      
      "reward_structure": {
        "base_reward_rate": 0.01,
        "category_rewards": {
          "amazon": {
            "reward_rate": 0.05,
            "calculation_method": "percentage",
            "cap": {
              "type": "monthly",
              "value": 5000,
              "unit": "points"
            },
            "minimum_transaction": 0,
            "exclusions": ["Amazon Pay balance load"]
          },
          "flipkart": {
            "reward_rate": 0.01,
            "calculation_method": "percentage",
            "cap": null
          },
          "myntra": {
            "reward_rate": 0.01,
            "calculation_method": "percentage",
            "cap": null
          },
          "ajio": {
            "reward_rate": 0.01,
            "calculation_method": "percentage",
            "cap": null
          },
          "grocery": {
            "reward_rate": 0.01,
            "calculation_method": "percentage",
            "cap": null
          },
          "other_online": {
            "reward_rate": 0.01,
            "calculation_method": "percentage",
            "cap": null
          }
        }
      },
      
      "redemption_options": [
        {
          "method": "Vouchers",
          "conversion_rate": 1.0,
          "minimum_points": 100,
          "opt_type": "Vouchers",
          "notes": "Amazon gift vouchers at 1:1"
        },
        {
          "method": "Cashback",
          "conversion_rate": 0.9,
          "minimum_points": 500,
          "opt_type": "Cashback",
          "notes": "Statement credit at 0.9:1"
        }
      ],
      
      "extra_benefits": {
        "annual_value": 1000,
        "benefits": [
          {
            "name": "Amazon Prime",
            "value": 1000,
            "condition": "Annual fees paid"
          }
        ]
      },
      
      "eligibility": {
        "min_income": 25000,
        "min_credit_score": 750,
        "age_range": [21, 60]
      },
      
      "metadata": {
        "active": true,
        "last_updated": "2025-10-07",
        "data_source": "CardGenius API reverse engineering"
      }
    }
  ]
}
```

**Card Catalog Population:**
1. **Automated Extraction** - Parse API responses for 100+ cards
2. **Manual Verification** - Validate against card issuer websites
3. **Pattern Confirmation** - Cross-check with multiple user samples
4. **Version Control** - Track changes over time

---

## 5. Core Calculation Engine

### 5.1 Architecture Overview

```
Input (User Spending)
        ↓
  Card Catalog Loader
        ↓
  Points Calculator  ← Reward Rules Engine
        ↓
  Redemption Calculator ← Best Value Selector
        ↓
  Net Savings Calculator
        ↓
  Ranking Engine
        ↓
  Output (Top 10 Cards)
```

### 5.2 Component Specifications

#### 5.2.1 Card Catalog Loader
```python
class CardCatalog:
    """
    Loads and manages card database
    """
    
    def __init__(self, catalog_path='config/card_catalog.json'):
        self.cards = self._load_catalog(catalog_path)
        self.index = self._build_index()
    
    def _load_catalog(self, path):
        """Load card catalog from JSON"""
        with open(path, 'r') as f:
            data = json.load(f)
        return [Card(**card_data) for card_data in data['cards']]
    
    def get_active_cards(self):
        """Return list of active cards"""
        return [card for card in self.cards if card.metadata.active]
    
    def get_card_by_name(self, name):
        """Retrieve specific card by name"""
        return self.index.get(name)
```

#### 5.2.2 Points Calculator
```python
class PointsCalculator:
    """
    Calculates reward points for each spending category
    """
    
    def calculate_category_points(
        self, 
        spending_amount: float,
        reward_config: dict
    ) -> float:
        """
        Calculate points for a single category
        
        Args:
            spending_amount: Spending in rupees
            reward_config: Card's reward configuration for this category
        
        Returns:
            Total points earned (after caps and exclusions)
        """
        
        # Extract config
        reward_rate = reward_config['reward_rate']
        calc_method = reward_config['calculation_method']
        cap = reward_config.get('cap')
        
        # Calculate base points
        if calc_method == 'percentage':
            points = spending_amount * reward_rate
        elif calc_method == 'per_transaction':
            # e.g., 4 points per ₹150 spent
            points = (spending_amount // reward_config['spend_per_unit']) * reward_rate
        else:
            points = 0
        
        # Apply caps
        if cap:
            if cap['type'] == 'monthly':
                monthly_spend = spending_amount  # Already monthly
                monthly_points = points
                capped_points = min(monthly_points, cap['value'])
                points = capped_points
            elif cap['type'] == 'yearly':
                yearly_points = points * 12
                capped_points = min(yearly_points, cap['value'])
                points = capped_points / 12
        
        return points
    
    def calculate_total_points(
        self,
        user_spending: dict,
        card: Card
    ) -> dict:
        """
        Calculate points across all categories for a user
        
        Returns:
            Dict with points per category
        """
        
        category_points = {}
        
        categories = [
            'amazon', 'flipkart', 'myntra', 
            'ajio', 'grocery', 'other_online'
        ]
        
        for category in categories:
            spending_field = f'avg_{category}_gmv'
            spending_amount = user_spending.get(spending_field, 0)
            
            # Get card's reward config for this category
            reward_config = card.reward_structure.category_rewards.get(
                category,
                card.reward_structure.get('base_reward_rate', {})
            )
            
            # Calculate points
            points = self.calculate_category_points(
                spending_amount,
                reward_config
            )
            
            category_points[f'{category}_points'] = points
        
        # Calculate "other_online" from confirmed GMV
        other_online_spend = self._calculate_other_online_spend(user_spending)
        if other_online_spend > 0:
            other_config = card.reward_structure.category_rewards.get('other_online')
            category_points['other_online_points'] = self.calculate_category_points(
                other_online_spend,
                other_config
            )
        
        return category_points
    
    def _calculate_other_online_spend(self, user_spending: dict) -> float:
        """
        Calculate other online spending from confirmed GMV
        Formula: confirmed_gmv - (amazon + flipkart + myntra + ajio + grocery)
        """
        confirmed = user_spending.get('avg_confirmed_gmv', 0)
        
        explicit_categories = sum([
            user_spending.get('avg_amazon_gmv', 0),
            user_spending.get('avg_flipkart_gmv', 0),
            user_spending.get('avg_myntra_gmv', 0),
            user_spending.get('avg_ajio_gmv', 0),
            user_spending.get('avg_grocery_gmv', 0)
        ])
        
        other_online = max(0, confirmed - explicit_categories)
        
        return other_online
```

#### 5.2.3 Redemption Calculator
```python
class RedemptionCalculator:
    """
    Converts points to rupee value using best redemption method
    """
    
    def calculate_redemption_value(
        self,
        total_points: float,
        redemption_options: list
    ) -> dict:
        """
        Calculate rupee value using best redemption method
        
        Returns:
            {
                'total_savings_yearly': float,
                'redemption_method': str,
                'redemption_rate': float
            }
        """
        
        # Filter for Vouchers and Cashback only
        valid_options = [
            opt for opt in redemption_options
            if opt['opt_type'] in ['Vouchers', 'Cashback']
        ]
        
        if not valid_options:
            return {
                'total_savings_yearly': 0,
                'redemption_method': 'None',
                'redemption_rate': 0
            }
        
        # Find highest conversion rate
        best_option = max(
            valid_options,
            key=lambda x: x['conversion_rate']
        )
        
        # Calculate rupee value
        # Assuming monthly points, annualize
        annual_points = total_points * 12
        total_savings = annual_points * best_option['conversion_rate']
        
        return {
            'total_savings_yearly': total_savings,
            'redemption_method': best_option['method'],
            'redemption_rate': best_option['conversion_rate']
        }
```

#### 5.2.4 Net Savings Calculator
```python
class NetSavingsCalculator:
    """
    Calculate final net savings for each card
    """
    
    def calculate_net_savings(
        self,
        total_savings_yearly: float,
        joining_fees: float,
        total_extra_benefits: float
    ) -> float:
        """
        Calculate net savings
        
        Formula: total_savings_yearly - joining_fees + total_extra_benefits
        """
        
        net_savings = (
            float(total_savings_yearly) 
            - float(joining_fees) 
            + float(total_extra_benefits)
        )
        
        return net_savings
    
    def should_include_card(
        self,
        total_savings_yearly: float,
        joining_fees: float,
        total_extra_benefits: float
    ) -> bool:
        """
        Determine if card should be included in recommendations
        
        Rules:
        - Exclude if any value is None/null
        - Exclude if net_savings is negative (for top recommendations)
        """
        
        # Check for null values
        if any([
            total_savings_yearly is None,
            joining_fees is None,
            total_extra_benefits is None
        ]):
            return False
        
        # Calculate net savings
        net_savings = self.calculate_net_savings(
            total_savings_yearly,
            joining_fees,
            total_extra_benefits
        )
        
        # Can include negative net_savings cards in full list
        # But they won't rank in top 10
        return True
```

#### 5.2.5 Ranking Engine
```python
class RankingEngine:
    """
    Ranks cards and selects top 10
    """
    
    def rank_cards(
        self,
        recommendations: list
    ) -> list:
        """
        Sort cards by net_savings (descending)
        Return top 10
        """
        
        # Sort by net_savings (primary), total_savings (secondary)
        sorted_cards = sorted(
            recommendations,
            key=lambda x: (
                -x['net_savings'],  # Descending
                -x['total_savings_yearly'],  # Descending
                x['card_name']  # Ascending (alphabetical)
            )
        )
        
        # Return top 10
        top_10 = sorted_cards[:10]
        
        # Add rank numbers
        for idx, card in enumerate(top_10, start=1):
            card['rank'] = idx
        
        return top_10
```

### 5.3 Main Recommendation Engine

```python
class RecommendationEngine:
    """
    Main engine orchestrating all components
    """
    
    def __init__(self, card_catalog_path='config/card_catalog.json'):
        self.catalog = CardCatalog(card_catalog_path)
        self.points_calculator = PointsCalculator()
        self.redemption_calculator = RedemptionCalculator()
        self.net_savings_calculator = NetSavingsCalculator()
        self.ranking_engine = RankingEngine()
    
    def get_recommendations(
        self,
        user_spending: dict
    ) -> list:
        """
        Generate card recommendations for a user
        
        Args:
            user_spending: Dict with user_id and spending data
        
        Returns:
            List of top 10 recommended cards
        """
        
        recommendations = []
        
        # Get all active cards
        cards = self.catalog.get_active_cards()
        
        # Calculate for each card
        for card in cards:
            # 1. Calculate points
            category_points = self.points_calculator.calculate_total_points(
                user_spending,
                card
            )
            
            total_points = sum(category_points.values())
            
            # 2. Calculate redemption value
            redemption_data = self.redemption_calculator.calculate_redemption_value(
                total_points,
                card.redemption_options
            )
            
            # 3. Calculate net savings
            net_savings = self.net_savings_calculator.calculate_net_savings(
                redemption_data['total_savings_yearly'],
                card.fees.joining_fees,
                card.extra_benefits.annual_value
            )
            
            # 4. Should include?
            if not self.net_savings_calculator.should_include_card(
                redemption_data['total_savings_yearly'],
                card.fees.joining_fees,
                card.extra_benefits.annual_value
            ):
                continue
            
            # 5. Build recommendation object
            recommendation = {
                'user_id': user_spending['user_id'],
                'card_name': card.card_name,
                'total_savings_yearly': redemption_data['total_savings_yearly'],
                'joining_fees': card.fees.joining_fees,
                'total_extra_benefits': card.extra_benefits.annual_value,
                'net_savings': net_savings,
                'redemption_method': redemption_data['redemption_method'],
                'redemption_rate': redemption_data['redemption_rate'],
                **category_points  # Spread category points
            }
            
            recommendations.append(recommendation)
        
        # 6. Rank and get top 10
        top_10 = self.ranking_engine.rank_cards(recommendations)
        
        return top_10
```

---

## 6. Implementation Plan

### Phase 1: Data Collection & Analysis (Week 1-2)

**Week 1:**
- [ ] Day 1-2: Build data collection scripts
- [ ] Day 3-5: Collect 1000+ API samples with diverse spending patterns
- [ ] Day 6-7: Initial pattern analysis

**Week 2:**
- [ ] Day 1-3: Deep pattern analysis (points, redemption, formulas)
- [ ] Day 4-5: Validate patterns across all samples
- [ ] Day 6-7: Document findings and create specifications

**Deliverables:**
- `api_samples.json` - 1000+ request-response pairs
- `patterns_analysis.md` - Documented patterns and rules
- `card_reward_rates.csv` - Extracted reward rates per card

### Phase 2: Card Catalog Creation (Week 3)

- [ ] Day 1-2: Build card catalog schema and database
- [ ] Day 3-4: Populate catalog for top 20 cards (80% of recommendations)
- [ ] Day 5: Validate catalog data against API
- [ ] Day 6-7: Complete remaining cards

**Deliverables:**
- `card_catalog.json` - Complete card database
- `catalog_validation_report.md` - Accuracy validation

### Phase 3: Engine Development (Week 4-5)

**Week 4:**
- [ ] Day 1-2: Build PointsCalculator
- [ ] Day 3-4: Build RedemptionCalculator
- [ ] Day 5: Build NetSavingsCalculator
- [ ] Day 6-7: Build RankingEngine

**Week 5:**
- [ ] Day 1-2: Integrate components into RecommendationEngine
- [ ] Day 3-4: Unit tests for each component
- [ ] Day 5: Integration tests
- [ ] Day 6-7: Performance optimization

**Deliverables:**
- Working recommendation engine
- Test suite with >90% coverage

### Phase 4: Validation (Week 6)

- [ ] Day 1-2: Test engine with 100 users, compare with API
- [ ] Day 3-4: Fix discrepancies, tune parameters
- [ ] Day 5: Test with 1000 users, measure accuracy
- [ ] Day 6: Performance testing (200K users)
- [ ] Day 7: Final validation and sign-off

**Success Criteria:**
- [ ] >95% match rate with CardGenius API
- [ ] Process 200K users in < 1 hour
- [ ] Net savings calculations 100% accurate

### Phase 5: Integration (Week 7)

- [ ] Day 1-2: Integrate with batch processing system
- [ ] Day 3-4: Integrate with API server
- [ ] Day 5: End-to-end testing
- [ ] Day 6: Documentation and training
- [ ] Day 7: Production deployment

---

## 7. Validation Strategy

### 7.1 Accuracy Validation

**Test Matrix:**

| Test Type | Sample Size | Acceptance Criteria |
|-----------|-------------|---------------------|
| Exact Match | 100 users | >80% exact match (all 10 cards) |
| Top 5 Match | 1000 users | >90% match in top 5 cards |
| Top 1 Match | 1000 users | >95% match for #1 card |
| Net Savings | All | 100% match (±₹1) |
| Points Calculation | 500 users | >98% match per category |

**Validation Script:**
```python
def validate_engine_accuracy(
    test_users: list,
    api_results: list,
    engine_results: list
) -> dict:
    """
    Compare engine output with API output
    """
    
    metrics = {
        'exact_match': 0,
        'top_5_match': 0,
        'top_1_match': 0,
        'net_savings_match': 0,
        'total_tests': len(test_users)
    }
    
    for user_id in test_users:
        api_recs = get_recommendations(api_results, user_id)
        engine_recs = get_recommendations(engine_results, user_id)
        
        # Check exact match (all 10 cards in same order)
        if api_recs == engine_recs:
            metrics['exact_match'] += 1
        
        # Check top 5 match
        if api_recs[:5] == engine_recs[:5]:
            metrics['top_5_match'] += 1
        
        # Check top 1 match
        if api_recs[0] == engine_recs[0]:
            metrics['top_1_match'] += 1
        
        # Check net savings calculations
        if all([
            abs(a['net_savings'] - e['net_savings']) < 1
            for a, e in zip(api_recs, engine_recs)
        ]):
            metrics['net_savings_match'] += 1
    
    # Calculate percentages
    for key in ['exact_match', 'top_5_match', 'top_1_match', 'net_savings_match']:
        metrics[f'{key}_pct'] = metrics[key] / metrics['total_tests'] * 100
    
    return metrics
```

### 7.2 Performance Validation

**Benchmarks:**

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Time per user | < 0.05s | Process 1000 users, divide by 1000 |
| Throughput | > 1000 users/min | Process 10,000 users, measure time |
| Memory usage | < 500 MB | Monitor during 200K batch |
| Batch processing | 200K in < 1 hour | End-to-end test |

---

## 8. Data Management

### 8.1 Card Catalog Maintenance

**Update Frequency:**
- **Weekly:** Check for new cards or reward rate changes
- **Monthly:** Full validation against card issuer websites
- **Quarterly:** Comprehensive audit

**Update Process:**
1. Automated scraping of card issuer websites
2. Compare with current catalog
3. Flag differences for manual review
4. Update catalog after approval
5. Re-run validation tests
6. Deploy updated catalog

**Version Control:**
```json
{
  "catalog_version": "2025.42",
  "last_updated": "2025-10-07",
  "cards": [...],
  "changelog": [
    {
      "date": "2025-10-07",
      "changes": [
        "Added SBI ELITE Card",
        "Updated HDFC Regalia reward rate for Amazon",
        "Removed inactive Axis Bank Burgundy"
      ]
    }
  ]
}
```

### 8.2 Quality Assurance

**Continuous Validation:**
- Run 100 sample users through both API and engine daily
- Alert if accuracy drops below 95%
- Automatically create ticket for investigation

**Monitoring Dashboard:**
- Accuracy metrics (real-time)
- Processing performance
- Card catalog version
- Recent changes log

---

## 9. Technical Requirements

### 9.1 Dependencies

```python
# requirements.txt
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0  # Excel file handling
pydantic>=2.0.0  # Data validation
jsonschema>=4.17.0  # Schema validation
pytest>=7.4.0  # Testing
```

### 9.2 System Requirements

**Development:**
- Python 3.10+
- 4 GB RAM minimum
- 1 GB disk space (for card catalog and samples)

**Production:**
- Python 3.10+
- 8 GB RAM (for processing 200K+ users)
- 5 GB disk space (for logs and checkpoints)
- Multi-core CPU (4+ cores for parallel processing)

---

## 10. Testing Strategy

### 10.1 Unit Tests

```python
# test_points_calculator.py

def test_amazon_points_calculation():
    """Test Amazon points calculation for ICICI Amazon Pay"""
    
    calculator = PointsCalculator()
    card = get_card('ICICI Amazon Pay')
    
    # Test case: ₹50,000 Amazon spend
    user_spending = {'avg_amazon_gmv': 50000}
    
    points = calculator.calculate_category_points(
        50000,
        card.reward_structure.category_rewards['amazon']
    )
    
    # Expected: 50,000 × 5% = 2,500 points
    assert points == 2500, f"Expected 2500, got {points}"

def test_points_cap():
    """Test points cap is applied correctly"""
    
    calculator = PointsCalculator()
    card = get_card('ICICI Amazon Pay')
    
    # Test case: ₹200,000 Amazon spend (should be capped at 5000 points/month)
    points = calculator.calculate_category_points(
        200000,
        card.reward_structure.category_rewards['amazon']
    )
    
    # Expected: Capped at 5,000 points
    assert points == 5000, f"Expected 5000 (capped), got {points}"
```

### 10.2 Integration Tests

```python
# test_recommendation_engine.py

def test_end_to_end_recommendation():
    """Test complete recommendation flow"""
    
    engine = RecommendationEngine()
    
    # Sample user
    user = {
        'user_id': 'TEST001',
        'avg_amazon_gmv': 50000,
        'avg_flipkart_gmv': 30000,
        'avg_myntra_gmv': 10000,
        'avg_ajio_gmv': 5000,
        'avg_grocery_gmv': 15000,
        'avg_confirmed_gmv': 120000
    }
    
    # Get recommendations
    recommendations = engine.get_recommendations(user)
    
    # Assertions
    assert len(recommendations) == 10, "Should return exactly 10 cards"
    assert recommendations[0]['rank'] == 1, "First card should be rank 1"
    assert recommendations[0]['net_savings'] > 0, "Top card should have positive savings"
    
    # Check sorting
    for i in range(len(recommendations) - 1):
        assert (
            recommendations[i]['net_savings'] >= recommendations[i+1]['net_savings']
        ), "Cards should be sorted by net_savings descending"
```

### 10.3 Validation Tests

```python
# test_api_comparison.py

def test_compare_with_api():
    """Compare engine output with CardGenius API"""
    
    # Load test users
    test_users = load_test_users('data/test_users_100.csv')
    
    # Get API results (pre-collected)
    api_results = load_api_results('data/api_results_100.json')
    
    # Get engine results
    engine = RecommendationEngine()
    engine_results = [
        engine.get_recommendations(user)
        for user in test_users
    ]
    
    # Validate accuracy
    metrics = validate_engine_accuracy(
        test_users,
        api_results,
        engine_results
    )
    
    # Assertions
    assert metrics['top_1_match_pct'] >= 95, \
        f"Top 1 match rate: {metrics['top_1_match_pct']:.1f}% (need ≥95%)"
    
    assert metrics['top_5_match_pct'] >= 90, \
        f"Top 5 match rate: {metrics['top_5_match_pct']:.1f}% (need ≥90%)"
    
    assert metrics['net_savings_match_pct'] >= 99, \
        f"Net savings match: {metrics['net_savings_match_pct']:.1f}% (need ≥99%)"
```

---

## 11. Risk & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Incomplete pattern identification** | High | Medium | Collect 1000+ diverse samples; continuous validation |
| **Card catalog becomes outdated** | High | High | Automated weekly checks; monitoring dashboard |
| **Accuracy below 95%** | High | Medium | Extensive testing; fallback to API if needed |
| **Performance degradation** | Medium | Low | Regular benchmarking; optimization |
| **Missing edge cases** | Medium | Medium | Comprehensive test suite; production monitoring |

---

## 12. Success Metrics

### Launch Criteria
- [ ] >95% accuracy vs CardGenius API (top 1 card)
- [ ] Process 200K users in < 1 hour
- [ ] 100% net_savings calculation accuracy
- [ ] Complete card catalog (100+ cards)
- [ ] Test suite passing (>90% coverage)

### Post-Launch (30 days)
- [ ] Maintaining >95% accuracy
- [ ] Zero critical bugs
- [ ] Processing 1M+ users successfully
- [ ] Card catalog update process working
- [ ] Documentation complete

---

## 13. Deliverables

### Code Deliverables
1. `recommendation_engine/` - Main engine code
2. `card_catalog.json` - Complete card database
3. `tests/` - Comprehensive test suite
4. `scripts/` - Data collection and validation scripts

### Documentation
1. Technical specification (this document)
2. API documentation
3. Card catalog maintenance guide
4. Troubleshooting guide
5. Performance optimization guide

### Data
1. API samples (1000+ request-response pairs)
2. Pattern analysis report
3. Validation test results
4. Performance benchmarks

---

## 14. Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Data Collection** | Week 1-2 | API samples, pattern analysis |
| **Card Catalog** | Week 3 | Complete card database |
| **Engine Development** | Week 4-5 | Working engine, tests |
| **Validation** | Week 6 | Accuracy >95%, performance tests |
| **Integration** | Week 7 | Production deployment |
| **TOTAL** | **7 weeks** | Production-ready system |

---

## 15. Open Questions

1. **CardGenius Partnership**
   - Can we get official card catalog from CardGenius?
   - Would they provide validation data?
   - Any concerns about replicating their logic?

2. **Legal/Compliance**
   - Any IP concerns with reverse engineering?
   - Need approval from legal team?

3. **Maintenance**
   - Who owns card catalog updates?
   - What's the escalation path for accuracy issues?

---

**Document Owner:** Product/Engineering Team  
**Reviewers:** Tech Lead, Data Team, Product Manager  
**Status:** Draft for Review  
**Next Review:** [Insert Date]




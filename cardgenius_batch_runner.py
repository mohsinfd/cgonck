#!/usr/bin/env python3
"""
CardGenius Batch Recommendation Runner

Processes Excel files with user spending data and generates card recommendations
using the CardGenius API with rate limiting and error handling.
"""

import pandas as pd
import requests
import json
import time
import argparse
import sys
import re
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cardgenius_batch.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CardGeniusBatchRunner:
    """Main class for processing CardGenius batch recommendations"""
    
    def __init__(self, config_path: str):
        """Initialize the runner with configuration"""
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CardGenius-Batch-Runner/1.0'
        })
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise
    
    def _safe_float(self, value: Any) -> float:
        """Safely convert value to float, returning 0 for invalid values"""
        try:
            if pd.isna(value) or value is None:
                return 0.0
            # Strip common currency symbols and commas
            if isinstance(value, str):
                value = re.sub(r'[₹,\s]', '', value)
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _fuzzy_column_match(self, target_column: str, available_columns: List[str]) -> Optional[str]:
        """Find the best matching column using case-insensitive fuzzy matching"""
        target_lower = target_column.lower()
        
        # Exact match (case-insensitive)
        for col in available_columns:
            if col.lower() == target_lower:
                logger.debug(f"Exact match found: '{target_column}' -> '{col}'")
                return col
        
        # Partial match
        for col in available_columns:
            if target_lower in col.lower() or col.lower() in target_lower:
                logger.debug(f"Partial match found: '{target_column}' -> '{col}'")
                return col
        
        # Regex-based matching for common patterns
        patterns = {
            'amazon': r'amazon.*gmv',
            'flipkart': r'flipkart.*gmv',
            'myntra': r'myntra.*gmv',
            'ajio': r'ajio.*gmv',
            'grocery': r'grocery.*gmv',
            'confirmed_gmv': r'(confirmed|avg_confirmed).*gmv',
            'user_id': r'user.*id'
        }
        
        for key, pattern in patterns.items():
            if key in target_lower:
                for col in available_columns:
                    if re.search(pattern, col.lower()):
                        logger.debug(f"Regex match found: '{target_column}' -> '{col}'")
                        return col
        
        logger.warning(f"No match found for column: '{target_column}'")
        return None
    
    def _prepare_payload(self, row: pd.Series, available_columns: List[str]) -> Dict[str, float]:
        """Prepare API payload from Excel row using new authoritative mapping"""
        mappings = self.config['column_mappings']
        
        # Extract individual spend values using fuzzy matching
        amazon_spends = self._safe_float(row.get(mappings['amazon_spends'], 0))
        flipkart_spends = self._safe_float(row.get(mappings['flipkart_spends'], 0))
        myntra = self._safe_float(row.get(mappings['myntra'], 0))
        ajio = self._safe_float(row.get(mappings['ajio'], 0))
        avg_confirmed_gmv = self._safe_float(row.get(mappings['avg_gmv'], 0))
        grocery = self._safe_float(row.get(mappings['grocery'], 0))
        
        # Calculate other_online_spends based on configuration
        other_online_mode = self.config['processing'].get('other_online_mode', 'sum_components')
        
        if other_online_mode == 'sum_components':
            # New authoritative mapping: myntra + ajio + avg_confirmed_gmv
            other_online_spends = myntra + ajio + avg_confirmed_gmv
            logger.debug(f"Using sum_components mode: other_online_spends = {myntra} + {ajio} + {avg_confirmed_gmv} = {other_online_spends}")
        else:
            # Fallback to confirmed_only mode
            other_online_spends = avg_confirmed_gmv
            logger.debug(f"Using confirmed_only mode: other_online_spends = {avg_confirmed_gmv}")
        
        # Prepare payload with all required fields
        payload = {
            "amazon_spends": amazon_spends,
            "flipkart_spends": flipkart_spends,
            "grocery_spends_online": grocery,
            "other_online_spends": other_online_spends,
            "selected_card_id": None
        }
        
        # Add all other supported keys as 0 (as per requirements)
        additional_keys = [
            "dining_spends", "fuel_spends", "travel_spends", "utility_spends",
            "entertainment_spends", "healthcare_spends", "education_spends",
            "insurance_spends", "investment_spends", "other_spends"
        ]
        
        for key in additional_keys:
            payload[key] = 0.0
            
        return payload
    
    def _call_cardgenius_api(self, payload: Dict[str, float], user_id: str) -> Optional[Dict[str, Any]]:
        """Call CardGenius API with retry logic"""
        api_config = self.config['api']
        url = api_config['base_url']
        
        for attempt in range(api_config['max_retries']):
            try:
                logger.info(f"Calling API for user {user_id} (attempt {attempt + 1})")
                
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=api_config['timeout']
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"API returned status {response.status_code} for user {user_id}")
                    if attempt < api_config['max_retries'] - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"API call failed for user {user_id} (attempt {attempt + 1}): {e}")
                if attempt < api_config['max_retries'] - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise
        
        return None
    
    def _extract_card_data(self, card: Dict[str, Any], card_rank: int) -> Dict[str, Any]:
        """Extract relevant data from a single card response"""
        prefix = f"top{card_rank}_"
        
        # Basic card information
        total_savings = card.get('total_savings_yearly', 0)
        joining_fees = card.get('joining_fees', 0)
        extra_benefits = card.get('total_extra_benefits', 0)
        net_savings = float(str(total_savings or 0)) - float(str(joining_fees or 0)) + float(str(extra_benefits or 0))
        
        # Create explanatory note for total_extra_benefits
        extra_benefits_explanation = ""
        welcome_benefits = card.get('welcomeBenefits', [])
        milestone_benefits = card.get('milestone_benefits', [])
        
        benefit_parts = []
        if welcome_benefits:
            for benefit in welcome_benefits:
                cash_value = benefit.get('cash_value', 0)
                if cash_value > 0:
                    benefit_parts.append(f"₹{cash_value} welcome bonus")
        
        if milestone_benefits:
            for benefit in milestone_benefits:
                if benefit.get('eligible', False):
                    rp_bonus = benefit.get('rpBonus', '')
                    voucher_bonus = benefit.get('voucherBonus', '')
                    cash_conversion = benefit.get('cash_conversion', 0)
                    
                    if rp_bonus and cash_conversion:
                        try:
                            rp_value = float(rp_bonus) * float(cash_conversion)
                            benefit_parts.append(f"₹{rp_value:.0f} milestone rewards")
                        except:
                            pass
                    
                    if voucher_bonus:
                        benefit_parts.append(f"₹{voucher_bonus} voucher bonus")
        
        if benefit_parts:
            extra_benefits_explanation = "Includes: " + ", ".join(benefit_parts)
        
        # Handle recommended redemption options first
        recommended_redemption_options = card.get('recommended_redemption_options', [])
        redemption_options = card.get('redemption_options', [])
        
        recommended_option = None
        if recommended_redemption_options and redemption_options:
            # Find the recommended option details
            for rec_opt in recommended_redemption_options:
                redemption_option_id = rec_opt.get('redemption_option_id')
                note = rec_opt.get('note', '')
                
                # Find the actual redemption option details
                for opt in redemption_options:
                    if opt.get('id') == redemption_option_id:
                        recommended_option = {
                            'method': opt.get('method', ''),
                            'brand': opt.get('brand', ''),
                            'conversion_rate': opt.get('conversion_rate', 0),
                            'note': note
                        }
                        break
                if recommended_option:
                    break
        
        # Determine card type and add derived fields
        card_type = "unknown"
        is_cashback_card = False
        redemption_required = True
        effective_conversion_rate = 0.0
        
        # Check if it's a cashback card (no points, direct savings)
        amazon_points = 0
        flipkart_points = 0
        grocery_points = 0
        other_online_points = 0
        
        # Get points from spending breakdown
        spending_breakdown = card.get('spending_breakdown', {})
        if isinstance(spending_breakdown, dict):
            amazon_data = spending_breakdown.get('amazon_spends', {})
            flipkart_data = spending_breakdown.get('flipkart_spends', {})
            grocery_data = spending_breakdown.get('grocery_spends_online', {})
            other_data = spending_breakdown.get('other_online_spends', {})
            
            amazon_points = amazon_data.get('points_earned', 0) if isinstance(amazon_data, dict) else 0
            flipkart_points = flipkart_data.get('points_earned', 0) if isinstance(flipkart_data, dict) else 0
            grocery_points = grocery_data.get('points_earned', 0) if isinstance(grocery_data, dict) else 0
            other_online_points = other_data.get('points_earned', 0) if isinstance(other_data, dict) else 0
        
        # Determine card type based on points vs direct savings
        total_points = amazon_points + flipkart_points + grocery_points + other_online_points
        total_savings_value = float(str(total_savings or 0))
        
        if total_points == 0 and total_savings_value > 0:
            # Direct cashback card
            card_type = "cashback"
            is_cashback_card = True
            redemption_required = False
            effective_conversion_rate = 1.0
        elif total_points > 0:
            # Points-based rewards card
            card_type = "rewards"
            is_cashback_card = False
            redemption_required = True
            # Use recommended redemption rate if available
            if recommended_option:
                effective_conversion_rate = recommended_option['conversion_rate']
            else:
                effective_conversion_rate = 0.0
        else:
            # Fallback case
            card_type = "unknown"
            is_cashback_card = False
            redemption_required = True
            effective_conversion_rate = 0.0
        
        result = {
            f"{prefix}card_name": card.get('card_name', ''),
            f"{prefix}card_type": card_type,
            f"{prefix}is_cashback_card": is_cashback_card,
            f"{prefix}redemption_required": redemption_required,
            f"{prefix}effective_conversion_rate": effective_conversion_rate,
            f"{prefix}joining_fees": joining_fees,
            f"{prefix}total_savings_yearly": total_savings,
            f"{prefix}total_extra_benefits": extra_benefits,
            f"{prefix}total_extra_benefits_explanation": extra_benefits_explanation,
            f"{prefix}net_savings": net_savings,
        }
        
        # Add redemption fields to result
        if recommended_option:
            result[f"{prefix}recommended_redemption_method"] = recommended_option['method']
            result[f"{prefix}recommended_redemption_conversion_rate"] = recommended_option['conversion_rate']
            result[f"{prefix}recommended_redemption_note"] = recommended_option['note']
        else:
            # Fallback to empty values
            result[f"{prefix}recommended_redemption_method"] = ""
            result[f"{prefix}recommended_redemption_conversion_rate"] = 0
            result[f"{prefix}recommended_redemption_note"] = ""
        
        # Extract spend breakdown data
        spend_keys = self.config['processing']['extract_spend_keys']
        spending_breakdown = card.get('spending_breakdown', {})
        
        # Handle both dict and array formats for spending_breakdown
        if isinstance(spending_breakdown, list):
            # Convert array to dict format
            breakdown_dict = {}
            for item in spending_breakdown:
                if isinstance(item, dict) and 'on' in item:
                    breakdown_dict[item['on']] = item
            spending_breakdown = breakdown_dict
        
        for spend_key in spend_keys:
            spend_data = spending_breakdown.get(spend_key, {})
            
            if isinstance(spend_data, dict):
                # Extract both points and rupee values
                points_earned = spend_data.get('points_earned', 0)
                savings_rupees = spend_data.get('savings', 0)
                
                # Output both values for clarity
                result[f"{prefix}{spend_key}_points"] = points_earned
                result[f"{prefix}{spend_key}_rupees"] = savings_rupees
                
                # Handle explanation as list or string
                explanation = spend_data.get('explanation', '')
                if isinstance(explanation, list) and explanation:
                    explanation = explanation[0]  # Take first explanation
                result[f"{prefix}{spend_key}_explanation"] = explanation
            else:
                result[f"{prefix}{spend_key}_points"] = 0
                result[f"{prefix}{spend_key}_rupees"] = 0
                result[f"{prefix}{spend_key}_explanation"] = ''
        
        return result
    
    def _process_api_response(self, response: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process API response and extract top N cards"""
        result = {}
        
        # Handle different response formats
        cards = []
        if 'savings' in response:
            cards = response['savings']
        elif 'cards' in response:
            cards = response['cards']
        elif isinstance(response, list):
            cards = response
        else:
            logger.warning(f"Unexpected response format for user {user_id}: {list(response.keys())}")
            return result
        
        if not cards:
            logger.warning(f"No cards returned for user {user_id}")
            return result
        
        # Filter out cards with null values in key fields
        valid_cards = []
        for card in cards:
            # Check for null values in key fields
            if (card.get('total_savings_yearly') is not None and 
                card.get('joining_fees') is not None and 
                card.get('total_extra_benefits') is not None):
                valid_cards.append(card)
            else:
                logger.warning(f"Skipping card {card.get('card_name', 'Unknown')} for user {user_id} due to null values")
        
        # Calculate correct ROI using only Vouchers/Cashback conversion rates
        def calculate_correct_roi(card):
            try:
                # Get the highest Vouchers/Cashback conversion rate
                redemption_options = card.get('redemption_options', [])
                voucher_cashback_rates = []
                
                for opt in redemption_options:
                    method = opt.get('method', '')
                    if method in ['Vouchers', 'Cashback']:
                        rate = opt.get('conversion_rate', 0)
                        if rate and rate > 0:
                            voucher_cashback_rates.append(float(str(rate)))
                
                # Calculate base net savings
                base_net_savings = (float(str(card.get('total_savings_yearly', 0) or 0)) - 
                                   float(str(card.get('joining_fees', 0) or 0)) + 
                                   float(str(card.get('total_extra_benefits', 0) or 0)))
                
                if voucher_cashback_rates:
                    # Use highest Vouchers/Cashback rate for ROI calculation
                    highest_rate = max(voucher_cashback_rates)
                    return base_net_savings * highest_rate
                else:
                    # Fallback to base net savings if no Vouchers/Cashback options
                    return base_net_savings
            except Exception as e:
                logger.warning(f"Error calculating ROI for card {card.get('card_name', 'Unknown')}: {e}")
                # Fallback to simple net savings calculation
                return (float(str(card.get('total_savings_yearly', 0) or 0)) - 
                       float(str(card.get('joining_fees', 0) or 0)) + 
                       float(str(card.get('total_extra_benefits', 0) or 0)))
        
        # Sort by net savings (highest to lowest) - this matches what's displayed in the output
        def calculate_net_savings(card):
            try:
                return (float(str(card.get('total_savings_yearly', 0) or 0)) - 
                       float(str(card.get('joining_fees', 0) or 0)) + 
                       float(str(card.get('total_extra_benefits', 0) or 0)))
            except Exception as e:
                logger.warning(f"Error calculating net savings for card {card.get('card_name', 'Unknown')}: {e}")
                return 0
        
        cards_sorted = sorted(valid_cards, key=calculate_net_savings, reverse=True)
        
        # Log the top card's ROI for verification
        if cards_sorted:
            top_card_roi = calculate_correct_roi(cards_sorted[0])
            logger.info(f"Top card for user {user_id}: {cards_sorted[0].get('card_name', 'Unknown')} with ROI: {top_card_roi}")
        
        # Extract top N cards
        top_n = self.config['processing']['top_n_cards']
        for i, card in enumerate(cards_sorted[:top_n], 1):
            card_data = self._extract_card_data(card, i)
            result.update(card_data)
        
        return result
    
    def process_excel(self) -> str:
        """Process the Excel file and generate recommendations"""
        excel_config = self.config['excel']
        processing_config = self.config['processing']
        
        # Load Excel file
        logger.info(f"Loading Excel file: {excel_config['input_file']}")
        try:
            df = pd.read_excel(
                excel_config['input_file'], 
                sheet_name=excel_config['sheet_name']
            )
        except Exception as e:
            logger.error(f"Failed to load Excel file: {e}")
            raise
        
        logger.info(f"Loaded {len(df)} rows from Excel file")
        
        # Resolve column mappings with fuzzy matching
        available_columns = list(df.columns)
        logger.info(f"Available columns: {available_columns}")
        
        resolved_mappings = {}
        mappings = self.config['column_mappings']
        
        for key, target_column in mappings.items():
            resolved_column = self._fuzzy_column_match(target_column, available_columns)
            if resolved_column:
                resolved_mappings[key] = resolved_column
                logger.info(f"Resolved mapping: {key} -> '{resolved_column}'")
            else:
                logger.warning(f"Could not resolve column mapping for: {key} (target: '{target_column}')")
        
        # Update config with resolved mappings
        self.config['column_mappings'] = resolved_mappings
        
        # Initialize result columns
        result_columns = {}
        for i in range(1, processing_config['top_n_cards'] + 1):
            prefix = f"top{i}_"
            result_columns.update({
                f"{prefix}card_name": "",
                f"{prefix}card_type": "",
                f"{prefix}is_cashback_card": False,
                f"{prefix}redemption_required": True,
                f"{prefix}effective_conversion_rate": 0.0,
                f"{prefix}joining_fees": 0,
                f"{prefix}total_savings_yearly": 0,
                f"{prefix}total_extra_benefits": 0,
                f"{prefix}total_extra_benefits_explanation": "",
                f"{prefix}net_savings": 0,
                f"{prefix}recommended_redemption_method": "",
                f"{prefix}recommended_redemption_conversion_rate": 0,
                f"{prefix}recommended_redemption_note": "",
            })
            
            for spend_key in processing_config['extract_spend_keys']:
                result_columns[f"{prefix}{spend_key}_points"] = 0
                result_columns[f"{prefix}{spend_key}_rupees"] = 0
                result_columns[f"{prefix}{spend_key}_explanation"] = ""
        
        result_columns["cardgenius_error"] = ""
        
        # Add result columns to dataframe efficiently
        result_df = pd.DataFrame(index=df.index)
        for col, default_val in result_columns.items():
            result_df[col] = default_val
        
        # Concatenate original dataframe with result columns
        df = pd.concat([df, result_df], axis=1)
        
        # Process each row
        total_rows = len(df)
        successful_calls = 0
        failed_calls = 0
        
        for idx, row in df.iterrows():
            user_id = str(row.get(self.config['column_mappings']['user_id'], ''))
            
            # Skip empty rows if configured
            if processing_config['skip_empty_rows'] and not user_id.strip():
                logger.info(f"Skipping empty row {idx + 1}")
                continue
            
            logger.info(f"Processing row {idx + 1}/{total_rows} - User ID: {user_id}")
            
            try:
                # Prepare payload
                payload = self._prepare_payload(row, available_columns)
                logger.debug(f"Payload for user {user_id}: {payload}")
                
                # Call API
                response = self._call_cardgenius_api(payload, user_id)
                
                if response:
                    # Process response
                    card_data = self._process_api_response(response, user_id)
                    
                    # Update dataframe
                    for col, value in card_data.items():
                        df.at[idx, col] = value
                    
                    successful_calls += 1
                    logger.info(f"Successfully processed user {user_id}")
                else:
                    error_msg = f"API call failed for user {user_id}"
                    df.at[idx, 'cardgenius_error'] = error_msg
                    failed_calls += 1
                    logger.error(error_msg)
                
            except Exception as e:
                error_msg = f"Error processing user {user_id}: {str(e)}"
                df.at[idx, 'cardgenius_error'] = error_msg
                failed_calls += 1
                logger.error(error_msg)
                
                if not processing_config['continue_on_error']:
                    raise
            
            # Rate limiting
            if idx < total_rows - 1:  # Don't sleep after the last row
                sleep_time = self.config['api']['sleep_between_requests']
                logger.debug(f"Sleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)
        
        # Save results
        output_file = excel_config['output_file']
        logger.info(f"Saving results to {output_file}")
        df.to_excel(output_file, index=False)
        
        # Summary
        logger.info(f"Processing complete!")
        logger.info(f"Total rows processed: {total_rows}")
        logger.info(f"Successful API calls: {successful_calls}")
        logger.info(f"Failed API calls: {failed_calls}")
        logger.info(f"Results saved to: {output_file}")
        
        return output_file

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='CardGenius Batch Recommendation Runner')
    parser.add_argument('--config', required=True, help='Path to configuration JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        runner = CardGeniusBatchRunner(args.config)
        output_file = runner.process_excel()
        print(f"\n✅ Processing complete! Results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

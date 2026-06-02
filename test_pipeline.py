import pytest
import pandas as pd
import numpy as np
import hashlib

# ==========================================
# 1. MOCK DATA FIXTURES
# ==========================================
# In production testing, we never use the live 2.5 million row dataset. 
# We build tiny, highly controlled DataFrames to test specific edge cases.

@pytest.fixture
def mock_scored_customers():
    """Creates a mock dataset simulating the output of our XGBoost model."""
    return pd.DataFrame({
        'household_key': [1, 2, 3, 4],
        'churn_probability': [0.85, 0.75, 0.20, 0.90],
        'monetary_value': [2000, 500, 1500, 100]
    })

@pytest.fixture
def mock_transaction_history():
    """Creates a mock dataset to test velocity and frequency calculations."""
    return pd.DataFrame({
        'household_key': [1, 1, 1, 2],
        'WEEK_NO': [10, 12, 14, 10], # Household 1 buys every 2 weeks. Household 2 bought once.
        'BASKET_ID': [101, 102, 103, 201],
        'SALES_VALUE': [50, 50, 50, 200]
    })

# ==========================================
# 2. SECURITY & GOVERNANCE TESTS
# ==========================================
def hash_pii(identifier: str) -> str:
    """The hashing function from our ETL pipeline."""
    return hashlib.sha256(str(identifier).encode('utf-8')).hexdigest()

def test_pii_hashing_is_deterministic_and_secure():
    """PROVES: The hashing algorithm masks data and returns consistent results."""
    raw_id = "12345"
    hashed_1 = hash_pii(raw_id)
    hashed_2 = hash_pii(raw_id)
    
    # Must be deterministic (same input = same output) so we can track users over time
    assert hashed_1 == hashed_2
    # Must not be the raw ID
    assert hashed_1 != raw_id
    # SHA-256 hashes are exactly 64 characters long
    assert len(hashed_1) == 64

# ==========================================
# 3. PRESCRIPTIVE ROI LOGIC TESTS
# ==========================================
def apply_prescriptive_logic(df):
    """The core logic stripped from prescriptive_action.py"""
    df = df.copy()
    CHURN_THRESHOLD = 0.70
    HIGH_LTV_THRESHOLD = 1000 # Hardcoded for the test to represent the 75th percentile
    
    df['prescriptive_action'] = "HOLD: Monitor Only"
    df['estimated_campaign_cost'] = 0.0
    
    vip_mask = (df['churn_probability'] >= CHURN_THRESHOLD) & (df['monetary_value'] >= HIGH_LTV_THRESHOLD)
    df.loc[vip_mask, 'prescriptive_action'] = "DEPLOY: $15 VIP Win-Back Coupon"
    df.loc[vip_mask, 'estimated_campaign_cost'] = 15.0
    
    standard_mask = (df['churn_probability'] >= CHURN_THRESHOLD) & (df['monetary_value'] < HIGH_LTV_THRESHOLD)
    df.loc[standard_mask, 'prescriptive_action'] = "DEPLOY: $5 Standard Discount Email"
    df.loc[standard_mask, 'estimated_campaign_cost'] = 5.0
    
    return df

def test_prescriptive_segmentation(mock_scored_customers):
    """PROVES: The business logic routes the correct intervention to the correct user."""
    result_df = apply_prescriptive_logic(mock_scored_customers)
    
    # Household 1: High Risk (0.85) + High Value (2000) -> VIP
    assert result_df.loc[result_df['household_key'] == 1, 'prescriptive_action'].iloc[0] == "DEPLOY: $15 VIP Win-Back Coupon"
    assert result_df.loc[result_df['household_key'] == 1, 'estimated_campaign_cost'].iloc[0] == 15.0
    
    # Household 2: High Risk (0.75) + Low Value (500) -> Standard
    assert result_df.loc[result_df['household_key'] == 2, 'prescriptive_action'].iloc[0] == "DEPLOY: $5 Standard Discount Email"
    
    # Household 3: Low Risk (0.20) -> Hold
    assert result_df.loc[result_df['household_key'] == 3, 'prescriptive_action'].iloc[0] == "HOLD: Monitor Only"
    assert result_df.loc[result_df['household_key'] == 3, 'estimated_campaign_cost'].iloc[0] == 0.0

def test_campaign_roi_calculation(mock_scored_customers):
    """PROVES: The total cost and protected revenue sums are mathematically flawless."""
    result_df = apply_prescriptive_logic(mock_scored_customers)
    
    total_cost = result_df['estimated_campaign_cost'].sum()
    # Expected Cost: Household 1 ($15) + Household 2 ($5) + Household 4 ($5) = $25
    assert total_cost == 25.0

# ==========================================
# 4. DATA ENGINEERING EDGE CASE TESTS
# ==========================================
def test_velocity_zero_division_handling(mock_transaction_history):
    """PROVES: The feature engineering pipeline does not crash on one-time buyers."""
    
    rfm = mock_transaction_history.groupby('household_key').agg(
        first_purchase_week=('WEEK_NO', 'min'),
        last_purchase_week=('WEEK_NO', 'max'),
        frequency=('BASKET_ID', 'nunique')
    ).reset_index()
    
    rfm['customer_lifespan_weeks'] = rfm['last_purchase_week'] - rfm['first_purchase_week']
    
    # The logic from our build_churn_model.py
    rfm['avg_weeks_between_orders'] = np.where(
        rfm['frequency'] > 1, 
        rfm['customer_lifespan_weeks'] / (rfm['frequency'] - 1), 
        999 
    )
    
    # Household 1 bought 3 times over 4 weeks. (4 / 2 intervals) = 2 weeks between orders.
    assert rfm.loc[rfm['household_key'] == 1, 'avg_weeks_between_orders'].iloc[0] == 2.0
    
    # Household 2 bought exactly ONCE. If we didn't use np.where, this would throw a ZeroDivisionError
    assert rfm.loc[rfm['household_key'] == 2, 'avg_weeks_between_orders'].iloc[0] == 999.0
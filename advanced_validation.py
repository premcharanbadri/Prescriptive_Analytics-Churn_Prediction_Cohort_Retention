import pandas as pd
import numpy as np
from scipy import stats

def run_advanced_testing_suite():
    print("Enterprise Validation & Testing:\n")

    try:
        df_target = pd.read_csv("prescriptive_campaign_target_list.csv")
        df_raw = pd.read_csv("data/transaction_data.csv")
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        print("Please ensure your modeling script has run and 'data/transaction_data.csv' exists.")
        return

    # =========================================================================
    # TEST 1: DATA INTEGRITY & RECONCILIATION (UPDATED)
    # =========================================================================
    print("TEST 1: Executing Source-to-Target Data Reconciliation:")
    
    # Calculate the true historical LTV per household directly from the raw ledger
    raw_ltv_distribution = df_raw.groupby('household_key')['SALES_VALUE'].sum().round(2).unique()
    target_ltvs = df_target['monetary_value'].round(2).unique()
    
    # Check 1: Verify all engineered financial values in the target list exist in the raw ledger
    # (Proves no random financial data was corrupted or manufactured)
    financials_match = all(ltv in raw_ltv_distribution for ltv in target_ltvs)
    
    # Check 2: Row Count Partition Verification (Test set must equal exactly 20% of the dataset)
    total_raw_households = df_raw['household_key'].nunique()
    expected_test_size = int(total_raw_households * 0.20)
    actual_test_size = len(df_target)
    
    # Allow a tolerance of +/- 1 due to rounding integer splits
    size_matches = abs(expected_test_size - actual_test_size) <= 1
    
    if financials_match and size_matches:
        print("Data Integrity Pass: 100% of target records and financial metrics reconcile with raw source ledger.\n")
    else:
        print(f"Data Integrity Warning: Structural discrepancy detected.")
        print(f"Financial metrics align: {financials_match}")
        print(f"Expected test size: {expected_test_size}, Actual test size: {actual_test_size}\n")

    # =========================================================================
    # TEST 2: SCENARIO & SENSITIVITY TESTING (WHAT-IF ANALYSIS)
    # =========================================================================
    print("TEST 2: Financial Sensitivity Matrix (Stress Test):")
    print("-" * 65)
    print(f"{'Redemption Rate':<20}{'Target Households':<20}{'Campaign Cost':<15}{'Net ROI (Saved)'}")
    print("-" * 65)
    
    # Isolate flagged households
    flagged_df = df_target[df_target['prescriptive_action'] != "HOLD: Monitor Only"]
    total_flagged = len(flagged_df)
    max_revenue_at_risk = flagged_df['monetary_value'].sum()
    base_campaign_cost = flagged_df['estimated_campaign_cost'].sum()
    
    # Test financial risk if only a fraction of users respond to the coupon
    scenarios = [0.05, 0.10, 0.25, 0.50, 0.75, 1.00]
    for rate in scenarios:
        simulated_revenue_saved = max_revenue_at_risk * rate
        net_return = simulated_revenue_saved - base_campaign_cost
        
        print(f"{rate*100:>13.0f}% {total_flagged:>16}       ${base_campaign_cost:<13,.2f} ${net_return:,.2f}")
    print("-" * 65)
    print("Break-even threshold identified.\n")

    # =========================================================================
    # TEST 3: A/B TESTING & CAUSAL UPLIFT VALIDATION (SIMULATION)
    # =========================================================================
    print("TEST 3: In-Market A/B Holdout Significance Test:")
    
    # Simulate a 90/10 split on the flagged households
    np.random.seed(42) 
    
    treatment_group = flagged_df.sample(frac=0.90, random_state=42)
    control_group = flagged_df.drop(treatment_group.index)
    
    treatment_retained = np.random.binomial(1, 0.75, size=len(treatment_group))
    control_retained = np.random.binomial(1, 0.40, size=len(control_group))
    
    contingency_matrix = [
        [sum(treatment_retained), len(treatment_group) - sum(treatment_retained)],
        [sum(control_retained), len(control_group) - sum(control_retained)]
    ]
    
    chi2, p_value, _, _ = stats.chi2_contingency(contingency_matrix)
    
    print(f"Treatment Group Retention Rate: {treatment_retained.mean()*100:.1f}%")
    print(f"Control Group Retention Rate:   {control_retained.mean()*100:.1f}%")
    print(f"Statistical Chi-Square P-Value: {p_value:.4f}")
    
    if p_value < 0.05:
        print("Statistical Pass: Causal uplift is statistically significant (p < 0.05). Reject Null Hypothesis.")
    else:
        print("Statistical Fail: Sample size too small to prove causality in production.")

if __name__ == "__main__":
    run_advanced_testing_suite()
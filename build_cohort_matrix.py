import pandas as pd

def build_standalone_cohort_matrix(data_dir='data/'):
    print("Raw transaction data:")
    # This reads the exact same file the churn model uses
    txns = pd.read_csv(f"{data_dir}transaction_data.csv")
    
    print("Acquisition Weeks:")
    # 1. Find the exact week each household made their first purchase
    acquisition = txns.groupby('household_key')['WEEK_NO'].min().reset_index()
    acquisition.rename(columns={'WEEK_NO': 'acquisition_week'}, inplace=True)
    
    # 2. Map every transaction to the household's original acquisition week
    df = txns.merge(acquisition, on='household_key', how='left')
    
    # 3. Calculate "Period Distance" (Weeks since they started)
    df['weeks_since_acquisition'] = df['WEEK_NO'] - df['acquisition_week']
    
    print("Aggregated Cohort Retention:")
    # 4. Group the data to count unique active households per period
    cohort_data = df.groupby(['acquisition_week', 'weeks_since_acquisition']).agg(
        active_households=('household_key', 'nunique')
    ).reset_index()
    
    # 5. Bound the data to 52 weeks (1 Year tracking)
    cohort_data = cohort_data[cohort_data['weeks_since_acquisition'] <= 52]
    
    # 6. Engineer the Retention Percentage directly in Python 
    cohort_sizes = cohort_data[cohort_data['weeks_since_acquisition'] == 0][['acquisition_week', 'active_households']]
    cohort_sizes.rename(columns={'active_households': 'initial_cohort_size'}, inplace=True)
    
    cohort_data = cohort_data.merge(cohort_sizes, on='acquisition_week', how='left')
    cohort_data['retention_percentage'] = cohort_data['active_households'] / cohort_data['initial_cohort_size']
    
    # 7. Save the final payload for Tableau
    output_file = "cohort_retention_matrix.csv"
    cohort_data.to_csv(output_file, index=False)
    print(f"Generated {len(cohort_data)} cohort periods across {cohort_data['acquisition_week'].nunique()} acquisition weeks.")
    print(f"Saved matrix to {output_file}")

if __name__ == "__main__":
    build_standalone_cohort_matrix()
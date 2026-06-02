import pandas as pd
import numpy as np

def build_rfm_features(data_dir='data/'):
    print("Core transaction and demographic tables:")
    txns = pd.read_csv(f"{data_dir}transaction_data.csv")
    demos = pd.read_csv(f"{data_dir}hh_demographic.csv")
    
    # 1. Establish the "Current Date" of the dataset
    current_week = txns['WEEK_NO'].max()
    
    print("Recency, Frequency, Monetary, and Velocity metrics:")
    
    # Get the FIRST and LAST purchase week for every household
    rfm = txns.groupby('household_key').agg(
        first_purchase_week=('WEEK_NO', 'min'),
        last_purchase_week=('WEEK_NO', 'max'),
        frequency=('BASKET_ID', 'nunique'),
        monetary_value=('SALES_VALUE', 'sum')
    ).reset_index()
    
    # Calculate Velocity Features
    rfm['recency_weeks'] = current_week - rfm['last_purchase_week']
    rfm['customer_lifespan_weeks'] = rfm['last_purchase_week'] - rfm['first_purchase_week']
    
    # Avoid division by zero for one-time buyers
    rfm['avg_weeks_between_orders'] = np.where(
        rfm['frequency'] > 1, 
        rfm['customer_lifespan_weeks'] / (rfm['frequency'] - 1), 
        999 # Flag one-time buyers with a high outlier
    )
    
    # Define Churn (3 weeks)
    rfm['is_churned'] = (rfm['recency_weeks'] > 3).astype(int)
    
    # Left join to preserve all 2,500 households
    df_model = rfm.merge(demos, on='household_key', how='left')
    
    # Drop data-leakage columns
    df_clean = df_model.drop(columns=['first_purchase_week', 'last_purchase_week', 'recency_weeks'])
    
    return df_clean

if __name__ == "__main__":
    feature_matrix = build_rfm_features()
    print(f"Feature Matrix: {feature_matrix.shape[0]} households, {feature_matrix.shape[1]} features.")
    print(feature_matrix['is_churned'].value_counts(normalize=True))


    import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

def train_churn_model(df):
    
    # 1. One-Hot Encoding for categorical demographics
    # Converts columns like 'INCOME_DESC' into binary columns (e.g., 'INCOME_DESC_50-74K')
    features = pd.get_dummies(df.drop(columns=['household_key', 'is_churned']))
    target = df['is_churned']
    
    # 2. Train/Test Split (80% training, 20% validation)
    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )
    
    # 3. The Class Imbalance Solution (scale_pos_weight)
    # Math: (Count of Negative Class) / (Count of Positive Class)
    negative_class_count = (y_train == 0).sum()
    positive_class_count = (y_train == 1).sum()
    scale_weight = negative_class_count / positive_class_count
    
    print(f"Applying scale_pos_weight of {scale_weight:.2f} to handle class imbalance.")
    
    # 4. Initialize and Train XGBoost
    model = xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=4,
        scale_pos_weight=scale_weight,
        eval_metric='auc',
        random_state=42
    )
    
    print("XGBoost Classifier:")
    model.fit(X_train, y_train)
    
    # 5. Evaluate the Model
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1] # Extract the % risk of churn
    
    print("\nModel Evaluation Metrics:")
    print("-" * 30)
    print(classification_report(y_test, predictions))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, probabilities):.3f}")
    
    return model, X_test, probabilities

if __name__ == "__main__":
    # Assuming feature_matrix is already loaded from the previous step
    # feature_matrix = build_rfm_features()
    model, test_data, churn_probs = train_churn_model(feature_matrix)

def generate_prescriptive_campaign(df_scored):
    print(" Prescriptive Action:")
    
    # We define business thresholds based on our model's confidence and customer value
    CHURN_THRESHOLD = 0.70  # Only intervene if the model is 70%+ sure they will churn
    HIGH_LTV_THRESHOLD = df_scored['monetary_value'].quantile(0.75) # Top 25% of spenders
    
    # Initialize the Action Column
    df_scored['prescriptive_action'] = "HOLD: Monitor Only"
    df_scored['estimated_campaign_cost'] = 0.0
    
    # Logic 1: High Risk & High Value -> VIP Save Campaign
    vip_mask = (df_scored['churn_probability'] >= CHURN_THRESHOLD) & (df_scored['monetary_value'] >= HIGH_LTV_THRESHOLD)
    df_scored.loc[vip_mask, 'prescriptive_action'] = "DEPLOY: $15 VIP Win-Back Coupon"
    df_scored.loc[vip_mask, 'estimated_campaign_cost'] = 15.0
    
    # Logic 2: High Risk & Low/Mid Value -> Standard Automated Save
    standard_mask = (df_scored['churn_probability'] >= CHURN_THRESHOLD) & (df_scored['monetary_value'] < HIGH_LTV_THRESHOLD)
    df_scored.loc[standard_mask, 'prescriptive_action'] = "DEPLOY: $5 Standard Discount Email"
    df_scored.loc[standard_mask, 'estimated_campaign_cost'] = 5.0
    
    # ROI Calculation
    total_interventions = (df_scored['prescriptive_action'] != "HOLD: Monitor Only").sum()
    total_cost = df_scored['estimated_campaign_cost'].sum()
    revenue_protected = df_scored.loc[vip_mask | standard_mask, 'monetary_value'].sum()
    
    print("\n[ EXECUTIVE CAMPAIGN SUMMARY ]")
    print(f"Total Households Flagged for Rescue: {total_interventions}")
    print(f"Total Campaign Investment Required: ${total_cost:,.2f}")
    print(f"Historical Revenue at Risk (Protected): ${revenue_protected:,.2f}")
    
    return df_scored

if __name__ == "__main__":
    # Assuming `model, test_data, churn_probs` from your XGBoost script
    # We append the probabilities back to the test data
    test_data = test_data.copy()
    test_data['churn_probability'] = churn_probs
    
    # Run the ROI Engine
    actionable_df = generate_prescriptive_campaign(test_data)
    actionable_df.to_csv("prescriptive_campaign_target_list.csv", index=False)
    print("\nCampaign Targeting List saved as 'prescriptive_campaign_target_list.csv'")
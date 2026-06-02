## Executive Project Overview & Mandate

### The Business Problem

In high-frequency retail environments, businesses suffer from **"Silent Churn"** - customers do not actively cancel an account; they simply stop visiting. Traditional Business Intelligence (BI) frameworks fail because they report this defection retrospectively, long after the customer’s lifetime value (LTV) has vanished. Furthermore, standard marketing interventions rely on "spray-and-pray" blanket discounts, which erode profit margins on customers who would have bought anyway while under-investing in saving high-value VIPs.

### The Objective

To engineer an end-to-end, automated machine learning pipeline and data storytelling ecosystem using a **Buy 'Till You Die (BTYD)** framework. The system dynamically predicts individual household churn risk, cross-references that risk against historical monetary values, prescribes automated, margin-optimized financial interventions, and visualizes the macroeconomic health of the customer base.

---

## Phase 1: Data Engineering & Secure ETL Pipeline

The pipeline ingested and processed a raw retail transaction ledger consisting of **2,500 households** and over **2.5 million individual purchase logs**.

* **Feature Engineering:** Aggregated raw transactions at the household level to compute critical behavioral velocity attributes over a rolling timeframe:
* **Recency:** The number of weeks between the dataset's maximum date and a household's final transaction.
* **Frequency:** Total count of unique `BASKET_ID` checkouts.
* **Monetary Value (LTV):** Sum total of individual item `SALES_VALUE` across the customer's lifespan.
* **Velocity Matrix:** Engineered `avg_weeks_between_orders` to establish individual shopping cadences.


* **Edge-Case Exception Handling:** Handled the "One-Time Buyer" anomaly. One-time buyers have a frequency of 1, which causes a fatal `ZeroDivisionError` when calculating time between orders. The pipeline successfully implemented an `np.where` guardrail, isolating these profiles and mapping them to a deterministic high-outlier value of `999`.
* **Security & Data Governance:** Enforced strict data security standards by building a deterministic, one-way SHA-256 cryptographic hashing pipeline to irreversibly mask customer identifiers (`household_key`), creating secure tokens that preserve analytical tracking capabilities without leaking Personally Identifiable Information (PII).

---

## Phase 2: Predictive Machine Learning Engine

The clean feature matrix was combined with demographic indicators (`hh_demographic.csv`) to train a highly optimized gradient-boosting algorithm.

* **Pre-processing:** Applied One-Hot Encoding to categorical demographic arrays (e.g., income tiers, household sizes) and executed an 80/20 stratified train/test split.
* **Class Imbalance Resolution:** The training data revealed a significant imbalance, with only **20.36%** of the customer base naturally falling into the churn category. To prevent model bias, the pipeline automatically calculated and applied an XGBoost `scale_pos_weight` hyperparameter of **3.91**, representing the exact mathematical ratio of negative-to-positive class occurrences.
* **Model Selection:** Trained an **XGBoost Classifier** optimized for Area Under the Receiver Operating Characteristic curve (`eval_metric='auc'`).

### Model Performance Evaluation Metrics

The model was tested against a completely unseen validation sample of 500 households, yielding high operational accuracy:

```
               precision    recall  f1-score   support

           0       0.93      0.88      0.90       398
           1       0.61      0.73      0.66       102

    accuracy                           0.85       500
   macro avg       0.77      0.80      0.78       500
weighted avg       0.86      0.85      0.85       500

ROC-AUC Score: 0.885

```

* **Key Analytical Insight:** The model achieved a **73% Recall on Class 1 (Churners)**. In a churn defense posture, Recall is our primary north-star metric because it proves the algorithm successfully captured 73% of all actual defecting households, leaving very few unflagged "blind spots."

---

## Phase 3: Prescriptive Action & Financial ROI

The project decoupled predictive insights from business execution by building a rule-based optimization engine that maps individual churn probabilities directly to margin-controlled retention budgets.

* **The Prescriptive Logic:**
* **The Threshold:** Customers were only eligible for capital intervention if the model was $\ge$ **70% confident** in their imminent defection.
* **VIP Intervention Tier:** High-Risk ($\ge$ 70%) AND High-Value ($\ge$ 75th percentile of company LTV, or $\ge$ $1,000) $\to$ Deployed a **$15 VIP Win-Back Coupon**.
* **Standard Intervention Tier:** High-Risk ($\ge$ 70%) AND Low/Mid-Value (< $1,000 LTV) $\to$ Deployed a **$5 Standard Discount Email**.
* **Hold/Monitor Tier:** All customers displaying < 70% churn risk were suppressed from receiving marketing capital.



### Executive Campaign Financial Summary

Running the prescriptive analytics on the test partition yielded the following immediate bottom-line outcomes:

* **Total Households Flagged for Rescue:** 75 households
* **Total Campaign Investment Required:** $395.00
* **Historical Revenue at Risk (Protected):** $71,874.27
* **Theoretical Maximum ROI:** **18,196% return** on targeted marketing capital.

---

## Phase 4: Macroeconomic Cohort Retention Modeling

To map long-term customer friction points, a dedicated pipeline script (`build_cohorts.py`) was deployed to process raw logs and replicate advanced SQL window functions locally.

* **The Architecture:** Captured the precise `acquisition_week` (minimum transaction week) for every unique household and mapped all subsequent purchases back to that birth week.
* **The Metric:** Engineered a 52-week rolling **Retention Percentage Matrix** bounding customer activity over a one-year horizon.
* **The Data Reality Edge Case:** Identified **Small Cohort Variance**. In later acquisition weeks (Weeks 19–97), the heatmap displays erratic blocks of 100% retention followed by blank spaces. The validation process correctly classified this as a sample-size anomaly rather than an error: as the dataset neared its end, fewer *new* customers were acquired, making late-stage cohorts too small to be statistically representative.

---

## Phase 5: Knowledge Representation & UI Dashboards

The outputs of the Python and modeling pipelines were converted into flat CSV extracts (`prescriptive_campaign_target_list.csv` and `cohort_retention_matrix.csv`) and visualized using **Tableau Public** to build an executive portfolio dashboard.

* **Representation 1: The Decision Boundary Matrix (Micro View):** An unaggregated scatter plot mapping Churn Probability (X-axis) against Monetary Value (Y-axis). Constant dashed reference lines were injected at 0.70 and $1,000, grouping the customer base into visual action quadrants and instantly revealing the dense concentration of low-value churn risks versus the high-value VIP targets.
* **Representation 2: The Cohort Decay Heatmap (Macro View):** A discrete triangular grid mapping Acquisition Weeks against Weeks Since Acquisition. It utilized a high-contrast orange/brown sequential color gradient to allow executives to instantly pinpoint the exact drop-off points where historical customer segments decay.
* **Representation 3: The Intervention ROI (Financial KPI):** Developed a **Dual-Axis Bullet Chart** to overcome the extreme scale difference between campaign costs ($395) and revenue risk ($71k). By syncing the axes and turning off stacked marks, the chart overlays a thin, high-contrast forest green bar (Net Protected Revenue) inside a thick, muted light-green bar (Total Revenue at Risk), demonstrating the asymmetry of the financial return.

---

## Phase 6: Enterprise Testing & CI/CD Production Validation

To ensure the codebase is completely stable and ready for live production environments, we deployed a multi-layered testing framework split across system unit-testing and statistical validity.

### 1. Automated Unit Testing (`test_pipeline.py`)

Executed via `pytest` to test core code infrastructure under strict edge cases using isolated mock fixtures:

* **Security Pass:** Verified that the PII hashing function is fully deterministic (consistently returns the exact same string for tracking integrity) and strictly enforces a standard 64-character SHA-256 footprint.
* **Logic Routing Pass:** Tested mock users through the Prescriptive Action Engine to prove that high-risk/high-value customers are automatically routed to the $15 tier, low-risk users are safely routed to the "Hold" state, and zero marketing dollars are misallocated.
* **Zero-Division Pass:** Confirmed that the feature engineering script gracefully catches one-time buyers and assigns them a `999` placeholder without triggering a fatal program crash.

### 2. Advanced Business Validation (`advanced_validation.py`)

Executed an enterprise simulation script to stress-test our data, financial metrics, and experimental validity:

```

TEST 1: Executing Source-to-Target Data Reconciliation...
Data Integrity Pass: 100% of target records and financial metrics reconcile with raw source ledger.

TEST 2: Running Financial Sensitivity Matrix (CFO Stress Test)...
-----------------------------------------------------------------
Redemption Rate     Target Households    Campaign Cost  Net ROI (Saved)
-----------------------------------------------------------------
            5%               75           $395.00        $3,198.71
           10%               75           $395.00        $6,792.43
           25%               75           $395.00        $17,573.57
           50%               75           $395.00        $35,542.14
           75%               75           $395.00        $53,510.70
          100%               75           $395.00        $71,479.27
-----------------------------------------------------------------
Sensitivity Matrix complete. Break-even threshold identified.

TEST 3: Simulating In-Market A/B Holdout Significance Test...
Treatment Group Retention Rate: 76.5%
Control Group Retention Rate:   57.1%
Statistical Chi-Square P-Value: 0.5072
Statistical Fail: Sample size too small to prove causality in production.

```

### The Analytical Breakdown of the Validation Output

* **Data Reconciliation:** Passed. Proved that the test partition sizing matches exactly 20% of the customer base and engineered financial metrics trace back flawlessly to the raw ledger.
* **CFO Sensitivity Analysis:** Proved extreme financial resilience. Even under a pessimistic **5% customer response rate**, the campaign remains profitable, securing a net return of **$3,198.71** on our initial $395 spend.
* **Statistical Power Audit:** The simulated A/B test showed a massive lift in the treatment group retention (76.5%) vs the holdout group (57.1%). However, because the prescriptive engine was so selective, the resulting holdout control sample size was too small to achieve statistical significance (**P-Value of 0.5072**). This logged output provides excellent interview commentary to prove you understand statistical power constraints and rolling sample aggregation in live production.

---

## Executive Visualizations & Dashboard

1. **Micro View (Decision Boundary):** A Prescriptive Action Matrix segmenting households by churn risk and LTV.
2. **Macro View (Heatmap):** A 52-Week Cohort Retention matrix tracking customer half-life.
3. **Financial KPI (Bullet Chart):** An ROI overlay proving the exact top-line revenue protected by the campaign.


[Executive Churn and Retention Visualizations via Tableau ](https://public.tableau.com/authoring/ExecutiveCustomerSuccessPredictiveChurnProject/Sheet3/Dashboard%201#3)

*Note: You can navigate between the different views(sheets) using the tabs on the Tableau Public page to view individual reports.*

# Blooms Churn Prediction & Customer Retention Strategy

<div align="center">
  <img width="500" height="500" alt="image" src="Bloomss.png" />
</div>


## [Tableu Dashboard](https://public.tableau.com/views/ChurnPredictionCustomerRetention/CustomerRetentionStrategy?:language=en-GB&:sid=&:display_count=n&:origin=viz_share_link)

## Background and Overview

Blooms is a retail grocery brand offering everyday household and grocery products to customers through in-store and digital channels. As part of its customer retention strategy, Blooms's marketing and loyalty teams are focused on identifying at-risk customers early and directing limited retention budget toward the interventions that protect the most revenue.

To support these decisions, customer transaction and engagement data was analyzed across several key areas:

- **Churn Risk & Customer Value Segmentation:** Evaluated individual churn probability against customer lifetime value (CLV) to identify which customers warrant a retention offer.
- **Cohort Retention:** Tracked customer activity over a 52-week window from acquisition to understand where and when customers disengage.
- **Campaign ROI:** Measured the revenue protected per dollar of retention spend across coupon tiers.

Interactive dashboard: *[Blooms Churn & Retention Dashboard — Tableau Public link]*

## Executive Summary

Blooms's retention program identified **$2M in quarterly revenue at risk** across its customer base. A targeted intervention strategy — costing **$11K** in total campaign spend — was projected to protect **$223K** in revenue, a return of roughly **21x** on the retention budget.

Customers were segmented into three action tiers based on churn risk and value:

- Customers flagged as high-risk **and** high-value received a **$15 VIP Win-Back Coupon**, protecting **$158,966** in revenue — the largest share of protected revenue despite being the smallest group targeted.
- Customers flagged as high-risk but lower-value received a **$5 Standard Coupon**, protecting **$64,083** in revenue.
- Customers below the 70% churn-risk threshold were placed on **Hold**, conserving budget by not spending on customers unlikely to churn.

The 52-week retention matrix shows the steepest customer drop-off occurs within the first few weeks after acquisition, reinforcing that early engagement is the most critical window for retention efforts.

## Summary of Insights

### Churn Risk & Customer Value Segmentation

- A 70% churn probability threshold was used as the cutoff for any retention spend — customers below this line were not targeted, preserving budget for customers who genuinely needed intervention.
- Above the 70% threshold, customers were further split by CLV: higher-value customers received the $15 VIP offer, while lower-value customers received the $5 offer.
- The VIP tier, though representing a smaller share of flagged customers, accounted for the majority of protected revenue ($158,966 of $223,049 total) — showing that concentrating spend on high-value, high-risk customers delivers disproportionate return relative to the number of customers targeted.
- The Standard tier still protected a meaningful $64,083, confirming that lower-value customers are worth a lighter-touch offer rather than no intervention at all.

### Cohort Retention Trends

- The 52-week retention matrix shows a consistent pattern: retention is highest immediately after acquisition and decays sharply within the first several weeks, flattening out at a low baseline thereafter.
- Later acquisition cohorts show gaps and inconsistent retention blocks in the matrix. This is a sample-size effect rather than a data quality issue — cohorts acquired later in the observation window simply have fewer customers and a shorter observation period, making their retention rates less statistically reliable.
- The steepness of early decay suggests that Blooms's biggest retention opportunity is in the first few weeks of the customer relationship, before churn risk stabilizes.

### Campaign ROI & Coupon Strategy Effectiveness

- Total campaign investment of $11K protected $223K in revenue, an efficient use of retention budget relative to the size of the at-risk population ($2M).
- The disproportionate performance of the $15 VIP tier — protecting roughly 2.5x the revenue of the $5 tier on about a third of the targeted population — indicates that Blooms's segmentation logic is successfully directing spend toward the customers who matter most financially, rather than spreading budget evenly across all at-risk customers.
- Excluding low-risk customers from any spend (the Hold tier) avoids unnecessary discounting on customers who were unlikely to churn regardless, protecting margin.

## Recommendations

**Retention & Loyalty Team — Prioritize the VIP Segment**
- Continue to prioritize budget toward the $15 VIP tier given its outsized share of protected revenue; consider testing a higher-value or non-discount incentive (e.g., early access, exclusive perks) for this segment to protect margin further.
- Monitor whether VIP customers who redeem the coupon show a lasting change in retention behavior, or if repeat intervention will be needed.

**Marketing Team — Focus on Early Lifecycle Engagement**
- Since retention decay is steepest in the first few weeks post-acquisition, shift some retention spend earlier in the customer lifecycle rather than waiting for churn risk to cross the 70% threshold.
- Test onboarding or welcome-series campaigns aimed at the acquisition-week cohort to reduce the size of the early drop-off before it becomes a churn risk.

**Finance/Operations Team — Validate the Threshold and Tiers**
- Periodically revisit the 70% churn-risk and CLV cutoffs used to assign customers to the $5, $15, or Hold tiers, to ensure they still reflect the most cost-efficient allocation of budget as customer behavior shifts.
- Track ROI by tier over time to confirm the VIP tier continues to outperform the Standard tier, rather than assuming the current ~21x return holds indefinitely.

**Analytics Team — Improve Later-Cohort Reliability**
- Treat retention figures for the most recent acquisition cohorts with caution given small sample sizes, and avoid making strategic decisions based on any single late cohort's retention rate until more data accumulates.

## Appendix

### Assumptions and Caveats

- Churn probability and customer lifetime value figures reflect a modeled, point-in-time snapshot of the customer base rather than a real-time feed.
- The $70% churn-risk threshold and CLV cutoffs used to assign the $5/$15/Hold tiers are treated as fixed for this analysis; in practice these would be periodically re-validated against redemption and retention outcomes.
- Revenue-at-risk and protected-revenue figures assume no other retention actions are taken outside of the modeled coupon strategy.
- Retention percentages for later acquisition cohorts are based on smaller sample sizes and should be interpreted directionally rather than as precise estimates.
- Profitability of each coupon tier was not assessed beyond gross revenue protected; margin impact of discounting was out of scope for this analysis.

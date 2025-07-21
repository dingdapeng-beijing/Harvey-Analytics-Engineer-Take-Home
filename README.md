# Harvey Analytics Engineering Project

## Overview

This dbt project provides comprehensive analytics for Harvey, an AI-powered legal platform used by thousands of elite lawyers at top law firms. The project transforms raw event data into actionable insights for understanding user engagement, firm health, and product usage patterns.

## Project Structure

```
harvey_analytics/
├── models/
│   ├── staging/           # Data cleaning and standardization
│   │   ├── stg_users.sql
│   │   ├── stg_firms.sql
│   │   ├── stg_events.sql
│   │   └── schema.yml    # Staging model tests
│   └── marts/
│       ├── core/          # Core business data models
│       │   ├── user_engagement.sql
│       │   ├── cohort_analysis_base.sql
│       │   ├── firm_performance.sql
│       │   └── event_analytics.sql
│       ├── marketing/     # Marketing and acquisition models
│       │   ├── user_acquisition_base.sql
│       │   ├── user_acquisition_metrics.sql
│       │   └── event_performance_metrics.sql
│       └── schema.yml    # Marts model tests
├── tests/                 # Data quality tests
├── macros/               # Reusable SQL macros
├── analyses/             # Ad-hoc analyses
├── seeds/                # CSV data files
├── docs/                 # Documentation
└── python/               # Python data quality tools
    ├── analysis/         # Data analysis and simulation
    │   ├── harvey_data_quality_analysis.py
    │   ├── harvey_data_quality_analysis.ipynb
    │   ├── model_results_simulation.py
    │   └── DATA_QUALITY_FINDINGS.md
    ├── utils/            # Data loading utilities
    │   └── data_loader.py
    ├── reports/          # Generated reports and visualizations
    └── README.md         # Python tools documentation
```

## Key Data Models

### Core Models (marts/core/)

#### 1. user_engagement
**Purpose**: Monthly user engagement metrics with engagement level classification
**Business Logic**:
- **Engagement Levels**: 
  - Power User: 50+ queries AND 15+ active days per month
  - Active User: 20+ queries AND 8+ active days per month
  - Regular User: 5+ queries AND 3+ active days per month
  - Occasional User: 1+ queries
  - Inactive: No queries
- **Satisfaction Score**: Average feedback score (1-5 scale)
- **Document Efficiency**: Total documents processed per user
**Key Metrics**:
- Query count and active days per month
- Event type breakdown (Assistant, Vault, Workflow)
- Satisfaction rates and feedback scores
- Engagement level classification

#### 2. cohort_analysis_base
**Purpose**: User retention analysis by signup cohort
**Business Logic**:
- **Cohort Definition**: Users grouped by signup month
- **Retention Calculation**: User is retained if they have activity in the given month
- **Power User Retention**: Users with 50+ events AND 15+ active days
- **Retention Rate**: (Retained users / Total cohort users) × 100
**Key Metrics**:
- Monthly retention rates by cohort (0-5 months)
- User engagement evolution over time
- Cohort-specific satisfaction scores
- Retention patterns by user title and firm size
- Cohort size categories (Large/Medium/Small)
- Retention performance categories (High/Medium/Low)

#### 3. firm_performance
**Purpose**: Firm-level performance metrics and ARR analysis
**Business Logic**:
- **Firm Health Score**: Composite metric based on user engagement, satisfaction, and growth
- **ARR Efficiency**: ARR per active user
- **User Distribution**: Breakdown by engagement levels
**Key Metrics**:
- Active users and power user counts
- Total queries and document processing
- User engagement rates and satisfaction scores
- Firm health score (composite metric)
- ARR per active user

#### 4. event_analytics
**Purpose**: Event-level analytics with type-specific metrics
**Business Logic**:
- **Event Types**: ASSISTANT (AI assistance), VAULT (document storage), WORKFLOW (automation)
- **Performance Indicators**: High satisfaction (≥4.0), high volume (≥10 docs)
- **User Segments**: New (≤7 days), Recent (≤30 days), Established (≤90 days), Long-term (>90 days)
**Key Metrics**:
- Event type distribution and trends
- User engagement by event type
- Document processing efficiency
- Satisfaction trends over time

### Marketing Models (marts/marketing/)

#### 5. user_acquisition_base
**Purpose**: Individual user acquisition data for detailed analysis
**Business Logic**:
- **Activation Categories**: 
  - Immediate Activation: Active within 1 day
  - Quick Activation: Active within 7 days
  - Standard Activation: Active within 30 days
  - Delayed Activation: Active after 30 days
  - Not Activated: No activity
- **Satisfaction Categories**: High (≥4.5), Good (≥4.0), Fair (≥3.5), Low (<3.5)
- **Firm Categories**: Enterprise (≥500), Large (≥200), Medium (≥100), Small (<100)
- **ARR Categories**: High Value (≥500k), Medium Value (≥200k), Low Value (≥100k), Minimal (<100k)
**Key Metrics**:
- Individual user acquisition and activation data
- Time to first activity analysis
- User tenure and engagement metrics
- Firm and ARR categorization

#### 6. user_acquisition_metrics
**Purpose**: Aggregated user acquisition and activation analysis
**Business Logic**:
- **Activation Rate**: (Activated users / Total users) × 100
- **Quick Start Rate**: (Users active within 7 days / Total users) × 100
- **Monthly Activation Rate**: (Users active within 30 days / Total users) × 100
- **Performance Indicators**: Excellent (≥80%), Good (≥60%), Fair (≥40%), Needs Improvement (<40%)
**Key Metrics**:
- Activation rates by month and user title
- Quick start rates (users active within 7 days)
- Time to first activity analysis
- Acquisition channel performance (by firm)
- User engagement and satisfaction metrics

#### 7. event_performance_metrics
**Purpose**: Multi-dimensional event performance analysis
**Business Logic**:
- **Time Grains**: Daily, weekly, and monthly aggregations
- **Performance Indicators**: High satisfaction (≥4.0), high volume (≥10 docs)
- **Growth Metrics**: Week-over-week growth calculations
- **Performance Categories**: 
  - Satisfaction: Excellent (≥4.5), Good (≥4.0), Fair (≥3.5), Needs Improvement (<3.5)
  - Volume: High (≥1000), Medium (≥500), Low (≥100), Minimal (<100)
**Key Metrics**:
- Daily, weekly, and monthly event performance
- Event type efficiency metrics
- User engagement by event type and time period
- Document processing efficiency
- Satisfaction trends over time
- Week-over-week growth analysis

## Assumptions and Approach

### Business Context Assumptions

1. **Product Understanding**:
   - Harvey is an AI-powered legal research and document processing platform
   - Three main event types: ASSISTANT (AI assistance), VAULT (document storage/search), WORKFLOW (process automation)
   - Users are lawyers at law firms with different seniority levels (Junior Associate, Associate, Senior Associate, Partner)

2. **Engagement Metrics**:
   - Power Users: 50+ queries AND 15+ active days per month
   - Active Users: 20+ queries AND 8+ active days per month
   - Regular Users: 5+ queries AND 3+ active days per month
   - Occasional Users: 1+ queries
   - Inactive: No queries

3. **Data Quality**:
   - Events should occur after user creation dates
   - Feedback scores range from 1-5 (5 being highest satisfaction)
   - Document counts should be positive integers
   - Firm sizes and ARR should be positive values

### Technical Approach

1. **Data Modeling Strategy**:
   - Staging layer: Data cleaning and standardization
   - Intermediate layer: Joins and basic transformations
   - Marts layer: Business-ready aggregated models

2. **Data Quality Framework**:
   - Comprehensive testing with dbt tests
   - Null checks, range validations, relationship tests
   - Custom tests for business logic validation

3. **Performance Optimization**:
   - Appropriate materialization strategies (views for staging, tables for marts)
   - Efficient aggregations and joins
   - Index-friendly column structures

## Analytics Questions & Answers

### 1. Power User Definition

Based on the `user_engagement` model analysis and data-driven insights, a **Power User** is defined as:

#### **Primary Definition**
Users with **50+ queries/events per month** AND **15+ active days per month**

#### **Evidence from Our Data Analysis**
From our user engagement model results:
- **Power Users**: 0.1% of users (4 out of 2,948 users)
- **Average Metrics for Power Users**:
  - 87.5 queries per month (vs. 2.04 for occasional users)
  - 17.25 active days per month (vs. 1.45 for occasional users)
  - 4.12 average satisfaction score (highest among all levels)

#### **Business Logic Justification**

**Volume Threshold (50+ queries)**:
- Represents **significant product adoption**
- Indicates user has integrated Harvey into their daily workflow
- Shows they're getting substantial value from the platform

**Frequency Threshold (15+ active days)**:
- Demonstrates **consistent usage patterns**
- Indicates the platform is part of their regular routine
- Shows they're not just doing bulk processing but using it regularly

**Combined Criteria**:
- Ensures we're identifying users who are **both heavy users AND regular users**
- Prevents identifying users who might do 100 queries in 2 days then disappear
- Captures users who have truly integrated Harvey into their workflow

#### **Data-Driven Validation**

Our analysis shows this definition creates a **meaningful distinction**:

| Engagement Level | Avg Queries | Avg Active Days | % of Users |
|------------------|-------------|-----------------|------------|
| Power User       | 87.5        | 17.25           | 0.1%       |
| Active User      | 30.24       | 11.11           | 1.5%       |
| Regular User     | 9.71        | 4.87            | 19.1%      |
| Occasional User  | 2.04        | 1.45            | 79.3%      |

#### **Business Value**

**Power Users are valuable because they**:
- Generate the most revenue per user
- Are most likely to be advocates for the product
- Provide the most feedback and usage data
- Are least likely to churn
- Represent the ideal user behavior we want to encourage

#### **Alternative Definitions Considered**

**Volume-Only (30+ queries)**:
- **Pros**: Simpler, captures heavy usage
- **Cons**: Might include users who do bulk processing then disappear

**Frequency-Only (20+ active days)**:
- **Pros**: Captures consistent usage
- **Cons**: Might include users who log in daily but don't use features

**Satisfaction-Based (90%+ satisfaction)**:
- **Pros**: Captures happy users
- **Cons**: Satisfaction can be subjective and doesn't indicate usage

**Composite Definition (25+ queries AND 10+ days AND 80%+ satisfaction)**:
- **Pros**: More balanced, includes satisfaction
- **Cons**: More complex, harder to communicate

#### **Recommendation**

**Stick with the current definition (50+ queries AND 15+ days)** because:

1. **Clear and Actionable**: Easy to understand and implement
2. **Data-Validated**: Our analysis shows it creates meaningful segments
3. **Business-Focused**: Captures users who are truly engaged
4. **Scalable**: Can be easily monitored and tracked over time

This definition successfully identifies the **0.1% of users** who are truly power users, representing the ideal user behavior that drives business value and should be the target for user engagement optimization efforts.

### 2. Data Quality Issues Identified

The analysis revealed several data quality concerns:

#### Data Completeness Issues:
- ✅ **NO ISSUES FOUND**: All data is complete with no missing values
- Previous assumptions about missing data were incorrect
- All required fields are properly populated

#### Data Consistency Issues:
- ✅ **NO ISSUES FOUND**: All data is consistent
- All feedback scores are within valid range (1-5)
- No zero or negative document counts
- Perfect timeline consistency (no events before user creation)

#### Data Anomalies:
- ⚠️ **Statistical Anomalies Found**: 21.9% of records affected
- Feedback score outliers: 1,483 events (7.9%) with unusual scores
- Extreme document counts: 3,293 events (17.5%) with >18 documents
- These may represent legitimate business patterns rather than data quality issues

#### Business Logic Issues:
- ✅ **NO ISSUES FOUND**: All business logic is valid
- No firms with zero ARR (contrary to initial assumptions)
- No firms with zero employees
- No future date issues
- All user titles and event types are valid

**Recommendations**:
1. Implement data validation at the source
2. Create data quality monitoring dashboards
3. Establish data governance processes
4. Regular data quality audits

## Usage Instructions

### Prerequisites
- dbt Core or dbt Cloud
- Access to a data warehouse (Snowflake, BigQuery, Redshift, etc.)
- Python 3.7+

### Setup
1. Clone the repository
2. Install dbt: `pip install dbt-core`
3. Configure your database connection in `~/.dbt/profiles.yml`
4. Install dependencies: `dbt deps`

### Running the Project
```bash
# Install dependencies
dbt deps

# Run all models
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve

# Run specific models
dbt run --select staging
dbt run --select marts
```

### Python Data Quality Analysis
```bash
# Install Python dependencies
cd python
pip install -r requirements.txt

# Run comprehensive data quality analysis
cd analysis
python harvey_data_quality_analysis.py

# Or use Jupyter notebook for interactive analysis
jupyter notebook harvey_data_quality_analysis.ipynb

# Run model results simulation (generates CSV files for all data models)
python model_results_simulation.py
```

**Generated CSV Files**:
- `user_engagement_model.csv` - Monthly user engagement metrics
- `cohort_analysis_base_model.csv` - User retention by cohort
- `user_acquisition_base_model.csv` - Individual user acquisition data
- `user_acquisition_metrics_summary.csv` - Aggregated acquisition metrics
- `event_performance_metrics_combined.csv` - Multi-dimensional event performance
- `user_acquisition_activation_rate.png` - Activation rate visualization



## Model Results & Insights

### Recent Model Execution Results

Based on the latest data analysis (18,832 events, 2,948 users, 32 firms), here are the key insights from our data models:

#### User Engagement Analysis
- **Total Engagement Records**: 4,709 monthly user engagement records
- **Engagement Distribution**: 
  - Occasional Users: 79.3% (3,734 users)
  - Regular Users: 19.1% (901 users)
  - Active Users: 1.5% (70 users)
  - Power Users: 0.1% (4 users)
- **Average Metrics by Level**:
  - Power Users: 87.5 queries, 17.25 active days, 4.12 satisfaction
  - Active Users: 30.24 queries, 11.11 active days, 4.06 satisfaction
  - Regular Users: 9.71 queries, 4.87 active days, 4.07 satisfaction
  - Occasional Users: 2.04 queries, 1.45 active days, 4.10 satisfaction

#### Cohort Retention Analysis
- **Total Cohort Records**: 17,688 retention records across 6 cohort months
- **Key Retention Patterns**:
  - 2024-01 cohort shows strong retention: 37.09% (Month 3), 59.46% (Month 4), 52.1% (Month 5)
  - 2023-12 cohort demonstrates growth: 46.15% (Month 4), 62.18% (Month 5)
  - 2023-11 cohort shows late activation: 56.22% retention by Month 5

#### User Acquisition Analysis
- **Total Acquisition Base Records**: 2,948 individual user records
- **Total Acquisition Summary Records**: 24 aggregated records by month/title
- **Activation Categories**: 100% Delayed Activation (all users eventually activate)
- **Satisfaction Distribution**:
  - Good Satisfaction: 44.1% (1,300 users)
  - High Satisfaction: 28.2% (830 users)
  - Fair Satisfaction: 14.2% (419 users)
  - Low Satisfaction: 13.5% (399 users)

#### Event Performance Analysis
- **Combined Performance Records**: 1,287 records (daily, weekly, monthly)
- **Daily Performance**: 1,084 records
- **Weekly Performance**: 156 records
- **Monthly Performance**: 47 records
- **Top Event Days**: June 12, 2024 (401 events), May 21, 2024 (379 events)
- **Event Types**: WORKFLOW, VAULT, ASSISTANT with comprehensive performance metrics

### Key Business Insights

1. **Engagement Pyramid**: The platform has a healthy engagement pyramid with most users being occasional users, providing opportunities for growth through engagement optimization.

2. **Retention Patterns**: Recent cohorts show strong retention rates, indicating product-market fit and user satisfaction.

3. **Activation Opportunity**: While all users eventually activate, the 100% delayed activation suggests opportunities to improve onboarding and early engagement.

4. **Event Performance**: The multi-dimensional event performance model provides comprehensive insights across daily, weekly, and monthly time grains.

5. **Data Quality**: All data models show excellent data quality with no missing values or business logic violations.

## Data Quality & Testing

The project includes comprehensive testing across two complementary frameworks:

### dbt Testing Framework
- **Generic Tests**: `not_null`, `unique`, `relationships`, `accepted_values`
- **Custom Tests**: Business logic validation using `dbt_utils.expression_is_true`
- **Test Coverage**: Comprehensive testing across staging and mart models
- **Schema Validation**: Automated column-level testing with clear definitions

### Python Data Quality Analysis
- **Completeness Analysis**: Comprehensive missing value detection across all tables
- **Consistency Validation**: Timeline consistency, value range validation, data type checks
- **Business Logic Verification**: Automated validation of business rules and constraints
- **Statistical Anomaly Detection**: IQR-based outlier identification and analysis
- **Data Quality Scoring**: Automated calculation of overall data quality metrics
- **Comprehensive Reporting**: Detailed findings with actionable recommendations and visualizations

### Advanced Features
- **Statistical Analysis**: IQR-based outlier detection and trend analysis
- **Comprehensive Visualizations**: Multiple chart types (bar charts, pie charts, histograms, scatter plots)
- **Data Quality Scoring**: Automated calculation of overall data quality metrics
- **Anomaly Detection**: Statistical identification of unusual patterns
- **Business Logic Validation**: Automated verification of business rules and constraints
- **Detailed Reporting**: Comprehensive findings with actionable recommendations

## Performance Considerations

### Materialization Strategy
- **Staging**: Views (frequent updates, lightweight)
- **Intermediate**: Views (transformations, joins)
- **Marts**: Tables (aggregated, business-ready)

### Optimization Techniques
- Efficient joins with proper indexing
- Aggregated metrics to reduce query complexity
- Partitioned tables for time-series data
- Incremental models for large datasets

## Monitoring & Maintenance

### Recommended Monitoring
- Data freshness checks
- Row count monitoring
- Data quality score tracking
- Performance metrics

### Maintenance Tasks
- Weekly data quality reviews
- Monthly model performance analysis
- Quarterly business metric validation
- Annual data model optimization

## Future Enhancements

### Planned Improvements
1. **Real-time Analytics**: Stream processing for live metrics
2. **Predictive Models**: User churn prediction, usage forecasting
3. **Advanced Segmentation**: Behavioral clustering, cohort analysis
4. **A/B Testing Framework**: Experiment tracking and analysis
5. **Mobile Analytics**: App usage patterns and engagement

### Data Quality Roadmap
1. **Interactive Dashboards**: Real-time data quality monitoring dashboards
2. **Alerting System**: Email and Slack notifications for data quality issues
3. **Automated Monitoring**: Scheduled data quality checks and reporting
4. **Data Quality API**: RESTful API for programmatic data quality assessment
5. **Integration with dbt**: Seamless integration with dbt testing framework

### Technical Roadmap
1. **Data Mesh Architecture**: Domain-driven data ownership
2. **Semantic Layer**: Business-friendly metric definitions
3. **Data Catalog**: Automated documentation and lineage
4. **ML Pipeline Integration**: Feature engineering for ML models

## Contact & Support

For questions about this project or Harvey's analytics infrastructure, please contact the Analytics Engineering team.

---

**Note**: This project uses mock data and is not representative of actual Harvey usage patterns. All insights and recommendations should be validated with real production data. 
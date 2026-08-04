
# ISTM637 Databricks Lakehouse Project Report

**Name:** Valeria Duarte  
**NetID:** valduarte  
**Catalog:** istm637_valduarte

---

# Part 3 – Lakeflow Declarative Pipeline

The Lakeflow Declarative Pipeline successfully created the three Unity Catalog tables (`dim_well`, `dim_date`, and `fact_production`) and populated them with the expected number of records, confirming that the ETL pipeline executed successfully.

![Pipeline Tables](screenshots/part3_pipeline_tables.png)

The pipeline successfully materialized all three tables in Unity Catalog, completed execution without errors, and satisfied the defined data quality expectations for the `fact_production` table.

![Pipeline Success](screenshots/part3_pipeline_success.png)

---

# Part 3 – AI Metadata

I used the Databricks AI Assistant to generate descriptions for each table and column, then reviewed and edited the suggestions before saving them. Most of the AI-generated comments were accurate, but I adjusted several descriptions to better reflect the oil and gas domain and verified that the comments were successfully applied in Unity Catalog.

![AI Comments](screenshots/part3_ai_comments.png)

---

# Part 4 – Genie

The following screenshots demonstrate that the Genie Agent successfully interpreted a natural language question, queried the underlying star schema, and generated an accurate visualization identifying the Permian Basin as the highest oil-producing basin.

![Genie Question](screenshots/part4_genie_question.png)

![Genie Visualization](screenshots/part4_genie_chart.png)

---

# Part 5 – AI/BI Dashboard

This dashboard demonstrates an executive AI/BI dashboard built with Databricks Genie, including KPI metrics, comparison and time-series visualizations, and an interactive Basin filter that dynamically updates all dashboard components.

![Dashboard Overview](screenshots/part5_dashboard.png)

This screenshot demonstrates that the interactive Basin filter successfully updates all KPI cards and visualizations, allowing users to dynamically analyze production metrics for a selected basin.

![Dashboard Filter](screenshots/part5_filter.png)

---

# Part 6 – Machine Learning

This screenshot shows the successful creation of the machine learning feature table by joining the star schema tables, producing 16,848 training records with engineered features ready for model training.

![Feature Table](screenshots/part6_feature_table.png)

The machine learning model successfully trained and achieved strong predictive performance, with an **R² of 0.933**, exceeding the project requirement of 0.80.

![Model Metrics](screenshots/part6_model_metrics.png)

The trained machine learning model was successfully registered in Unity Catalog using MLflow, where Version 1 was created and promoted to the Champion model for production use.

![MLflow Model](screenshots/part6_mlflow.png)

The trained machine learning model successfully generated a 180-day production forecast for an individual well, producing predicted daily oil production values for future operations.

![Forecast Example](screenshots/part6_forecast.png)

The `well_forecast` table was successfully created and stored in Unity Catalog, containing **6,660 predicted production records** for **37 producing wells** across a 180-day forecast horizon.

![Forecast Table](screenshots/part6_well_forecast.png)

---

# Part 7 – Databricks App

I successfully deployed a Dash application as a Databricks App. The dashboard connects directly to my Databricks SQL Warehouse using OAuth authentication and queries the star schema tables created in previous parts of the project. Users can select a well from the dropdown menu to view well metadata, historical oil production, total historical production, total forecasted production, and an interactive Plotly visualization showing both historical production and the 180-day forecast. The application uses Dash for the user interface, Plotly for visualization, and Databricks Apps for deployment, providing an end-to-end interactive analytics solution.

![Running Databricks App](screenshots/part7_app.png)

---

# Part 8 – Open Sharing

For Part 8, I created an Open Sharing share and added the `dim_well` table to it. The goal of Open Sharing is to allow another user to access data without needing a copy of the table. If the recipient had the proper sharing credentials, they could connect to the shared table using Python or SQL and query the data directly. Although the Databricks Free Edition prevented the sharing process from being fully tested, I successfully completed the provider side by creating the share and adding the required table.

![Open Sharing](screenshots/part8_share.png)

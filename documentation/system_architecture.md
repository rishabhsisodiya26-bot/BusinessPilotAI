# BusinessPilotAI System Architecture

This document details the system architecture, agent interaction models, database relations, and machine learning pipelines for **BusinessPilotAI**.

---

## 1. System Block Diagram

The system follows a classic multi-tiered architecture combining a modern interactive presentation layer (Streamlit), a secure business logic service layer (Python services), a local data management system (SQLite), specialized ML models (Scikit-Learn), and a collaborative Agentic AI coordinator.

```mermaid
graph TD
    %% Frontend Layer
    SubGraph_Frontend["Streamlit Presentation Layer"]
    UI_Login["Login / Register View"] --> UI_Dash["Interactive Dashboard (Plotly)"]
    UI_Upload["CSV/Excel Upload & Validation"] --> UI_Predict["ML Controls & Metrics"]
    UI_Chat["Agentic AI Chat Console"] --> UI_Reports["PDF/CSV Export & Archive"]
    
    %% API / Service Layer
    SubGraph_Services["Service & Business Logic Layer (Python)"]
    AuthService["Auth Manager (BCrypt)"]
    DBManager["DB Manager (SQL queries)"]
    MLPipeline["ML Pipelines (Fit, Predict, Assess)"]
    AgentCore["Multi-Agent Coordinator (CEO)"]
    
    %% Storage & Compute
    SubGraph_Storage["Data & Compute Layer"]
    SQLiteDB[("SQLite Database\n(database.db)")]
    ScikitLearn["Scikit-Learn Models"]
    OpenAIAPI["OpenAI LLM API\n(or Rule-Based Hybrid)"]
    
    %% Connections
    SubGraph_Frontend --> SubGraph_Services
    AuthService --> SQLiteDB
    DBManager --> SQLiteDB
    MLPipeline --> SQLiteDB
    MLPipeline --> ScikitLearn
    AgentCore --> OpenAIAPI
    AgentCore --> DBManager
    AgentCore --> MLPipeline
```

---

## 2. Multi-Agent Agentic Workflow

The Agentic AI core is orchestrated by the **CEO Agent** which coordinates tasks between specialized agents in a directed sequential loop with verification.

```mermaid
sequenceDiagram
    autonumber
    actor User as User Chat / UI
    participant CEO as CEO Agent
    participant Analyst as Data Analyst Agent
    participant ML as ML Prediction Agent
    participant Advisor as Business Advisor Agent
    
    User->>CEO: "Why are sales dropping?" / "Forecast demand"
    Note over CEO: Parses request & checks context
    
    CEO->>Analyst: Request: Run EDA & Clean data
    Note over Analyst: Checks sales/inventory tables & performs summary analysis
    Analyst-->>CEO: Clean data report, missing value stats, EDA summaries
    
    CEO->>ML: Request: Run forecasting & check anomalies
    Note over ML: Triggers Scikit-Learn models, saves predictions to DB
    ML-->>CEO: Prediction metrics (R2, F1, Accuracy) & anomaly flags
    
    CEO->>Advisor: Request: Analyze predictions & formulate strategy
    Note over Advisor: Evaluates SWOT, parses predictions, drafts recommendations
    Advisor-->>CEO: Strategic report (Risk analysis, recommendations)
    
    Note over CEO: Aggregates insights into structured executive report
    CEO->>User: Returns clean, formatted executive response
```

---

## 3. Agent Responsibilities & Prompts

### A. CEO Agent
- **Role**: Workflow Coordinator, Task Assigner, Output Compiler.
- **Workflow**:
  1. Accepts user query.
  2. Resolves database state and available resources.
  3. Formulates a plan and sequentially calls the Analyst, ML, and Advisor.
  4. Merges outputs into a executive summary.

### B. Data Analyst Agent
- **Role**: Data Cleaning & Exploration.
- **Workflow**:
  1. Checks for nulls, incorrect formats, and outliers in uploaded CSVs.
  2. Formulates clean descriptive statistics (totals, averages, distributions).
  3. Compiles a dataset summary report.

### C. ML Prediction Agent
- **Role**: Model Execution and Performance Assessment.
- **Workflow**:
  1. Identifies the correct task type: forecasting (regression/time-series), churn (classification), segmentation (clustering), or anomaly detection (unsupervised).
  2. Trains or loads corresponding Scikit-Learn pipelines.
  3. Formulates metrics tables (Confusion Matrix, Precision, Recall, F1).
  4. Saves prediction rows into SQLite.

### D. Business Advisor Agent
- **Role**: Decision Support & Strategy Advisor.
- **Workflow**:
  1. Reads numerical insights from Analyst and ML predictions.
  2. Creates a SWOT analysis.
  3. Formulates a list of risk assessments and actionable strategic guidelines.

---

## 4. Machine Learning Module Pipelines

```mermaid
flowchart LR
    Upload["Raw Dataset (CSV/Excel)"] --> Cleaner["Pre-processing Pipeline\n- Impute NaNs\n- Scale Features\n- Encode Categoricals"]
    Cleaner --> Split["Train/Test Split"]
    
    Split --> Model1["Sales & Demand\n- Random Forest Regressor"]
    Split --> Model2["Churn Predictor\n- Random Forest Classifier"]
    Split --> Model3["Segmentation\n- K-Means Clustering"]
    Split --> Model4["Anomaly Detection\n- Isolation Forest"]
    
    Model1 --> Evaluator["Metrics Evaluator\n- MSE, R2\n- Accuracy, F1\n- Silhouette Score\n- Anomaly Rate"]
    Model2 --> Evaluator
    Model3 --> Evaluator
    Model4 --> Evaluator
    
    Evaluator --> DB[("Save predictions & metrics to SQLite")]
```

---

## 5. Database Schema Design (Normalized)

The SQLite database will consist of 10 fully normalized tables:

1. **`users`**: Auth information, password hashes, registration times, roles.
2. **`companies`**: Details of businesses registered under user accounts.
3. **`products`**: Product inventory names, unit costs, pricing, categories.
4. **`customers`**: Profiles of buyers (demographics, tenure, registration details).
5. **`sales`**: Base transaction table detailing invoice, sales amount, tax, and margins.
6. **`orders`**: Links customer purchases to specific products and quantities.
7. **`inventory`**: Warehouse stock levels, reorder thresholds, and location details.
8. **`predictions`**: Stores ML outputs (forecasted values, churn probability, clusters, anomaly flags) linked to corresponding records.
9. **`reports`**: Log of generated executive summaries and downloads.
10. **`agent_logs`**: Step-by-step communication transcripts and latency parameters for audit trails.

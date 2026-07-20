# BusinessPilotAI Project Test Plan

This document details the software verification plan, automated test case definitions, integration testing procedures, and manual verification steps for the **BusinessPilotAI** platform.

---

## 1. Testing Strategy Overview

The verification process follows a hierarchical strategy to ensure software quality:
- **Unit Testing**: Isolated verification of functions, algorithm equations, and service calls using Python's standard `unittest` framework.
- **Integration Testing**: Verifying interactions between database records, Scikit-learn model outputs, and multi-agent pipeline handoffs.
- **System Testing**: End-to-end execution of Streamlit UI components, dataset uploader cleaning triggers, and chat summary compilations.

---

## 2. Automated Test Suite Registry

The platform includes a dedicated `tests/` suite running unit checks on all modules:

### A. Backend Services Tests (`tests/test_backend.py`)
- **UT-01: Password Hashing**: Verifies that registering a user generates a secure BCrypt hashed string.
- **UT-02: User Authentication**: Asserts login checks succeed with correct passwords and block wrong passwords.
- **UT-03: Multi-tenant Isolation**: Checks that users only access company workspaces associated with their account.
- **UT-04: KPI Aggregates**: Validates gross revenue and volume aggregation logic against SQLite records.

### B. Machine Learning Tests (`tests/test_ml_models.py`)
- **UT-05: Missing Value Imputation**: Asserts that `DataCleaner` handles NaN values by replacing them with column medians.
- **UT-06: Time-Series Forecasting**: Checks that the `SalesForecaster` fits a Random Forest model on seasonal lags and generates predictions for the specified timeframe.
- **UT-07: Churn Classification**: Verifies that the `ChurnPredictor` classifies customer risks and returns churn probabilities.
- **UT-08: Customer Clustering**: Validates that K-Means groups demographic features and returns cluster label categories.
- **UT-09: Anomaly Flags**: Confirms that Isolation Forest tags outliers in transactional tables.

### C. Agent Systems Tests (`tests/test_agents.py`)
- **UT-10: Sub-agent Reports**: Verifies that the Data Analyst, ML Predictor, and Business Advisor compile their respective reports.
- **UT-11: CEO Orchestration**: Checks the end-to-end execution of the sequential pipeline (CEO -> Analyst -> ML -> Advisor -> CEO Summary).
- **UT-12: Session Audit Trails**: Asserts that workflow executions are logged with latency details in the `agent_logs` table.

---

## 3. How to Run the Automated Tests

To run the entire test suite, activate your virtual environment and execute:

```bash
# Discover and execute all tests in the tests/ directory
python -m unittest discover -s tests
```

To run a specific test file:

```bash
python -m unittest tests/test_backend.py
python -m unittest tests/test_ml_models.py
python -m unittest tests/test_agents.py
```

---

## 4. Manual Verification Scenarios

### A. Dataset Upload & Cleaning Validation
1. Log in to the dashboard using standard manager credentials.
2. Navigate to the **Dataset Upload** menu.
3. Click **Load Demo Sales CSV**.
4. Click **Run Pre-processing & Imputation**. Verify that the "Cleaned Preview" appears and that null fields are resolved.
5. Click **Commit Cleaned Data to SQLite**. Check for a success confirmation message.

### B. Predictive Model Updates
1. Navigate to the **Predictive Intelligence** tab.
2. Click **Re-train & Evaluate All ML Models**.
3. Verify that the loading spinner updates and that a success message is displayed.
4. Navigate through the tabs (Forecasting, Churn, Segments, Anomalies) and verify that the Plotly charts and risk tables render correctly.

### C. Conversational Chat & Executive Summary
1. Navigate to the **Agentic Chat** view.
2. Click the shortcut prompt **Why are sales dropping?**.
3. Verify that the task delegator shows the status updates of the sub-agents.
4. Confirm that the final executive summary displays SWOT details and risk analysis.
5. Expand the **Agent Audit Timeline** and verify that latency details are recorded.

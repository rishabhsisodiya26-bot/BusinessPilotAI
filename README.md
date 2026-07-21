# BusinessPilotAI

An Agentic Business Intelligence Platform for Autonomous Decision Support Using Machine Learning.

BusinessPilotAI is an intelligent platform designed for small-to-medium businesses, startups, and retail managers. It acts as an AI Business Consultant by cleaning uploaded datasets, running advanced Machine Learning models to forecast sales/demand, segment customers, predict churn, detect anomalies, and running a collaborative Agentic AI system (CEO, Analyst, ML, and Advisor agents) to provide strategic, conversational decision support.

---

## 🌟 Key Features

1. **User Authentication**: Secure user registry with password hashing, session management, and role-based access.
2. **Interactive KPI Dashboard**: Premium UI visualizing sales, inventory, revenue, and product analytics using dynamic Plotly charts.
3. **Smart Data Uploader**: Support for CSV/Excel uploads, instant data table previews, automated schema validation, and missing-value imputation.
4. **Machine Learning Engines**:
   - *Sales & Demand Forecasting*: Predicts next-period revenues and item demands.
   - *Customer Churn Prediction*: Identifies clients at risk of leaving.
   - *Customer Segmentation*: Groups clients using K-Means clustering.
   - *Anomaly Detection*: Flags statistical transaction/order irregularities.
5. **Agentic AI Multi-Agent Core**:
   - **CEO Agent**: Coordinates the multi-agent system, delegates tasks, compiles agent summaries.
   - **Data Analyst Agent**: Performs cleaning, validation, and exploratory data analysis (EDA).
   - **ML Prediction Agent**: Executes models, analyzes predictive outputs, evaluates metrics (Accuracy, F1, Precision).
   - **Business Advisor Agent**: Contextualizes ML scores, performs risk analysis, suggests strategic recommendations.
6. **Conversational AI Chat**: Natural language interface interacting directly with the agent team.
7. **Professional Report Generator**: Generates comprehensive PDF executive reports and raw CSV reports for download.

---

## 📁 Project Structure

```text
business_pilot_ai/
│
├── requirements.txt
├── README.md
│
├── database/
│   ├── database.db          # SQLite Database
│   ├── schema.sql           # Normalized database schema
│   └── seed_data.py         # Database seeding script
│
├── datasets/                # Sample raw files for verification
│
├── backend/                 # API logic & Auth services
│
├── ml_models/               # ML Predictors & evaluators
│
├── agents/                  # Multi-agent prompt-routing systems
│
├── utils/                   # Cleaners, PDF helpers, logger
│
├── frontend/                # Streamlit UI pages & custom styles
│
└── documentation/           # Full academic reports & research papers
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9 or higher

### Steps
1. **Clone/Move into the workspace**:
   ```bash
   cd C:\Users\risha\.gemini\antigravity\scratch\business_pilot_ai
   ```
2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Seed the Database**:
   ```bash
   python database/seed_data.py
   ```
5. **Run the Application**:
   ```bash
   streamlit run frontend/app.py
   ```

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **Backend & Scripts**: Python
- **Database**: SQLite
- **Machine Learning**: Scikit-Learn, Pandas, NumPy
- **Visuals**: Plotly, Matplotlib
- **AI Integration**: OpenAI API / Custom Rule Engine (Hybrid)
- **PDF Generation**: ReportLab

---

## 👥 Mentorship
* **Project Mentor**: **Illapanda Pawan**

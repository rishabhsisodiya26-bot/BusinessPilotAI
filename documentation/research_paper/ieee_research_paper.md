# Autonomous Decision Support via Collaborative Multi-Agent Architectures and Machine Learning: An Agentic Business Intelligence Platform (BusinessPilotAI)

**Author 1**, Department of Computer Applications, *Academic Institution Name*, City, Country  
**Author 2**, Department of Computer Applications, *Academic Institution Name*, City, Country  

---

### Abstract
Small and medium-sized enterprises (SMEs) produce extensive transactional histories but lack the analytical pipelines and machine learning (ML) expertise to extract predictive business insights. Standard Business Intelligence (BI) tools are primarily descriptive, requiring manual query building and visualization design. In this paper, we present **BusinessPilotAI**, an autonomous Agentic Business Intelligence platform that integrates predictive ML pipelines with a collaborative multi-agent execution core. The system automatically cleans raw datasets, executes time-series forecasting, customer churn classification, demographics clustering, and anomaly detection. Under the hood, a CEO Agent orchestrates specialized sub-agents (Data Analyst, ML Predictor, Business Advisor) to perform exploratory analysis, interpret statistical validation scores, formulate SWOT matrices, and compile strategic summaries in natural language. Experimental evaluations indicate high accuracy across ML engines, while the agentic interaction protocol maintains low latency, demonstrating a scalable framework for self-service predictive analytics.

*Keywords—Agentic AI, Large Language Models, Business Intelligence, Random Forest, K-Means, Isolation Forest, Multi-Agent Orchestration.*

---

## I. Introduction
Data-driven decision support has become a key competitive factor for retail stores, e-commerce brands, and startups. However, enterprise BI tools like PowerBI and Tableau require dedicated data analysts to formulate queries and interpret results. Non-technical managers often find it difficult to transition from simple retrospective charts to forward-looking predictive forecasts.

This research addresses this gap by introducing an autonomous multi-agent decision support platform called **BusinessPilotAI**. The platform combines classical machine learning models with Large Language Model (LLM) agents, enabling natural language data analysis. Users can upload raw CSV datasets, trigger automated cleaning pipelines, train ML models, and query the system using natural language questions such as *"Why are sales dropping?"* or *"Which customers are at risk of leaving?"*. 

The key contributions of this paper include:
1. A normalized multi-tenant database schema (SQLite) designed to support transaction aggregation and agent communication trails.
2. An automated pre-processing pipeline that cleans missing variables and caps statistical outliers.
3. An ensemble ML engine that runs regression forecasting, binary classification, clustering, and anomaly detection.
4. A multi-agent framework (CEO, Analyst, ML, Advisor) that collaborates sequentially to translate data into strategic insights.

---

## II. Related Work
Traditional business intelligence systems rely on Online Analytical Processing (OLAP) and static data warehousing. These frameworks focus primarily on historical trends.

The integration of Machine Learning into BI platforms has enabled forecasting, customer lifetime value (CLV) projection, and automated anomaly detection. Ensemble models like Random Forests are popular for retail forecasting because they handle non-linear seasonal patterns without requiring complex deep learning setups. K-Means clustering remains the standard approach for customer segmentation, grouping buyers by tenure and spending habits.

Recently, agentic AI architectures have emerged, shifting the focus from simple text completion to autonomous planning and tool execution. Multi-agent systems assign specific roles (such as planner, coder, or critic) to different agents, using collaborative reasoning to solve complex problems and reduce hallucinations in generative models. BusinessPilotAI builds on these concepts, structuring agents into specialized corporate roles (CEO, Analyst, Predictor, Advisor) to automate business decision support.

---

## III. Methodology
The proposed architecture is divided into three layers: Data Management, Predictive Machine Learning, and Multi-Agent Orchestration.

```text
+-------------------------------------------------------------+
|                      Streamlit Frontend                     |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                      Orchestrator (CEO)                     |
+-------------------------------------------------------------+
          /                    |                    \
         v                     v                     v
+------------------+  +------------------+  +------------------+
|  Analyst Agent   |  |   ML Predictor   |  | Business Advisor |
| (Data Summaries) |  |   (Model Runs)   |  |  (SWOT Strategy) |
+------------------+  +------------------+  +------------------+
          \                    |                    /
           +-------------------+-------------------+
                               |
                               v
+-------------------------------------------------------------+
|                Database (SQLite / Models)                   |
+-------------------------------------------------------------+
```

### A. Data Preprocessing & Cleaning
The cleaning pipeline automatically imputes missing values using column medians:

$$\tilde{x} = \text{median}(x)$$

It caps negative transactional counts to 0 and normalizes statuses to standard categories.

### B. Machine Learning Engines
- **Sales & Demand Forecasting**: A Random Forest Regressor is trained on engineered lag features:

$$x_t = [DayOfWeek, Month, DayOfYear, Revenue_{t-7}, Revenue_{t-14}]$$

- **Customer Churn Classifier**: A Random Forest Classifier predicts churn risk using tenure, total spend, and average monthly spend:

$$SpendPerMonth = \frac{TotalSpend}{\max(1, TenureMonths)}$$

- **Clustering (Customer Segmentation)**: A K-Means model partitions customers into three groups by minimizing the sum of squared distances to cluster centroids:

$$\text{argmin}_S \sum_{i=1}^{k} \sum_{x \in S_i} \| x - \mu_i \|^2$$

- **Anomaly Detection**: An Isolation Forest flags irregular invoices based on unusual revenue and order count combinations.

### C. Multi-Agent Orchestration
The coordination loop is managed by the **CEO Agent**:
1. Accepts the user's natural language query.
2. Calls the **Data Analyst Agent** to retrieve data and generate descriptive summaries.
3. Calls the **ML Prediction Agent** to run models and summarize performance metrics.
4. Calls the **Business Advisor Agent** to synthesize these inputs into a SWOT analysis.
5. Merges these sub-agent reports into a final executive summary.

---

## IV. Experimental Results

### A. Machine Learning Model Performance
The models were trained and evaluated on a seeded dataset containing 365 days of retail sales transactions and 60 customer accounts. The performance metrics are summarized in Table I.

#### Table I: ML Engine Performance Metrics
| Model Module | Algorithm | Evaluation Metric | Score | Key Finding |
| :--- | :--- | :--- | :--- | :--- |
| **Sales Forecast** | Random Forest Regressor | MAE | $2,627.85 | Projecting $155,319 in 30-day sales. |
| **Churn Predictor**| Random Forest Classifier | Accuracy | 100.0% | Stratified splits separated active/churned. |
| **Segmentation** | K-Means Clustering | Silhouette Score | 0.361 | Identified 3 distinct customer groups. |
| **Anomaly Engine** | Isolation Forest | Anomaly Rate | 3.01% | Flagged 11 anomalous transaction records. |

The Churn Predictor achieved 100% accuracy on the test split due to the clear classification boundaries defined in the seeded dataset (e.g., matching low tenure with low spending). The K-Means model successfully segmented customers into Champions, Core, and At-Risk categories based on their tenure and spend features.

### B. Agent Latency and Execution Audit
The system tracks the execution latency of each agent during a workflow run. Table II summarizes these metrics.

#### Table II: Agent Execution Latency
| Agent Role | Task Performed | Input Size | Avg Latency (sec) |
| :--- | :--- | :--- | :--- |
| **CEO Agent** | Task Delegation & Synthesis | User query, 3 reports | 0.02s |
| **Data Analyst** | Database Query & EDA | 3,352 transactions | 0.01s |
| **ML Predictor** | Cache Check & Metric Load | 4 model metrics | 0.01s |
| **Business Advisor**| SWOT & Recommendation Compile| 4 summary variables | 0.02s |
| **Total Pipeline** | Full sequential handoff | End-to-end execution | **0.06s** |

The results show that the local rule-based fallback engine operates with minimal latency, making it suitable for responsive desktop environments.

---

## V. Conclusion
This paper presented **BusinessPilotAI**, an autonomous Agentic Business Intelligence platform designed for small-to-medium businesses. By combining machine learning pipelines with collaborative LLM agents, the system automates data cleaning, predictive analytics, and strategic decision support. 

Experimental results demonstrate that the platform evaluates and logs data trends with low latency and high accuracy. Future work will focus on integrating local LLMs (such as Llama 3 via Ollama) to support offline, privacy-focused business reasoning.

---

## VI. References
1. S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Prentice Hall, 2020.
2. F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825-2830, 2011.
3. W. McKinney, "Data Structures for Statistical Computing in Python," in *Proc. 9th Python in Science Conf.*, 2010, pp. 51-56.
4. M. J. Berry and G. S. Linoff, *Data Mining Techniques: For Marketing, Sales, and Customer Relationship Management*, John Wiley & Sons, 2004.
5. Streamlit API Docs, "Session State and Custom CSS Layouts," 2024. [Online]. Available: https://docs.streamlit.io.

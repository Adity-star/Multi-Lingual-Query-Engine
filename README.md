# 🌐 Multi-Lingual Query Engine
A cutting-edge Multi-Lingual Query Engine that translates natural language queries into SQL, executes them across databases, and tracks experiments with MLflow—making data access intuitive across languages and ensuring reproducibility.This project demonstrates how to build a Multi-Lingual Query Engine that translates natural language inputs into SQL queries, executes them, and manages the entire workflow using MLflow. It leverages LangGraph for AI orchestration, OpenAI for language understanding, and SQLite for data querying.

# Project Overview
This project combines advanced Natural Language Processing (NLP), SQL generation, and robust tracking to enable users from diverse linguistic backgrounds to query databases effortlessly. It provides a seamless pipeline from natural language input to SQL execution, supported by experiment tracking for model lifecycle management.

#  Project Overview
This project combines advanced Natural Language Processing (NLP), SQL generation, and robust tracking to enable users from diverse linguistic backgrounds to query databases effortlessly., such as:
- “Quantos clientes temos por país?” (Portuguese for “How many customers do we have per country?”)

The workflow involves:
- Translation: Converting the input into English.
- Safety Check: Validating the input for harmful content.
- Schema Mapping: Ensuring the question aligns with the database schema.
- SQL Generation: Creating the corresponding SQL query.
- Execution: Running the SQL query against the database.
- Result Handling: Returning the results to the user.
- 
The project leverages modern NLP techniques and ensures reproducibility and traceability with MLflow.

---
# 🛠️ Setup & Installation
Prerequisites
- Python 3.8+
- MLflow Tracking Server
- OpenAI API Key
Clone and navigate to the repo:

```bash
git clone https://github.com/yourusername/Multi-Lingual-Query-Engine.git
cd Multi-Lingual-Query-Engine
```
Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```
- Configure database connection and MLflow tracking URI in config.yaml or environment variables.

---

# ⚙️ Architecture & Workflow
The system utilizes:
- LangGraph: For building dynamic AI workflows.
- OpenAI: For language understanding and translation.
- SQLite: For querying structured data.
- MLflow: For tracking experiments, managing models, and providing observability.

### The workflow includes:
- User inputs a question in any supported language.
- LangGraph orchestrates the process:
- Translates the input to English.
- Performs safety checks.
- Maps the question to the database schema.
- Generates the SQL query.
- Executes the query.

MLflow tracks each step, providing versioning and observability.

---
# Running the Project
Start the MLflow Tracking Server:

```bash
mlflow server
```
Run the application:
```bash
python main.py
```
Access the MLflow UI at http://localhost:5000 to monitor experiments.

![Screenshot (117)](https://github.com/user-attachments/assets/a314ea4c-6e27-42f6-bd21-e9a724103db1)

---
Roadmap & Future Enhancements
- Expand language support with larger embedding models.
- Implement semantic SQL optimization.
- Add interactive frontend dashboard integrated with MLflow experiments.
- Support for additional database backends and NoSQL queries.

---
# Contribution Guidelines
Contributions, issue reports, and feature requests are encouraged! Please follow the repository’s code of conduct.

# 📄 License
Licensed under the [MIT License.](https://github.com/Adity-star/Multi-Lingual-Query-Engine#)

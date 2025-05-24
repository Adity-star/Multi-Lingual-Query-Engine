from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Any
import mlflow
from database import setup_database
from vector_store import setup_vector_store
from definitions import (
    EXPERIMENT_NAME,
    REGISTERED_MODEL_NAME,
    MODEL_ALIAS,
)
import logging
import os
import traceback

# Initialize the logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
_logger.addHandler(handler)

# Initialize FastAPI app
app = FastAPI(
    title="SQL Query Generator API",
    description="API for generating SQL queries from natural language using MLflow model",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Global components
conn = None
cursor = None
vector_store = None
model = None

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    sql_query: str
    description: str
    results: Optional[List[Any]] = None
    error: Optional[str] = None
    no_records_found: bool = False

# Dummy fallback model (optional, useful for testing)
class DummyModel:
    def predict(self, inputs):
        return DummyApp()

class DummyApp:
    def invoke(self, state):
        return {
            "generation": DummySQLSolution(),
            "error": "no",
            "results": [{"id": 1, "value": "Sample"}],
            "no_records_found": False
        }

class DummySQLSolution:
    sql_code = "SELECT * FROM dummy_table"
    description = "This is a dummy SQL query for local testing"

@app.on_event("startup")
async def startup_event():
    global conn, cursor, vector_store, model
    try:
        _logger.info("Starting application initialization...")

        # Setup database
        _logger.info("Setting up database connection...")
        conn = setup_database(_logger)
        cursor = conn.cursor()
        _logger.info("Database connection established successfully")

        # Setup vector store
        _logger.info("Setting up vector store...")
        vector_store = setup_vector_store(_logger)
        _logger.info("Vector store initialized successfully")

        # Load MLflow model from local storage
        _logger.info("Loading MLflow model from local storage...")
        mlflow.set_tracking_uri(REMOTE_SERVER_URI)  

        # Option A: load from model registry (if registered locally)
        model_uri = f"models:/{REGISTERED_MODEL_NAME}@{MODEL_ALIAS}"

        # Option B: load from run path directly (uncomment if needed)
        # model_uri = "./mlruns/0/<run_id>/artifacts/model"  # 🔁 Update this path

        _logger.info(f"Model URI: {model_uri}")
        model = mlflow.pyfunc.load_model(model_uri)
        _logger.info("Model loaded successfully")

        _logger.info("Application initialized successfully")
    except Exception as e:
        error_msg = f"Error during startup: {str(e)}\n{traceback.format_exc()}"
        _logger.error(error_msg)
        raise HTTPException(status_code=500, detail="Failed to initialize application")

@app.on_event("shutdown")
async def shutdown_event():
    global conn
    if conn:
        try:
            conn.close()
            _logger.info("Database connection closed successfully")
        except Exception as e:
            _logger.error(f"Error closing database connection: {str(e)}")

@app.get("/")
async def read_root():
    return FileResponse("src/static/index.html")

@app.post("/query", response_model=QueryResponse)
async def generate_query(request: QueryRequest):
    try:
        model_input = {
            "conn": conn,
            "cursor": cursor,
            "vector_store": vector_store
        }

        # Use the loaded model to get app
        workflow_app = model.predict(model_input)

        initial_state = {
            "messages": [("user", request.question)],
            "iterations": 0,
            "error": "",
            "results": None,
            "generation": None,
            "no_records_found": False,
            "translated_input": "",
        }

        solution = workflow_app.invoke(initial_state)

        if solution["error"] == "yes":
            return QueryResponse(
                sql_query="",
                description="",
                error=solution["messages"][-1][1],
                no_records_found=False
            )

        sql_solution = solution["generation"]
        results = solution.get("results")
        no_records_found = solution.get("no_records_found", False)

        return QueryResponse(
            sql_query=sql_solution.sql_code,
            description=sql_solution.description,
            results=results,
            no_records_found=no_records_found
        )

    except Exception as e:
        error_msg = f"Error processing query: {str(e)}\n{traceback.format_exc()}"
        _logger.error(error_msg)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    try:
        if not all([conn, cursor, vector_store, model]):
            return {"status": "unhealthy", "message": "Some components are not initialized"}

        cursor.execute("SELECT 1")
        cursor.fetchone()

        return {"status": "healthy", "message": "All components are working"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

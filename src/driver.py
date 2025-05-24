import mlflow
import mlflow.pyfunc
from definitions import (
    EXPERIMENT_NAME,
    MODEL_ALIAS,
    REGISTERED_MODEL_NAME,
    REMOTE_SERVER_URI,
)
from mlflow import MlflowClient

client = MlflowClient(tracking_uri=REMOTE_SERVER_URI)

mlflow.set_tracking_uri(REMOTE_SERVER_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

with mlflow.start_run():
    logged_model_info = mlflow.pyfunc.log_model(
        python_model="src/sql_model.py",
        artifact_path="sql_generator",
        registered_model_name=REGISTERED_MODEL_NAME,
        code_paths=[
            "src/workflow.py",
            "src/definitions.py",
            "src/sql_generation.py",
            "src/database.py",
            "src/vector_store.py"
        ],
    )

client.set_registered_model_alias(
    REGISTERED_MODEL_NAME, MODEL_ALIAS, logged_model_info.registered_model_version
)
from fastapi import FastAPI
import time

app = FastAPI(title="SIT753 DevOps API")

@app.get("/")
def read_root():
    return {"status": "success", "message": "Welcome to the DevOps Pipeline HD Project!"}

@app.get("/metrics")
def get_metrics():
    # Exposes a mock endpoint so monitoring tools can track usage and health
    return {
        "cpu_usage_percent": 45, 
        "memory_usage_mb": 120, 
        "status": "healthy",
        "timestamp": time.time()
    }

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from prometheus_fastapi_instrumentator import Instrumentator

# SQLite Database Setup
DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SIT753 DevOps CRUD API", version="1.0.0")

# Expose real Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app)

# Pydantic Schemas
class TaskCreate(BaseModel):
    title: str
    description: str = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str = None

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to SIT753 DevOps CRUD API with Real Prometheus Monitoring!"}

@app.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskDB(title=task.title, description=task.description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(TaskDB).all()

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": f"Task {task_id} deleted successfully"}

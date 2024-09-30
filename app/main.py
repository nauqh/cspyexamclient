from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .schemas import Exam, Submission, SubmissionResponse

# Database
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title='Submission API',
    summary="Client for learner submissions",
    version='0.0.2'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def root():
    return {"message": "Root endpoint"}


@app.post("/submission", status_code=status.HTTP_201_CREATED)
async def add_submission(data: Submission, db: Session = Depends(get_db)):
    submission = models.Submission(**data.model_dump())
    db.add(submission)
    db.commit()

    return f"Added submission for {submission.email}"


@app.get("/submission/{email}", response_model=SubmissionResponse)
async def get_assignment(email: str, db: Session = Depends(get_db)):
    assignment = db.query(models.Submission).filter(
        models.Submission.email == email).order_by(models.Submission.submitted_at.desc()).first()
    return assignment


@app.post("/exam", status_code=status.HTTP_201_CREATED)
async def add_assignment(data: Exam, db: Session = Depends(get_db)):
    exam = models.Exam(**data.model_dump())
    db.add(exam)
    db.commit()

    return f"Added new assignment: {exam.name}"


@app.get("/exam/{id}", response_model=Exam)
async def get_exam(id: str, db: Session = Depends(get_db)):
    exam = db.query(models.Exam).filter(models.Exam.id == id).first()
    return exam

from fastapi import FastAPI
from database import engine
from models import Base

app = FastAPI()

# create tables automatically
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "DevHive backend running"}
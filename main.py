from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "活動報名平台"}
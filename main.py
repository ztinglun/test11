from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles          # add
from routes import registrations_router              # add

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")  # add
app.include_router(registrations_router)             # add

@app.get("/")
def home():
    return {"message": "活動報名平台"}
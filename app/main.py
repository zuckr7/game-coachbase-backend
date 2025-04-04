from fastapi import FastAPI
import uvicorn
from routers import users, auth, progress

app = FastAPI(title="My Project API")

# Подключаем роутеры
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(progress.router)

@app.get("/")
def root():
    return {"message": "Server rabotaet"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
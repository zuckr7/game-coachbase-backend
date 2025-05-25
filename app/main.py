from fastapi import FastAPI
import uvicorn
from app.routers import users, auth, progress, levels, purchase
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Hamster Invasion")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hamster-invation.ru"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Подключаем роутеры
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(progress.router)
app.include_router(levels.router)
app.include_router(purchase.router)

@app.get("/")
def root():
    return {"message": "Server rabotaet"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
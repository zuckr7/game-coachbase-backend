from fastapi import FastAPI, HTTPException
from db import db
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Server rabotaet"}

# (INSERT)
@app.post("/users/")
def create_user(user_id: str, name: str, email: str):
    document = {
        "name": name,
        "email": email
    }
    db.insert(user_id, document)
    return {"message": "User created", "user": document}

# (SELECT)
@app.get("/users/{user_id}")
def get_user(user_id: str):
    try:
        user = db.get(user_id).content_as[dict]
        return {"user": user}
    except:
        return {"error": "User not found"}

# (DELETE)
@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    try:
        db.remove(user_id)
        return {"message": "User deleted"}
    except:
        return {"error": "User not found"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
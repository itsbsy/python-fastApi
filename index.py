print("hello World")
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/bye")
def read_root():
    return {"Bye": "World"}

@app.post("/items/")
def create_item(item_id: int, item_name: str):
    return {"item_id": item_id, "item_name": item_name}

@app.get("/items/{item_id}")
def read_item(item_id: int, query_param: str = None):
    return {"item_id": item_id, "query_param": query_param}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="Basic CRUD API", version="1.0.0")

# Pydantic models for request/response
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None

class Item(ItemBase):
    id: str
    
    class Config:
        from_attributes = True

# In-memory database
items_db = {}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Basic CRUD API"}

# CREATE - Add a new item
@app.post("/items/", response_model=Item)
def create_item(item: ItemCreate):
    item_id = str(uuid.uuid4())
    new_item = Item(id=item_id, **item.dict())
    items_db[item_id] = new_item
    return new_item

# READ - Get all items
@app.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100):
    items = list(items_db.values())
    return items[skip: skip + limit]

# READ - Get a specific item by ID
@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: str):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

# UPDATE - Update an existing item
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: str, item_update: ItemUpdate):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    stored_item = items_db[item_id]
    update_data = item_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(stored_item, field, value)
    
    items_db[item_id] = stored_item
    return stored_item

# DELETE - Remove an item
@app.delete("/items/{item_id}")
def delete_item(item_id: str):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    del items_db[item_id]
    return {"message": "Item deleted successfully"}

# Additional endpoints for better functionality
@app.get("/items/search/", response_model=List[Item])
def search_items(q: str):
    """Search items by name or description"""
    results = []
    for item in items_db.values():
        if (q.lower() in item.name.lower() or 
            (item.description and q.lower() in item.description.lower())):
            results.append(item)
    return results

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "total_items": len(items_db)
    }

# To run the server:
# pip install fastapi uvicorn
# uvicorn main:app --reload
#
# Then visit:
# - http://localhost:8000/docs for interactive API documentation
# - http://localhost:8000/redoc for alternative documentation
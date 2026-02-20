
from fastapi import FastAPI, HTTPException, Body  # type: ignore
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from bson import ObjectId # type: ignore
from typing import List, Dict, Any
import os

app = FastAPI()

# Configuração do Banco de Dados
MONGO_DETAILS = "mongodb://database:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client["seu_banco_dados"]


def helper(item) -> dict:
    item["id"] = str(item["_id"])
    del item["_id"]
    return item

@app.get("/{collection}", response_model=List[Dict[Any, Any]])
async def get_all(collection: str):
    cursor = db[collection].find()
    results = []
    async for document in cursor:
        results.append(helper(document))
    return results

@app.get("/{collection}/{id}")
async def get_one(collection: str, id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    document = await db[collection].find_one({"_id": ObjectId(id)})
    if document:
        return helper(document)
    raise HTTPException(status_code=404, detail="Não encontrado")

@app.post("/{collection}", status_code=201)
async def create_item(collection: str, data: dict = Body(...)):
    result = await db[collection].insert_one(data)
    new_item = await db[collection].find_one({"_id": result.inserted_id})
    return helper(new_item)

@app.put("/{collection}/{id}")
async def update_item(collection: str, id: str, data: dict = Body(...)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_result = await db[collection].update_one(
        {"_id": ObjectId(id)}, {"$set": data}
    )
    
    if update_result.modified_count == 1:
        updated_item = await db[collection].find_one({"_id": ObjectId(id)})
        return helper(updated_item)
    
    raise HTTPException(status_code=404, detail="Documento não alterado ou não encontrado")

@app.delete("/{collection}/{id}")
async def delete_item(collection: str, id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    delete_result = await db[collection].delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return {"message": "Deletado com sucesso"}
    
    raise HTTPException(status_code=404, detail="Não encontrado")
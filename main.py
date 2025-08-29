# main.py

from fastapi import FastAPI

# 1. Cria uma instância do FastAPI
app = FastAPI()

# Dados de exemplo (simulando um banco de dados)
db_items = {
    1: {"nome": "Comprar leite", "descricao": "Ir ao mercado e comprar leite integral.", "completo": False},
    2: {"nome": "Fazer tutorial de API", "descricao": "Escrever um guia completo sobre como criar APIs.", "completo": True},
    3: {"nome": "Ligar para o cliente", "descricao": "Confirmar a reunião de amanhã.", "completo": False},
}


# 2. Define o endpoint da raiz ("/") com o método GET
@app.get("/")
async def root():
    """
    Endpoint principal da API. Retorna uma mensagem de boas-vindas.
    """
    return {"message": "Olá! Bem-vindo à minha API de tarefas."}


# 3. Endpoint para listar todos os itens
@app.get("/items/")
async def listar_items():
    """
    Retorna todos os itens da nossa base de dados.
    """
    return db_items


# 4. Endpoint para buscar um item específico por ID
@app.get("/items/{item_id}")
async def buscar_item(item_id: int):
    """
    Busca um item pelo seu ID. O {item_id} na URL é passado como argumento.
    """
    if item_id not in db_items:
        return {"erro": "Item não encontrado"}
    return db_items[item_id]

# main.py (continuação)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ... (código anterior aqui) ...

# 5. Modelo de dados para validação com Pydantic
class Item(BaseModel):
    nome: str
    descricao: str | None = None # | None = None torna o campo opcional
    completo: bool

# 6. Endpoint para criar um novo item (POST)
@app.post("/items/")
async def criar_item(item: Item):
    """
    Cria um novo item. Os dados são recebidos no corpo (body) da requisição.
    O Pydantic garante que os dados recebidos têm o formato correto.
    """
    novo_id = max(db_items.keys() or [0]) + 1
    db_items[novo_id] = item.dict()
    return {"id": novo_id, **item.dict()}


# 7. Endpoint para atualizar um item (PUT)
@app.put("/items/{item_id}")
async def atualizar_item(item_id: int, item: Item):
    """
    Atualiza um item existente.
    """
    if item_id not in db_items:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    db_items[item_id] = item.dict()
    return {"id": item_id, **item.dict()}


# 8. Endpoint para deletar um item (DELETE)
@app.delete("/items/{item_id}")
async def deletar_item(item_id: int):
    """
    Deleta um item da base de dados.
    """
    if item_id not in db_items:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    del db_items[item_id]
    return {"message": "Item deletado com sucesso"}
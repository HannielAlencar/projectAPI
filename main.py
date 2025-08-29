# main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional

# --- MÓDULOS DA AUTOMAÇÃO (ainda como placeholders) ---
# No futuro, você substituirá o conteúdo dessas funções pelo código real
# do Selenium e do Pdfplumber que discutimos.

def baixar_e_processar_editais(ano: int, mes: str, estado: str) -> List[Dict]:
    """
    FUNÇÃO PLACEHOLDER: Simula o robô que baixa e lê os PDFs.
    Retorna uma lista de dicionários com os imóveis encontrados e filtrados.
    """
    print(f"--- SIMULANDO AUTOMAÇÃO PARA {mes}/{ano} de {estado} ---")
    # Estes são os dados que o seu robô (Módulos 2 e 3) extrairia
    dados_ficticios = [
        {"endereco": f"RUA EXEMPLO, 123, {estado}", "valor_1_leilao": 250000.0, "valor_2_leilao": 245000.0, "provisao": 5000.0, "origem_edital": f"edital_{mes}_{ano}_1.pdf"},
        {"endereco": f"AVENIDA TESTE, 456, {estado}", "valor_1_leilao": 500000.0, "valor_2_leilao": 490000.0, "provisao": 10000.0, "origem_edital": f"edital_{mes}_{ano}_2.pdf"},
        {"endereco": f"TRAVESSA MODELO, 789, {estado}", "valor_1_leilao": 150000.0, "valor_2_leilao": 144500.0, "provisao": 5500.0, "origem_edital": f"edital_{mes}_{ano}_3.pdf"}
    ]
    print("--- SIMULAÇÃO CONCLUÍDA ---")
    return dados_ficticios

# --- ESTRUTURA DA API ---

app = FastAPI(
    title="API de Automação de Cadastro de Imóveis",
    description="Gerencia o processo de busca e o armazenamento de imóveis de leilão da Caixa."
)

# Modelo Pydantic para o Imóvel
class Imovel(BaseModel):
    id: int
    endereco: str
    valor_1_leilao: float
    valor_2_leilao: float
    provisao: float
    origem_edital: str
    status: str = "novo" # Status para controlar o fluxo (ex: novo, cadastrado, ignorado)

# Modelo para atualização, permitindo alterar apenas o status
class ImovelUpdate(BaseModel):
    status: str

# "Banco de dados" em memória para armazenar os imóveis encontrados
db_imoveis: Dict[int, Imovel] = {}

# --- LÓGICA DA AUTOMAÇÃO EM SEGUNDO PLANO ---

def executar_logica_e_salvar(ano: int, mes: str, estado: str):
    """
    Função que executa a automação e salva os resultados no nosso "banco de dados".
    """
    imoveis_encontrados = baixar_e_processar_editais(ano, mes, estado)
    
    # Adiciona os imóveis encontrados ao nosso db
    for imovel_data in imoveis_encontrados:
        novo_id = max(db_imoveis.keys() or [0]) + 1
        novo_imovel = Imovel(id=novo_id, **imovel_data)
        db_imoveis[novo_id] = novo_imovel
        print(f"Imóvel ID {novo_id} adicionado: {novo_imovel.endereco}")

# --- ENDPOINTS DA API ---

@app.post("/automacao/executar", status_code=202)
def iniciar_automacao(ano: int, mes: str, estado: str, background_tasks: BackgroundTasks):
    """
    Inicia o processo de automação em segundo plano.
    Responde imediatamente com uma mensagem de sucesso.
    """
    background_tasks.add_task(executar_logica_e_salvar, ano, mes, estado)
    return {"message": "Processo de automação iniciado em segundo plano. Os resultados estarão disponíveis em breve no endpoint /imoveis/."}

@app.get("/imoveis/", response_model=List[Imovel])
def listar_imoveis(status: Optional[str] = None):
    """
    Lista todos os imóveis encontrados pela automação.
    Pode ser filtrado por status (ex: /imoveis/?status=novo).
    """
    if status:
        return [imovel for imovel in db_imoveis.values() if imovel.status == status]
    return list(db_imoveis.values())

@app.get("/imoveis/{imovel_id}", response_model=Imovel)
def buscar_imovel(imovel_id: int):
    """
    Busca um imóvel específico pelo seu ID.
    """
    if imovel_id not in db_imoveis:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    return db_imoveis[imovel_id]

@app.put("/imoveis/{imovel_id}", response_model=Imovel)
def atualizar_status_imovel(imovel_id: int, imovel_update: ImovelUpdate):
    """
    Atualiza o status de um imóvel (ex: para 'cadastrado').
    """
    if imovel_id not in db_imoveis:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    imovel_existente = db_imoveis[imovel_id]
    imovel_existente.status = imovel_update.status
    db_imoveis[imovel_id] = imovel_existente
    return imovel_existente

@app.delete("/imoveis/{imovel_id}")
def deletar_imovel(imovel_id: int):
    """
    Remove um imóvel da lista.
    """
    if imovel_id not in db_imoveis:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    del db_imoveis[imovel_id]
    return {"message": "Imóvel deletado com sucesso"}


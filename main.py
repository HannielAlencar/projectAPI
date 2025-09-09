# main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import scraper_caixa
import processador_pdf
import os

# --- MÓDULOS DA AUTOMAÇÃO (ainda como placeholders) ---
# No futuro, você substituirá o conteúdo dessas funções pelo código real
# do Selenium e do Pdfplumber que discutimos.

def baixar_e_processar_editais(ano: float, mes: str, estado: str) -> List[Dict]:
    """
    Executa o fluxo real de automação: baixa os editais e depois processa os PDFs.
    """
    # Define o nome da pasta onde os arquivos serão salvos e lidos.
    pasta_dos_editais = "editais_baixados"
    
    arquivos_ja_processados_path = os.path.join(pasta_dos_editais, "processados.txt")
    arquivos_ja_processados = set()
    if os.path.exists(arquivos_ja_processados_path):
        with open(arquivos_ja_processados_path, "r") as f:
            arquivos_ja_processados = set(f.read().splitlines())

    # 1. Chama o robô do scraper_caixa para baixar os arquivos
    print(f"Iniciando download dos editais para {mes}/{ano} de {estado}...")
    scraper_caixa.baixar_editais_por_mes(
        ano=ano,
        mes_texto=mes,
        estado_sigla=estado,
        pasta_download=pasta_dos_editais,
        arquivos_existentes=list(arquivos_ja_processados)
    )
    print("Download dos editais concluído.")

    # 2. Chama o processador_pdf para ler os arquivos baixados e filtrar os imóveis
    print("Iniciando processamento dos PDFs baixados...")
    imoveis_reais_filtrados = processador_pdf.processar_pdfs_e_filtrar(pasta_dos_editais, arquivos_ja_processados)
    print(f"Processamento concluído. {len(imoveis_reais_filtrados)} imóveis aprovados encontrados.")

    # Salva os novos arquivos processados
    if imoveis_reais_filtrados:
        novos_arquivos_processados = {imovel["origem_edital"] for imovel in imoveis_reais_filtrados}
        with open(arquivos_ja_processados_path, "a") as f:
            for arquivo in novos_arquivos_processados:
                f.write(f"{arquivo}\n")

    # 3. Retorna os dados reais que foram extraídos
    return imoveis_reais_filtrados

# --- ESTRUTURA DA API ---

app = FastAPI(
    title="API de Automação de Cadastro de Imóveis",
    description="Gerencia o processo de busca e o armazenamento de imóveis de leilão da Caixa."
)

# Modelo Pydantic para o Imóvel
class Imovel(BaseModel):
    id: int
    endereco: str
    matricula: Optional[str] = None # Adicionamos o campo de matricula
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
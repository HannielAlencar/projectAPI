# executar_automacao.py (VERSÃO FINAL)

from datetime import date, datetime
import scraper_caixa
import processador_pdf
from pprint import pprint
import os # Importamos o módulo 'os'

# ===================================================================
# ---               PAINEL DE CONTROLE DA AUTOMAÇÃO               ---
# ===================================================================
DATA_INICIO_BUSCA = date.today()
ESTADOS_PARA_BUSCAR = ["SP"] # Adicione os estados que desejar
PASTA_DOWNLOADS = "editais_baixados"
# ===================================================================

def gerar_meses_anos(data_inicio):
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    data_atual = datetime.now()
    ano_atual, mes_atual = data_atual.year, data_atual.month
    ano, mes = data_inicio.year, data_inicio.month
    
    while ano < ano_atual or (ano == ano_atual and mes <= mes_atual):
        yield (ano, meses[mes-1])
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1

if __name__ == "__main__":
    print("="*50)
    print(f"INICIANDO BUSCA AUTOMÁTICA POR EDITAIS")
    print(f"Data de início da busca: {DATA_INICIO_BUSCA.strftime('%d/%m/%Y')}")
    print("="*50)
    
    # Lista de arquivos para verificar se já foram processados
    arquivos_ja_processados_path = os.path.join(PASTA_DOWNLOADS, "processados.txt")
    arquivos_ja_processados = set()
    if os.path.exists(arquivos_ja_processados_path):
        with open(arquivos_ja_processados_path, "r") as f:
            arquivos_ja_processados = set(f.read().splitlines())

    # Etapa 1: O Gerente manda o Coletor buscar os arquivos mês a mês
    for estado in ESTADOS_PARA_BUSCAR:
        for ano, mes in gerar_meses_anos(DATA_INICIO_BUSCA):
            scraper_caixa.baixar_editais_por_mes(
                ano=ano,
                mes_texto=mes,
                estado_sigla=estado,
                pasta_download=PASTA_DOWNLOADS,
                arquivos_existentes=list(arquivos_ja_processados) # Passa os arquivos já processados para o scraper
            )

    # Etapa 2: O Gerente manda o Analista processar o que foi coletado
    imoveis_novos_encontrados = processador_pdf.processar_pdfs_e_filtrar(PASTA_DOWNLOADS, arquivos_ja_processados)
    
    # Salva os novos arquivos processados
    if imoveis_novos_encontrados:
      # Obtém o nome do arquivo de origem de cada imóvel e o armazena no conjunto
      novos_arquivos_processados = {imovel["origem_edital"] for imovel in imoveis_novos_encontrados}
      with open(arquivos_ja_processados_path, "a") as f:
        for arquivo in novos_arquivos_processados:
          f.write(f"{arquivo}\n")

    if imoveis_novos_encontrados:
        print("\n--- NOVOS IMÓVEIS APROVADOS ENCONTRADOS NESTA BUSCA ---")
        pprint(imoveis_novos_encontrados)
    else:
        print("\n--- NENHUM NOVO IMÓVEL APROVADO FOI ENCONTRADO. ---")

    print("\n" + "="*50)
    print("BUSCA AUTOMÁTICA FINALIZADA.")
    print("="*50)
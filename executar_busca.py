# executar_automacao.py

from datetime import date
import scraper_caixa
import processador_pdf
from pprint import pprint

# ===================================================================
# ---               PAINEL DE CONTROLE DA AUTOMAÇÃO               ---
# ===================================================================

# DEFINA AQUI A DATA A PARTIR DA QUAL VOCÊ QUER OS EDITAIS
# Formato: (Ano, Mês, Dia)
DATA_INICIO_BUSCA = date(2025, 9, 16)

# DEFINA AQUI A LISTA DE ESTADOS QUE O ROBÔ DEVE PESQUISAR
ESTADOS_PARA_BUSCAR = ["SP", "RJ", "MG", "BA", "SC", "RS", "PE", "CE"] # Adicione ou remova estados

# NOME DA PASTA PARA SALVAR OS PDFS
PASTA_DOWNLOADS = "editais_baixados"

# ===================================================================

if __name__ == "__main__":
    print("="*50)
    print(f"INICIANDO BUSCA AUTOMÁTICA POR EDITAIS")
    print(f"Data de início da busca: {DATA_INICIO_BUSCA.strftime('%d/%m/%Y')}")
    print(f"Estados a serem pesquisados: {', '.join(ESTADOS_PARA_BUSCAR)}")
    print("="*50)
    
    # 1. Chama o scraper inteligente para baixar apenas os arquivos novos
    scraper_caixa.baixar_editais_a_partir_de(
        data_inicio=DATA_INICIO_BUSCA,
        estados=ESTADOS_PARA_BUSCAR,
        pasta_download=PASTA_DOWNLOADS
    )
    
    # 2. Chama o processador para ler os arquivos que foram baixados
    imoveis_encontrados = processador_pdf.processar_pdfs_e_filtrar(PASTA_DOWNLOADS)

    if imoveis_encontrados:
        print("\n--- IMÓVEIS APROVADOS ENCONTRADOS NESTA BUSCA ---")
        pprint(imoveis_encontrados)
        # LÓGICA FUTURA: Aqui você pode adicionar o código para salvar
        # estes dados em um banco de dados ou enviar para o seu sistema.
    else:
        print("\n--- NENHUM IMÓVEL APROVADO FOI ENCONTRADO NOS NOVOS EDITAIS. ---")

    print("\n" + "="*50)
    print("BUSCA AUTOMÁTICA FINALIZADA.")
    print("="*50)
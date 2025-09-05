# executar_automacao.py (VERSÃO FINAL)

from datetime import date, datetime
import scraper_caixa
import processador_pdf
from pprint import pprint

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

    # Etapa 1: O Gerente manda o Coletor buscar os arquivos mês a mês
    for estado in ESTADOS_PARA_BUSCAR:
        for ano, mes in gerar_meses_anos(DATA_INICIO_BUSCA):
            scraper_caixa.baixar_editais_por_mes(
                ano=ano,
                mes_texto=mes,
                estado_sigla=estado,
                pasta_download=PASTA_DOWNLOADS
            )

    # Etapa 2: O Gerente manda o Analista processar o que foi coletado
    imoveis_novos_encontrados = processador_pdf.processar_pdfs_e_filtrar(PASTA_DOWNLOADS)

    if imoveis_novos_encontrados:
        print("\n--- NOVOS IMÓVEIS APROVADOS ENCONTRADOS NESTA BUSCA ---")
        pprint(imoveis_novos_encontrados)
    else:
        print("\n--- NENHUM NOVO IMÓVEL APROVADO FOI ENCONTRADO. ---")

    print("\n" + "="*50)
    print("BUSCA AUTOMÁTICA FINALIZADA.")
    print("="*50)
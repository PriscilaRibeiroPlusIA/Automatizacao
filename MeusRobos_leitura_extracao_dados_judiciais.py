# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1lsV5RX1Gcunz8a9GJwvsgO3tY1-RqNc9
"""

# Célula 1: Conectar ao Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Célula 2: Instalar a biblioteca PyPDF2
!pip install PyPDF2

# Célula 3: Definir o caminho da pasta dos PDFs
import os # Biblioteca para interagir com o sistema de arquivos (pastas e arquivos)

# !!!!! MUITO IMPORTANTE !!!!!
# Substitua o texto abaixo pelo caminho correto da sua pasta de PDFs no Google Drive.
# Exemplo: '/content/drive/MyDrive/Pdfs'
pasta_dos_pdfs = "/content/drive/MyDrive/Pdfs" # <<< SUBSTITUA AQUI

# Vamos verificar se a pasta existe para evitar erros
if not os.path.exists(pasta_dos_pdfs):
    print(f"Atenção! A pasta '{pasta_dos_pdfs}' não foi encontrada. Verifique o caminho e tente novamente.")
    print("Certifique-se de que o Google Drive está montado e o caminho está correto.")
else:
    print(f"Ok! A pasta de PDFs foi configurada como: {pasta_dos_pdfs}")

# A pasta onde os resumos serão salvos será a mesma
pasta_dos_resumos = pasta_dos_pdfs

# Célula 4: Agente 1 - Função para ler textos de arquivos PDF
import PyPDF2 # A biblioteca que instalamos para ler PDFs

def agente_leitor_de_pdfs(caminho_da_pasta_com_pdfs):
    """
    Esta função (nosso "agente leitor") vai até a pasta especificada,
    encontra todos os arquivos PDF e tenta ler o texto de cada um.
    """
    print(f"\n--- Agente Leitor Ativado: Buscando PDFs em '{caminho_da_pasta_com_pdfs}' ---")
    documentos_lidos = [] # Uma lista vazia para guardar o nome e o texto de cada PDF

    # Vamos olhar cada item dentro da pasta
    for nome_do_arquivo in os.listdir(caminho_da_pasta_com_pdfs):
        # Verificamos se o arquivo termina com ".pdf" (ignorando se é PDF ou pdf)
        if nome_do_arquivo.lower().endswith(".pdf"):
            print(f"Encontrei um PDF: {nome_do_arquivo}")
            caminho_completo_do_arquivo = os.path.join(caminho_da_pasta_com_pdfs, nome_do_arquivo)

            try:
                texto_do_pdf = ""
                # Abrimos o arquivo PDF em modo de leitura binária ('rb')
                with open(caminho_completo_do_arquivo, 'rb') as arquivo_pdf:
                    # Criamos um objeto "leitor de PDF"
                    leitor = PyPDF2.PdfReader(arquivo_pdf)
                    # Vamos passar por cada página do PDF
                    for numero_pagina in range(len(leitor.pages)):
                        pagina = leitor.pages[numero_pagina]
                        texto_do_pdf += pagina.extract_text() # Extrai o texto da página

                if texto_do_pdf: # Se conseguimos ler algum texto
                    documentos_lidos.append({
                        "nome_arquivo": nome_do_arquivo,
                        "conteudo_texto": texto_do_pdf
                    })
                    print(f"  Texto extraído de '{nome_do_arquivo}' com sucesso!")
                else:
                    print(f"  Aviso: Não consegui extrair texto do '{nome_do_arquivo}' (pode estar vazio ou ser uma imagem).")

            except Exception as e:
                # Se der algum erro ao tentar ler o PDF
                print(f"  Ops! Ocorreu um erro ao tentar ler o arquivo '{nome_do_arquivo}': {e}")

    if not documentos_lidos:
        print("Nenhum texto de PDF foi extraído. Verifique se há PDFs na pasta ou se eles contêm texto selecionável.")
    else:
        print(f"--- Agente Leitor Concluído: {len(documentos_lidos)} PDF(s) processados. ---")
    return documentos_lidos

# Para testar (opcional, vamos rodar tudo junto no final):
# lista_de_textos_dos_pdfs = agente_leitor_de_pdfs(pasta_dos_pdfs)
# print(f"\nEncontrei {len(lista_de_textos_dos_pdfs)} PDFs com texto.")

# Célula 5: Agente 2 - Função para extrair informações do texto
import re # Biblioteca para "Expressões Regulares" (busca avançada de texto)

def agente_extrator_de_informacoes(texto_do_documento):
    """
    Este "agente extrator" recebe o texto de um documento e tenta
    encontrar nome, CPF, endereço do autor e a decisão/sentença/acórdão.
    """
    # print("\n--- Agente Extrator Ativado: Analisando texto... ---")
    informacoes = {
        "nome_autor": "Não encontrado",
        "cpf_autor": "Não encontrado",
        "endereco_autor": "Não encontrado",
        "tipo_decisao": "Não especificado", # Para "Decisão", "Sentença" ou "Acórdão"
        "resumo_decisao": "Não encontrado"
    }

    # Tentar encontrar NOME DO AUTOR
    # Procuramos por "Autor(a):", "Requerente:", "Parte Autora:" seguido de um nome.
    # [A-Za-zÀ-ú\s]+ significa "uma ou mais letras (maiúsculas, minúsculas, com acento) e espaços"
    # O '?' depois de \s* faz a busca ser "não gulosa", parando no primeiro \n (nova linha) ou CPF
    match_nome = re.search(r"(?:Autor\(a\)|Requerente|Parte Autora|Exequente)\s*:\s*([A-Za-zÀ-ú\s]+?)(?:\n|CPF)", texto_do_documento, re.IGNORECASE)
    if match_nome:
        informacoes["nome_autor"] = match_nome.group(1).strip() # .group(1) pega o que está nos parênteses () da regex

    # Tentar encontrar CPF DO AUTOR
    # Procuramos por "CPF:" seguido de números no formato XXX.XXX.XXX-XX ou XXXXXXXXXXX
    match_cpf = re.search(r"CPF\s*(?:nº|:)?\s*(\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})", texto_do_documento, re.IGNORECASE)
    if match_cpf:
        informacoes["cpf_autor"] = match_cpf.group(1).strip()

    # Tentar encontrar ENDEREÇO DO AUTOR
    # Esta é a parte mais difícil, pois endereços variam muito.
    # Procuramos por "Endereço:" seguido de qualquer texto até uma nova linha ou palavras como CEP, Cidade.
    # re.DOTALL faz o '.' na regex também pegar quebras de linha, mas limitamos a busca.
    # Esta regex é um EXEMPLO e provavelmente precisará de ajustes!
    match_endereco = re.search(r"(?:Endereço|ENDEREÇO)\s*:\s*(.+?)(?:\n\s*(?:CEP|Cidade|Bairro|Estado)|Processo Nº|CITADO\(A\))", texto_do_documento, re.IGNORECASE | re.DOTALL)
    if match_endereco:
        # Remove quebras de linha excessivas do endereço
        endereco_limpo = re.sub(r'\s*\n\s*', ' ', match_endereco.group(1).strip())
        informacoes["endereco_autor"] = endereco_limpo
    else: # Tentativa mais simples se a primeira falhar
        match_endereco_simples = re.search(r"residente\s+e\s+domiciliado(?:a)?\s+à\s+(.+?)(?:,|\.|CEP|nº)", texto_do_documento, re.IGNORECASE | re.DOTALL)
        if match_endereco_simples:
            endereco_limpo = re.sub(r'\s*\n\s*', ' ', match_endereco_simples.group(1).strip())
            informacoes["endereco_autor"] = endereco_limpo


    # Tentar encontrar TIPO DE DECISÃO e um RESUMO
    texto_lower = texto_do_documento.lower() # Para facilitar a busca por palavras-chave
    palavras_chave_decisao = ["decisão", "sentença", "acórdão"]
    indice_inicio_decisao = -1

    for palavra in palavras_chave_decisao:
        # Procuramos a palavra cercada por espaços ou no início/fim de uma frase, para evitar falsos positivos
        # como "decisãoprocessual"
        match_palavra_chave = re.search(r"\b" + palavra + r"\b", texto_lower)
        if match_palavra_chave:
            informacoes["tipo_decisao"] = palavra.capitalize()
            indice_inicio_decisao = match_palavra_chave.start() # Onde a palavra foi encontrada
            break # Para na primeira que encontrar (Decisão, depois Sentença, depois Acórdão)

    if indice_inicio_decisao != -1:
        # Pega um trecho do texto começando da palavra-chave encontrada.
        # O "resumo" aqui será os próximos 1000 caracteres após a palavra-chave.
        # Isso é uma simplificação! Um resumo de verdade é mais complexo.
        texto_apos_palavra_chave = texto_do_documento[indice_inicio_decisao:]

        # Tenta encontrar frases comuns de julgamento para um "resumo" mais focado
        # (JULGO PROCEDENTE..., CONDENO..., NEGO PROVIMENTO..., etc.)
        # (?:.|\n) significa "qualquer caractere OU uma nova linha"
        match_julgamento = re.search(r"(JULGO\s+(?:PARCIALMENTE\s+)?PROCEDENTE|JULGO\s+IMPROCEDENTE|NEGO\s+PROVIMENTO|DOU\s+(?:PARCIAL\s+)?PROVIMENTO|CONDENO|ABSOLVO|DECRETO|MANTENHO\s+A\s+SENTENÇA|REFORMO\s+A\s+SENTENÇA)(?:.|\n){0,500}", texto_apos_palavra_chave, re.IGNORECASE | re.DOTALL)
        if match_julgamento:
            # Pega até 500 caracteres do trecho do julgamento.
            resumo_bruto = match_julgamento.group(0).strip()
            informacoes["resumo_decisao"] = re.sub(r'\s+', ' ', resumo_bruto[:500]) + "..." # Limpa espaços extras
        else:
            # Se não achar frases de julgamento, pega um trecho genérico
            resumo_bruto = texto_apos_palavra_chave[:1000].strip()
            informacoes["resumo_decisao"] = re.sub(r'\s+', ' ', resumo_bruto) + "..." # Limpa espaços extras
    else:
        informacoes["resumo_decisao"] = "Palavra-chave (Decisão/Sentença/Acórdão) não encontrada no texto ou texto subsequente não capturado."

    # print("--- Agente Extrator Concluído. ---")
    return informacoes

# Para testar (opcional):
# if lista_de_textos_dos_pdfs: # Se a lista não estiver vazia
#     texto_exemplo = lista_de_textos_dos_pdfs[0]["conteudo_texto"] # Pega o texto do primeiro PDF
#     infos_exemplo = agente_extrator_de_informacoes(texto_exemplo)
#     print("\nInformações extraídas do primeiro PDF (exemplo):")
#     for chave, valor in infos_exemplo.items():
#         print(f"  {chave}: {valor[:100]}...") # Mostra só os primeiros 100 caracteres

# Célula 6: Agente 3 - Função para salvar os dados extraídos em um arquivo de texto
def agente_arquivista(dados_para_salvar, nome_do_pdf_original, caminho_da_pasta_para_salvar):
    """
    Este "agente arquivista" pega os dados extraídos e os salva
    em um arquivo .txt na pasta especificada.
    O nome do arquivo de resumo será baseado no nome do PDF original.
    """
    # print(f"\n--- Agente Arquivista Ativado: Preparando para salvar resumo de '{nome_do_pdf_original}' ---")
    # Cria um nome para o arquivo de resumo. Ex: se o PDF é "processo123.pdf", o resumo será "resumo_processo123.txt"
    nome_arquivo_resumo = "RESUMO_" + nome_do_pdf_original.replace(".pdf", ".txt").replace(".PDF", ".txt")
    caminho_completo_do_resumo = os.path.join(caminho_da_pasta_para_salvar, nome_arquivo_resumo)

    try:
        # Abre (ou cria se não existir) o arquivo de resumo em modo de escrita ('w')
        # encoding='utf-8' ajuda com acentos e caracteres especiais
        with open(caminho_completo_do_resumo, 'w', encoding='utf-8') as arquivo_saida:
            arquivo_saida.write(f"Arquivo Original: {nome_do_pdf_original}\n")
            arquivo_saida.write("=" * 40 + "\n") # Uma linha separadora
            arquivo_saida.write(f"Nome do Autor: {dados_para_salvar['nome_autor']}\n")
            arquivo_saida.write(f"CPF do Autor: {dados_para_salvar['cpf_autor']}\n")
            arquivo_saida.write(f"Endereço do Autor: {dados_para_salvar['endereco_autor']}\n")
            arquivo_saida.write("-" * 40 + "\n") # Outra linha separadora
            arquivo_saida.write(f"Tipo de Decisão/Documento: {dados_para_salvar['tipo_decisao']}\n")
            arquivo_saida.write(f"Conteúdo Principal da Decisão/Sentença/Acórdão:\n{dados_para_salvar['resumo_decisao']}\n")

        print(f"  Sucesso! Resumo salvo em: {caminho_completo_do_resumo}")
    except Exception as e:
        print(f"  Ops! Ocorreu um erro ao tentar salvar o resumo '{nome_arquivo_resumo}': {e}")

# Para testar (opcional):
# if lista_de_textos_dos_pdfs and infos_exemplo: # Se tivermos dados de exemplo
#     agente_arquivista(infos_exemplo, lista_de_textos_dos_pdfs[0]["nome_arquivo"], pasta_dos_resumos)

# Célula 7: Executando o projeto completo - Orquestrando os agentes

print("=======================================================")
print("🤖 INICIANDO PROJETO DE EXTRAÇÃO DE INFORMAÇÕES JUDICIAIS 🤖")
print("=======================================================")

# Verifica se a pasta dos PDFs foi configurada corretamente (da Célula 3)
if 'pasta_dos_pdfs' not in globals() or not os.path.exists(pasta_dos_pdfs):
    print("\n❌ ERRO: A variável 'pasta_dos_pdfs' não foi definida ou a pasta não existe.")
    print("Por favor, execute a Célula 3 (Definir o caminho da pasta dos PDFs) corretamente.")
    print("Certifique-se de que o Google Drive está montado e o caminho está correto.")
else:
    print(f"\n🔎 Usando a pasta de PDFs: {pasta_dos_pdfs}")
    print(f"📝 Os resumos serão salvos em: {pasta_dos_resumos}")

    # ---- AGENTE 1: LER OS PDFs ----
    # Chamamos a função que definimos na Célula 4
    lista_documentos_com_texto = agente_leitor_de_pdfs(pasta_dos_pdfs)

    if not lista_documentos_com_texto:
        print("\n⚠️ Nenhum documento PDF foi lido ou nenhum texto pôde ser extraído. O programa não pode continuar.")
    else:
        print(f"\n👍 Agente Leitor finalizou. Total de {len(lista_documentos_com_texto)} documento(s) com texto para analisar.")
        print("-------------------------------------------------------")

        contador_sucessos = 0
        # Vamos passar por cada documento que o Agente 1 leu
        for i, documento_atual in enumerate(lista_documentos_com_texto):
            nome_arquivo = documento_atual["nome_arquivo"]
            texto_completo = documento_atual["conteudo_texto"]

            print(f"\n📄 Processando documento {i+1}/{len(lista_documentos_com_texto)}: {nome_arquivo}")

            # ---- AGENTE 2: EXTRAIR INFORMAÇÕES ----
            # Chamamos a função que definimos na Célula 5
            print("   🧠 Agente Extrator iniciando...")
            informacoes_extraidas = agente_extrator_de_informacoes(texto_completo)

            # Mostra um resumo do que foi encontrado (ou não)
            print("      Informações encontradas (prévia):")
            for chave, valor in informacoes_extraidas.items():
                valor_prev = str(valor)
                if len(valor_prev) > 70: # Se o valor for muito longo, mostra só o começo
                    valor_prev = valor_prev[:70] + "..."
                print(f"         - {chave.replace('_', ' ').capitalize()}: {valor_prev}")


            # ---- AGENTE 3: SALVAR AS INFORMAÇÕES ----
            # Chamamos a função que definimos na Célula 6
            print("   💾 Agente Arquivista iniciando...")
            agente_arquivista(informacoes_extraidas, nome_arquivo, pasta_dos_resumos)
            contador_sucessos +=1
            print("-------------------------------------------------------")

        print(f"\n🎉 Processamento Concluído! 🎉")
        if contador_sucessos > 0:
            print(f"Foram processados e salvos resumos para {contador_sucessos} documento(s).")
            print(f"Verifique a pasta '{pasta_dos_resumos}' no seu Google Drive pelos arquivos 'RESUMO_...'")
        else:
            print("Nenhum resumo foi gerado. Verifique as mensagens anteriores para possíveis avisos ou erros.")

print("\n=======================================================")
print("🤖 FIM DO PROJETO 🤖")
print("=======================================================")
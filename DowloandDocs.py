import json
import datetime
import os
import logging
import requests
import traceback
from dotenv import load_dotenv

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO, filename='ex.log')


# Cria diretorio na maquina local
def CriarDiretorio():
    caminho = r'C:\Contratos'

    try:
        os.makedirs(caminho)
        logging.info("Diretório criado!")

    except FileExistsError:
        logging.debug("O diretório já existe!")

    except PermissionError as e:
        logging.error(f"Erro ao criar o diretório: {str(e)}")
        traceback.print_exc()

    except Exception as e:
        logging.error(f"Erro desconhecido: {str(e)}")
        traceback.print_exc()

# Busca lista de todos os docs
def BuscaDocsParaDowloand(PagAtual):

    query_params = {'access_token': f'{token}','page': PagAtual}

    try:
        api_response = requests.get(
            'https://app.clicksign.com/api/v1/documents?', params=query_params)
        response = api_response
        if response.status_code != 200:
            logging.error(
                f"A requisição falhou. Código de status: {response.status_code}")
            return {}

        data = response.text
        return json.loads(data)

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao realizar a requisição: {str(e)}")
        traceback.print_exc()
        return {}

    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar os dados JSON: {str(e)}")
        traceback.print_exc()
        return {}

    except Exception as e:
        logging.error(f"Erro desconhecido: {str(e)}")
        traceback.print_exc()
        return {}

# Realiza dowload dos docs pelo id copturado
def RealizaDowloadDocs(key):

    api_response = f"https://app.clicksign.com/api/v1/documents/{key}?access_token={token}"

    try:
        response = requests.get(api_response, verify=False)
        response.raise_for_status()

        data = response.text
        parse_json = json.loads(data)

        fileName = f'C:/Contratos/{key}.pdf'

        urlzip = parse_json['document']['downloads']['signed_file_url']
        r = requests.get(url=urlzip, stream=True)
        r.raise_for_status()

        if r.status_code == 200:
            with open(fileName, 'wb') as f:
                r.raw.decode_content = True
                f.write(r.content)

        return fileName

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao realizar a requisição: {str(e)}")
        traceback.print_exc()
        return {}

    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar os dados JSON: {str(e)}")
        traceback.print_exc()
        return {}

    except Exception as e:
        logging.error(f"Erro desconhecido: {str(e)}")
        traceback.print_exc()
        return {}

load_dotenv() # Carregar variáveis de ambiente do arquivo .env
token =  os.getenv('token')
nPaginas = 999
PagAtual = 1
lContinua = True
today = datetime.date.today()

while nPaginas > PagAtual:
    listaDocs = BuscaDocsParaDowloand(PagAtual)

    docs = listaDocs['documents']

    if docs is None or len(docs) <= 0:
        logging.info("Não encontramos nenhum documento na lista para dowload")
        lContinua = False
        exit
    else:   
        for doc in docs:
            if doc['status'] == 'closed' and datetime.datetime.strptime(doc['finished_at'], '%Y-%m-%dT%H:%M:%S.%f%z').date() == today and doc['folder_id'] == 7091526: RealizaDowloadDocs(doc['key'])

    if nPaginas > PagAtual:
        PagAtual += 1
    else:
        lContinua = False

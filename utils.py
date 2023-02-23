import requests

def remover_acentos(name):
    
    acento_letra = {
        'ç' : 'c',
        'á' : 'a',
        'â' : 'a',
        'à' : 'a',
        'ã' : 'a',
        'ä' : 'a',
        'é' : 'e',
        'ê' : 'e',
        'è' : 'e',
        'ë' : 'e',
        'í' : 'i',
        'î' : 'i',
        'ì' : 'i',
        'ï' : 'i',
        'ó' : 'o',
        'ô' : 'o',
        'ò' : 'o',
        'ø' : 'o',
        'õ' : 'o',
        'ö' : 'o',
        'ú' : 'u',
        'û' : 'u',
        'ù' : 'u',
        'ü' : 'u',
        'ñ' : 'n',
        'ý' : 'y'
    }
    
    chars = list(name)
    
    return ''.join([acento_letra.get(char, char) for char in chars])

def padronizar_nom_regiao(nom_regiao:str)->str:

    nom_regiao_limpo = remover_acentos(nom_regiao)
    nom_regiao_upper = nom_regiao_limpo.upper()

    return nom_regiao_upper

def limpar_nomes_regiao(dados_regionais:dict)->dict:

    limpos = {}
    for nom_regiao, valores in dados_regionais.items():
        nom_regiao_padrao = padronizar_nom_regiao(nom_regiao)

        limpos[nom_regiao_padrao] = valores
    
    return limpos


def get_camada_geosampa(camada:str):

    DOMAIN = 'http://wfs.geosampa.prefeitura.sp.gov.br/geoserver/ows/'
    endpoint = (
            '?service=WFS&version=1.0.0'
            '&request=GetFeature'
            '&outputFormat=application/json'
            '&exceptions=application/json'
            '&typeName={camada}'
    )

    url = DOMAIN + endpoint.format(camada=camada)

    with requests.get(url) as r:
        return r.json()
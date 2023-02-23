import requests
import pandas as pd
import geopandas as gpd
import streamlit as st
import pydeck as pdk
import json
import matplotlib.pyplot as plt
from utils import limpar_nomes_regiao, get_camada_geosampa

DOMAIN = 'https://api.observasampa.prefeitura.sp.gov.br/'
COD_INDICADOR=27
NIVEIS_REGIONAIS = ['Distrito', 'Subprefeitura', 'Município']

@st.cache_data
def get_data(cod_indicador:int)->dict:
    
    endpoint = 'v1/front_end/ficha_indicador/{cod_indicador}'
    
    url = DOMAIN + endpoint.format(cod_indicador=cod_indicador)
    
    with requests.get(url) as r:
        return r.json()

@st.cache_data
def get_lst_indicadores()->dict:

    endpoint = 'v1/basic/indicadores/'

    url = DOMAIN + endpoint

    with requests.get(url) as r:
        return r.json()

@st.cache_data
def resultados_regiao(dados:dict, nivel_regional:str, as_df:bool=False)->pd.DataFrame:
    
    if nivel_regional not in NIVEIS_REGIONAIS:
        raise ValueError(f'{nivel_regional} not in {NIVEIS_REGIONAIS}')
    
    results = dados['resultados'][nivel_regional]

    results_limpos = limpar_nomes_regiao(results)

    if as_df:
        return pd.DataFrame(results_limpos)
    
    return results_limpos


@st.cache_data
def join_geojson_and_resultados(dados:dict, nivel_regional:str, ano:int)->dict:

    niveis = {'Distrito', 'Subprefeitura'}
    if nivel_regional not in niveis:
        raise ValueError(f'{nivel_regional} not in {niveis}')

    resultados_limpos = resultados_regiao(dados, nivel_regional)

    if nivel_regional == 'Distrito':
        geojson = get_camada_geosampa('geoportal:distrito_municipal')
        nm_regiao = 'nm_distrito_municipal'
    else:
        geojson = get_camada_geosampa('geoportal:subprefeitura')
        nm_regiao = 'nm_subprefeitura'

    for feature in geojson['features']:
        nom_regiao = feature['properties'][nm_regiao]

        feature['properties']['resultados'] = resultados_limpos.get(nom_regiao, {}).get(ano, None)

    return gpd.read_file(json.dumps(geojson))


@st.cache_resource
def grafico_linha(df:pd.DataFrame, filtro_regiao:list)->None:

    df = df[filtro_regiao]
    st.line_chart(df)

#@st.cache_resource
def mapa(_geojson:dict):
    fig, ax = plt.subplots()
    ax.axis('off')
    _geojson.plot(ax=ax, column='resultados', cmap='Blues', legend=True)
    st.pyplot(fig, transparent=False)



st.title('Dashboard ObservaSampa')
st.header('Oficina Residentes - fev/2023')

indicadores = get_lst_indicadores()
indicador = st.selectbox('Escolha o indicador', indicadores, format_func=lambda x: x['nm_indicador'])
dados = get_data(indicador['cd_indicador'])

with st.sidebar:
    markdown_txt = f"""
        ### {dados['nm_indicador']}
        #### Descrição: 
        *{dados['nm_completo_indicador']}*
        """
    st.markdown(markdown_txt)
    col1, col2 = st.columns(2)
    with col1:
        markdown_txt = f"""
        #### Fórmula de cálculo:
        {dados['dc_formula_indicador']}
        """
        st.markdown(markdown_txt)
    with col2:
        
        markdown_txt = f"""
        #### Fonte:
        {dados['tx_fonte_indicador']}
        """
        st.markdown(markdown_txt)
    
    st.image('https://www.prefeitura.sp.gov.br/cidade/secretarias/upload/chamadas/governo_horizontal_fundo_claro-compressed_1665689301.png')

nivel = st.selectbox('Nível regional', NIVEIS_REGIONAIS, index=2)


try:
    df_results = resultados_regiao(dados, nivel, as_df=True)
except KeyError:
    st.warning(f"O indicador {indicador['nm_indicador']} não possui dados para o nível {nivel}")
    st.stop()


tab1, tab2 = st.tabs(['Série temporal', 'Mapa'])

with tab1:
    regioes = st.multiselect('Escolha as regiões', df_results.columns, df_results.columns[0])
    grafico_linha(df_results, regioes)


with tab2:
    if nivel != "Município":
        anos = sorted(set(key for reg in dados['resultados'][nivel].values() for key in reg.keys()))
        ano = st.select_slider('Escolha o ano', anos)
        geojson = join_geojson_and_resultados(dados, nivel, ano)
        mapa(geojson)
    else:
        st.warning('Dados espacializados não disponíveis para este indicador.')




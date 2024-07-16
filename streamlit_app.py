import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import requests
import json

st.title("GeoInt 🌎 Map Choropleth")
st.markdown(
    """
    Essa é uma solução desenvolvida em python para criar uma visualização simple e explorável de um mapa clorópletico.
    
    Mapas coroplético representa normalmente uma superfície estatística por meio de áreas simbolizadas com cores, sombreamentos ou padrões de acordo com uma escala que representa a proporcionalidade da variável estatística em causa."
    """
)

# Função principal do Streamlit
def main():
    st.title("Mapas Coropléticos de Consultores e Distribuidores")

    # Carregar o arquivo Excel
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type="xlsx")
    
    if uploaded_file is not None:
        # Ler o arquivo Excel
        df = pd.read_excel(uploaded_file)

        # Exibir os dados carregados com visualização gráfica
        show_insights(df)
        
        # Criar os mapas coropléticos
        create_choropleth_maps(df)

def show_insights(df):
    st.write("Quantidade de Municípios Atendidos por Consultor e Distribuidor")

    # Contar a quantidade de municípios por consultor
    consultor_counts = df['CONSULTOR'].value_counts().reset_index()
    consultor_counts.columns = ['CONSULTOR', 'Quantidade']

    # Gráfico de barras para consultores
    fig_consultor = px.bar(consultor_counts, x='CONSULTOR', y='Quantidade', title='Quantidade de Municípios por Consultor',
                           color='CONSULTOR', color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig_consultor)

    # Contar a quantidade de municípios por distribuidor
    distribuidor_counts = df['DISTRIBUIDOR'].value_counts().reset_index()
    distribuidor_counts.columns = ['DISTRIBUIDOR', 'Quantidade']

    # Gráfico de barras para distribuidores
    fig_distribuidor = px.bar(distribuidor_counts, x='DISTRIBUIDOR', y='Quantidade', title='Quantidade de Municípios por Distribuidor',
                              color='DISTRIBUIDOR', color_discrete_sequence=px.colors.sequential.Reds)
    st.plotly_chart(fig_distribuidor)

def create_choropleth_maps(df):
    # Buscar dados geoespaciais da API do IBGE
    url = "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/26?formato=application/vnd.geo+json"
    response = requests.get(url)
    data = response.json()
    
    # Verificar a estrutura do JSON
    st.write("Estrutura da resposta JSON do IBGE:")
    st.json(data)

    # Extrair as features do JSON
    features = data.get("features", [])
    
    if not features:
        st.error("Não foi possível encontrar a chave 'features' no JSON retornado pela API.")
        return
    
    # Criar GeoDataFrame a partir das features
    gdf = gpd.GeoDataFrame.from_features(features)

    # Mapear códigos IBGE da planilha para o GeoDataFrame
    df['CD_MUN'] = df['CD_MUN'].astype(str)
    gdf['code'] = gdf['properties'].apply(lambda x: x['code'])
    gdf = gdf.set_index('code').join(df.set_index('CD_MUN'))

    # Primeiro Mapa: Consultores
    fig_consultor = px.choropleth(gdf.reset_index(), geojson=data, 
                                  locations='index', featureidkey='properties.code', color='CONSULTOR',
                                  hover_name='NM_MUNICIP', color_continuous_scale=px.colors.sequential.Blues)
    fig_consultor.update_geos(fitbounds="locations", visible=False, center={"lat": -8.47, "lon": -37.99}, projection_scale=10)
    st.subheader("Mapa de Consultores")
    st.plotly_chart(fig_consultor)

    # Segundo Mapa: Distribuidores
    fig_distribuidor = px.choropleth(gdf.reset_index(), geojson=data, 
                                     locations='index', featureidkey='properties.code', color='DISTRIBUIDOR',
                                     hover_name='NM_MUNICIP', color_continuous_scale=px.colors.sequential.Reds)
    fig_distribuidor.update_geos(fitbounds="locations", visible=False, center={"lat": -8.47, "lon": -37.99}, projection_scale=10)
    st.subheader("Mapa de Distribuidores")
    st.plotly_chart(fig_distribuidor)

if __name__ == "__main__":
    main()
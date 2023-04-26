# Libraris
import pandas as pd
import io
import re

import numpy as np
from datetime import date, datetime
import plotly.express as px
import plotly.graph_objects as go
import folium
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static



# Import dataset
df = pd.read_csv('train.csv')


# Limpeza do DataFrame
df1 = df.copy()
# 1 - Convertendo a coluna Age de texto para número 'int'.
linhas_vazias = (df1['Delivery_person_Age'] != 'NaN ')
df1 = df1.loc[linhas_vazias, :].copy()

linhas_vazias = (df1['Road_traffic_density'] != 'NaN ')
df1 = df1.loc[linhas_vazias, :].copy()

df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

linhas_vazias = (df1['City'] != 'NaN ')
df1 = df1.loc[linhas_vazias, :].copy()

linhas_vazias = (df1['Festival'] != 'NaN ')
df1 = df1.loc[linhas_vazias, :].copy()

# 2 - Convertendo a coluna Ratings de texto para número 'float'.
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
# 3 - Convertendo a coluna Date de texto para data.
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
# 4 - Convertendo a coluna  multiple_deliveries de texto para número (int).
linhas_vazias = (df1['multiple_deliveries'] != 'NaN ')
df1 = df1.loc[linhas_vazias, :].copy()
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
# 5 - Removendo os espaços dentro de strings/texto/object
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
# 6. Limpando a coluna time taken
def remove_units (df1, columns, what):
    for col in columns:
        df1[col] = df1[col].str.strip(what)
 
remove_units(df1, ['Time_taken(min)'], '(min)')

df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
## ===================================================================================
# Sidebar - Barra Lateral
## ===================================================================================
st.header('Marketplace - Visão Entregadores')

image = Image.open('megadados.png')
st.sidebar.image(image, width=250)


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")
st.sidebar.markdown('## Selecione uma data:')
data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')
     
st.sidebar.markdown("""___""")
traffic_options = st.sidebar.multiselect(
    'Quais as Condições do trânsito:',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""___""")
st.sidebar.markdown( '### Powered by Mega Dados' )

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]
## ===================================================================================
# Layout no Streamlit
## ===================================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','',''])

with tab1:
    with st.container():
        st.markdown('### Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = (df1.loc[:, 'Delivery_person_Age'].max())
            col1.metric("Maior Idade", maior_idade)
            
        with col2:
            menor_idade = (df1.loc[:, 'Delivery_person_Age'].min())
            col2.metric("Menor Idade", menor_idade)
            
        with col3:
            melhor_condicao = (df1.loc[:, 'Vehicle_condition'].max())
            col3.metric('Melhor Condição', melhor_condicao)
            
        with col4:
            pior_condicao = (df1.loc[:, 'Vehicle_condition'].min())
            col4.metric('Pior Condição', pior_condicao)
#=======================================================================           
    with st.container():
        st.markdown("""___""")
        st.markdown('### Avaliações')
        
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.markdown('##### Avaliação media por Entregador')
            df_avg_rating_per_deliver = (df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                            .groupby('Delivery_person_ID')
                                            .mean()
                                            .reset_index())
            st.dataframe(df_avg_rating_per_deliver)

            
        with col2:
            st.markdown('##### Avaliação média por Trânsito')
            df_avg_std_rating_by_traffic = ((df1.loc[: , [ 'Delivery_person_Ratings', 'Road_traffic_density']]
                                                .groupby('Road_traffic_density')
                                                .agg({'Delivery_person_Ratings':['mean', 'std']})
                                                .reset_index()))
            # Mudança de nome das Colunas           
            df_avg_std_rating_by_traffic.columns = ['Road_traffic_density', 'Delivery_mean', 'Delivery_std']  
            st.dataframe(df_avg_std_rating_by_traffic)
            
            st.markdown('##### Avaliação média por Clima')
            df_avg_std_rating_by_Weatherconditions = ((df1.loc[: , [ 'Delivery_person_Ratings', 'Weatherconditions']]
                                                          .groupby('Weatherconditions')
                                                          .agg({'Delivery_person_Ratings':['mean', 'std']})
                                                          .reset_index()))
            df_avg_std_rating_by_Weatherconditions.columns = ['Weatherconditions', 'Delivery_mean', 'Delivery_std']
            st.dataframe(df_avg_std_rating_by_Weatherconditions)
         
#=======================================================================          
    with st.container():
        st.markdown("""___""")
        st.markdown('##### Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            df2 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).min().sort_values(['City','Time_taken(min)'], ascending=True).reset_index()
            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            st.dataframe(df3)
            
            
            
        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df2 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).max().sort_values(['City','Time_taken(min)'], ascending=False).reset_index()
            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            st.dataframe(df3)    
        
        
        
        
        
        
        
        
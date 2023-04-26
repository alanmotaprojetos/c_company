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
st.header('Marketplace - Visão Restaurantes')

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
        st.markdown("___")
        st.markdown("### Overal Metrics")
        
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('E. Únicos', delivery_unique)
            
        with col2:
            col_delivery = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df_aux = df1['distance'] = df1.loc[:, col_delivery].apply( lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1 )
            media = np.round(df1['distance'].mean(), 2)
            col2.metric('Distânica Média', media)
            
        with col3:
            col_festival = ['Time_taken(min)', 'Festival']
            df_aux_festivais = df1.loc[:, col_festival].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
            df_aux_festivais.columns = ['mean_festivais', 'std_festivais']
            df_aux_festivais = df_aux_festivais.reset_index()
            tempo_medio_c_festival = np.round(df_aux_festivais.iloc[1, 1], 2)
            col3.metric('Com Festival', tempo_medio_c_festival)
         
        with col4:
            col_festival = ['Time_taken(min)', 'Festival']
            df_aux_festivais = df1.loc[:, col_festival].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
            df_aux_festivais.columns = ['mean_festivais', 'std_festivais']
            df_aux_festivais = df_aux_festivais.reset_index()
            desvio_padrao_c_festival = np.round(df_aux_festivais.iloc[1, 2], 2)
            col3.metric('STD c/ Fest.',  desvio_padrao_c_festival)
            
        with col5:
            col_festival = ['Time_taken(min)', 'Festival']
            df_aux_festivais = df1.loc[:, col_festival].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
            df_aux_festivais.columns = ['mean_festivais', 'std_festivais']
            df_aux_festivais = df_aux_festivais.reset_index()
            tempo_medio_s_festival = np.round(df_aux_festivais.iloc[0, 1], 2)
            col3.metric('Sem Festival', tempo_medio_s_festival)
            
        with col6:
            col_festival = ['Time_taken(min)', 'Festival']
            df_aux_festivais = df1.loc[:, col_festival].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
            df_aux_festivais.columns = ['mean_festivais', 'std_festivais']
            df_aux_festivais = df_aux_festivais.reset_index()
            desvio_padrao_s_festival = np.round(df_aux_festivais.iloc[0, 2], 2)
            col3.metric('STD s/ Fest.', desvio_padrao_s_festival)
            
            
            
    st.markdown("""___""")  
    with st.container():
        col1, col2 = st.columns(2)             
        with col1:
            st.markdown("##### Tempo Médio e Desvio Padrão por Cidade.")
            cols = ['City','Time_taken(min)']
            df_aux = df1.loc[:, cols].groupby( 'City' ).agg( {'Time_taken(min)':['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Control',
                                x=df_aux['City'],
                                y=df_aux['avg_time'],
                                error_y=dict(type='data', array=df_aux['std_time'])))
            st.plotly_chart(fig.update_layout(barmode='group'))
        
        with col2:
            st.markdown("##### Tempo médio e o desvio padrão p/ cidade e pedido")
            
            cols = ['City', 'Time_taken(min)', 'Type_of_order']
            df_aux_tempo = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)':['mean', 'std']})
            df_aux_tempo.columns = ['mean_entrega','std_entrega']
            df_aux_tempo = df_aux_tempo.reset_index()
            st.dataframe( df_aux_tempo )
            
        
    with st.container():
        st.markdown("""___""")
        st.markdown("#### Distribuição do Tempo")
        
        col1, col2 = st.columns(2)
        with col1:  
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df1['distance'] = df1.loc[:, cols].apply( lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1 )
            
            avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0.1,0.1,0])]) 
            st.plotly_chart(fig) 
            
            
    with st.container():        
        with col2:
            st.markdown("##### Tempo médio e o desvio padrão p/ cidade e tipo de tráfego")
            cols = ['City', 'Road_traffic_density', 'Time_taken(min)']
            df_aux_city_traffic = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
            df_aux_city_traffic.columns = ['mean_traffic','std_traffic']
            df_aux_city_traffic = df_aux_city_traffic.reset_index()

            st.plotly_chart(px.sunburst(df_aux_city_traffic, path=['City', 'Road_traffic_density'], values='mean_traffic',color='std_traffic', color_continuous_scale='RdBu',color_continuous_midpoint=np.average(df_aux_city_traffic['std_traffic'])))
        
        
        
        
        
        
        
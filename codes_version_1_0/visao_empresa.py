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
st.header('Marketplace - Visão Cliente')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        # Order Traffic
        # Visão Empresas
        ## 1. Quantidade de pedidos por dia.
        st.markdown("# Visão Gerencial")
        st.markdown("## I-Orders by Day")
        quantidade = df1[['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
        
        fig = px.bar(quantidade, x = 'Order_Date', y = 'ID')
        st.plotly_chart(fig, use_container=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("II-Traffic Order Share")
            cols5 = ['ID', 'Road_traffic_density'] 
            df_aux2 = df1.loc[:, cols5].groupby('Road_traffic_density').count().reset_index() 
            df_aux2['Percentual'] = df_aux2['ID'] / df_aux2['ID'].sum()
        
            fig2 = px.pie(df_aux2, values='Percentual', names='Road_traffic_density')
            st.plotly_chart(fig2, use_container=True)
            
              
        with col2:
            st.header('III-Traffic Order City')
            df1 = df1.loc[df1['City'] != 'NaN', :]
            comp_vcity = ['City', 'Road_traffic_density', 'ID']
            vol_city = df1.loc[:, comp_vcity].groupby(['City', 'Road_traffic_density']).count().reset_index()
            fig3 = px.scatter(vol_city, x= 'City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig3, use_container=True)    


        

with tab2:
    with st.container():
        st.markdown("# Visão Tática")
        st.markdown("### IV-Order by Week")
        
        df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
        amount_year = df1[['ID', 'week_of_year']].groupby( 'week_of_year' ).count()
        fig4 = px.line(amount_year)
        st.plotly_chart(fig4, use_container=True)
    
    with st.container():
        st.markdown("### V-Order Share by Week")
        df_aux01 = df1.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

        df_aux = pd.merge(df_aux01, df_aux02, how= 'inner') 
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        fig5 = px.line(df_aux, x = 'week_of_year', y = 'order_by_deliver') 
        st.plotly_chart(fig5, use_container=True)
    
with tab3:
    st.markdown("# Visão Geográfica")
    st.markdown("### VI-Country Maps")

    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density' ]).median().reset_index()

    map_ = folium.Map()
    for i in range( len( df_aux ) ):
        folium.Marker( [df_aux.loc[i, 'Delivery_location_latitude'], df_aux.loc[i, 'Delivery_location_longitude']]).add_to(map_)
    folium_static(map_, width=1024 , height=600)



#with tab4:
 #   st.header("Configurações Gerais")
  #  uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
    #for uploaded_file in uploaded_files:
     #   bytes_data = uploaded_file.read()
    #st.write("filename:", uploaded_file.name)
    #st.write(bytes_data)
    
        


print("Código executado com sucesso!!")
#Libraries
import pandas as pd
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
import folium 
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='✍️', layout='wide')
#------------------------
# Funções
#------------------------
def country_maps(df):
    data_plot = df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby( ['City', 'Road_traffic_density']).median().reset_index()
    data_plot = data_plot[data_plot['City'] != 'NaN']
    data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']
    # Desenhar o mapa
    map_ = folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                          location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
  
    folium_static(map_, width=1024, height=600)

def order_share_by_week(df):
    cols = ['ID','Delivery_person_ID', 'week_of_year']
    df_aux1 = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year' ).count().reset_index()
    df_aux2 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig


def order_by_week(df):
    #Quantidade de pedidos por semana
    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')
    cols = ['ID', 'week_of_year']
    df_aux = df.loc[:, cols].groupby('week_of_year').count().reset_index()
    fig=px.line(df_aux, x='week_of_year', y='ID')
    return fig
        
def traffic_order_city(df):
    cols = ['ID', 'City', 'Road_traffic_density']
    df_aux = df.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[df_aux['City']!='NaN',:]
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN',:]
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID') 
    return fig

def traffic_order_share (df):
    cols = ['ID', 'Road_traffic_density' ]   
    df_aux = df.loc[:, cols].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN',:]
    df_aux['perc_ID'] = 100* (df_aux['ID'] / df_aux['ID'].sum())
    fig = px.pie(df_aux, values = 'perc_ID', names = 'Road_traffic_density')
    return fig
            
def order_metric(df):
    #quandidade de pedidos por dia
    cols = ['ID', 'Order_Date']
    df_aux = df.loc[:, cols].groupby('Order_Date').count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']
    #gráfico
    fig = px.bar(df_aux, x='order_date', y='qtde_entregas')
    return fig
        
def clean_code (df_ori):

    #Limpeza do Dataframe
    df = df_ori.copy()

    df = df.loc[df['Delivery_person_Age'] != 'NaN ', :]
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)

    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)

    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    # Remove as linhas da culuna multiple_deliveries que tenham o 
    # conteudo igual a 'NaN '
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    linhas_vazias = df['City'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['Festival'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # Removendo espaços dentro de stings/object/texto
    df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
    df.loc[:,'Road_traffic_density'] = df.loc[:,'Road_traffic_density'].str.strip()
    df.loc[:,'Type_of_order'] = df.loc[:,'Type_of_order'].str.strip()
    df.loc[:,'Type_of_vehicle'] = df.loc[:,'Type_of_vehicle'].str.strip()
    df.loc[:,'City'] = df.loc[:,'City'].str.strip()

    #Limpando a coluna Time_taken
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)
    
    return df

#Import dataset
df_ori = pd.read_csv ('dataset/train.csv')

#Limpeza do Dataframe
df = df_ori.copy()

#Cleaning dataset
df = clean_code(df_ori)

#======================================
# Barra Lateral
#======================================

st.header('Marketplace - Visão Empresa')

image_path='/home/renata/Documentos/repos/ds_ao_dev/Ciclo06/logo.png'
image= Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery  in Town')
st.sidebar.markdown("""---""")


st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2023,3,21),
    min_value=pd.datetime(2022,2,11),
    max_value=pd.datetime(2022,4,6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do transito?',
    ['Low', 'Medium','High','Jam'],
    default='Low')

st.sidebar.markdown("""---""")

#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas,:]


#Filtro de data
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas,:]

#======================================
# Layout no Streamlit
#======================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('# Orders by Day')
        fig = order_metric(df)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('# Traffic Order Share')
            fig = traffic_order_share(df)
            st.plotly_chart(fig,use_container_width=True)
                       
        with col2:            
            st.markdown('# Traffic Order City')
            fig = traffic_order_city(df)
            st.plotly_chart(fig, use_container_width=True)       
    
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df)
        st.plotly_chart(fig, use_container_width=True)
           
    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df)
        st.plotly_chart(fig, use_container_width=True)
            
with tab3:
    st.markdown('#Country Maps ')
    country_maps(df)
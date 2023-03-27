#Libraries
import pandas as pd
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
import folium 
from streamlit_folium import folium_static
import numpy as np
import plotly.graph_objs as go


st.set_page_config( page_title='Visão Restaurantes', page_icon='✍️', layout='wide')
#------------------------
# Funções
#------------------------

def avg_std_time_on_traffic(df):
    cols = ['Time_taken(min)','City', 'Road_traffic_density']
    df_aux = df.loc[:, cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean', 'std']})
    df_aux.columns = ['avg', 'std']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg', color='std', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std']))
    return fig


def avg_std_time_graph (df):
    df_aux = (df.loc[:,['City', 'Time_taken(min)']]
                .groupby('City')
                .agg({'Time_taken(min)':['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
           
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'],error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig
        
        
def avg_std_time_delivery(df, festival, op):
    """
        Está função calcula o tempo médio e o desvio padrão do tempo de entrega
           Input: 
              - df: dataframe com os dados necessários para os cálculos
              - op: tipo de operação que precisa ser calculado
                  'avg_time': calcula o tempo médio
                  'std_time': calcula o desvio padrão do tempo
            Output: 
              - df: dataframe com duas colunas e uma linha
    """
    
    cols = ['Festival', 'Time_taken(min)']
    df_aux = (df.loc[:,cols]
                .groupby('Festival')
                .agg({'Time_taken(min)':['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op],2) 
    
    return df_aux

def distance(df, fig):
    if fig==False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df['distance'] = df.loc[:,cols].apply(lambda x:                   haversine((x['Restaurant_latitude'],x['Restaurant_longitude']), (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1 )
        avg_distance = np.round(df['distance'].mean(),2)          
        return avg_distance
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df['distance'] = df.loc[:,cols].apply(lambda x:                   haversine((x['Restaurant_latitude'],x['Restaurant_longitude']), (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1 )     
        avg_distance = df.loc[:,['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure (data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'],pull=[0,0.1,0])])
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

st.header('Marketplace - Visão Entregadores')

#image_path='/home/renata/Documentos/repos/ds_ao_dev/Ciclo06/logo.png'
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

weather_options = st.sidebar.multiselect(
    'Quais as condições climáticas?',
    ['conditions Cloudy', 'conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny', 'conditions Windy'])

st.sidebar.markdown("""---""")

#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas,:]


#Filtro de tipo de tráfego
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas,:]

#Filtro de clima
linhas_selecionadas = df['Weatherconditions'].isin(weather_options)
df = df.loc[linhas_selecionadas,:]


#======================================
# Layout no Streamlit
#======================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        st.markdown('##### 01')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            qtd_entregadores = len(df['Delivery_person_ID'].unique())
            col1.metric('Entregadores', qtd_entregadores)
            
        with col2:
            avg_distance = distance(df, fig=False)
            col2.metric('Distância',avg_distance) 
            
        with col3:           
            df_aux = avg_std_time_delivery(df,'Yes ', 'avg_time')
            col3.metric('Tempo Médio', df_aux)
                   
        with col4:
            df_aux = avg_std_time_delivery(df,'Yes ','std_time') 
            col4.metric('Std Entrega', df_aux)
        
        with col5:
            df_aux = avg_std_time_delivery(df,'No ','avg_time') 
            df_aux = col5.metric('Tempo Médio', df_aux)
                 
        with col6:
            df_aux = avg_std_time_delivery(df,'No ','std_time') 
            col6.metric('Std Entrega', df_aux)
        
    with st.container():
        st.markdown("""---""")
        st.markdown('##### 02')
        fig = avg_std_time_graph (df)
        st.plotly_chart(fig)

            

    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        with col1:
            fig = distance(df, fig=True)
            st.plotly_chart(fig)
            
            
                     
        with col2:
            fig = avg_std_time_on_traffic(df)
            st.plotly_chart(fig)

        
    with st.container():
        st.markdown("""---""")
        cols = ['Time_taken(min)','City', 'Type_of_order']
        df_aux = df.loc[:, cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean', 'std']})
        df_aux.columns = ['avg', 'std']
        df_aux.reset_index()
        st.dataframe(df_aux)
        
        
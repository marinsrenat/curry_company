#Libraries
import pandas as pd
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
import folium 
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon='✍️', layout='wide')
#------------------------
# Funções
#------------------------
def top_delivers(df, top_asc):
    cols = ['Delivery_person_ID', 'City', 'Time_taken(min)']
    df2 = (df.loc[:, cols].groupby(['City', 'Delivery_person_ID'])
                          .max()
                          .sort_values(['City','Time_taken(min)'], ascending = top_asc)
                          .reset_index())
               
    df_aux1 = df2.loc[df2['City']=='Urban',:].head(10)
    df_aux2 = df2.loc[df2['City']=='Semi-Urban',:].head(10)
    df_aux3 = df2.loc[df2['City']=='Metropolitian',:].head(10)

    df3=pd.concat([df_aux1,df_aux2,df_aux3]).reset_index(drop=True)
                
    return df3

            
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
        st.markdown('# Overrall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #Maior idade dos entregadores           
            max_age = df.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade', max_age)
                
        with col2:
            #Menor idade dos entregadores
            min_age = df.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade',min_age)

        with col3:
            #Pior condição do veículo          
            pior = df.loc[:,'Vehicle_condition'].min() 
            col3.metric('Pior condição', pior)

        with col4:
            #Melhor condição do veículo
            melhor = df.loc[:,'Vehicle_condition'].max()
            col4.metric('Melhor condição', melhor)
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            #Avaliação média por entregador
            st.markdown('##### Avaliação média por entregador')
            cols = ['Delivery_person_Ratings', 'Delivery_person_ID']
            df_avg_ratings_per_deliver = (df.loc[:,cols]
                                            .groupby('Delivery_person_ID')
                                            .mean()
                                            .reset_index())
            st.dataframe(df_avg_ratings_per_deliver)
                    
        with col2:
            #Avaliação média e o desvio padrão por tipo de tráfego
            st.markdown('##### Avaliação média por tipo de tráfego')
            cols = ['Delivery_person_Ratings', 'Road_traffic_density']
            df_aux = df.loc[df['Road_traffic_density']!= 'NaN']
            df_avg_std_ratings_by_traffic = (df_aux.loc[:, cols]
                                                   .groupby('Road_traffic_density')
                                                   .agg({'Delivery_person_Ratings':['mean', 'std']})
                                                   .reset_index())
            #Mudança do nome de colunas
            df_avg_std_ratings_by_traffic.columns = ['Road_traffic_density', 'delivery_mean', 'delivery_std']
            st.dataframe(df_avg_std_ratings_by_traffic)
            
            
            st.markdown('##### A avaliação média por condição climática')  
            #A avaliação média e o desvio padrão por condição climática
            cols = ['Delivery_person_Ratings', 'Weatherconditions']
            df_aux = df.loc[df['Weatherconditions']!= 'conditions NaN']
            df_avg_std_ratings_by_weather = (df_aux.loc[:, cols]
                                                   .groupby('Weatherconditions')
                                                   .agg({'Delivery_person_Ratings':['mean', 'std']})
                                                   .reset_index())
            df_avg_std_ratings_by_weather.columns = ['Road_traffic_density', 'delivery_mean', 'delivery_std']
            st.dataframe(df_avg_std_ratings_by_weather)
        
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df3 = top_delivers(df, top_asc=True)
            st.dataframe(df3)
        
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df3 = top_delivers(df, top_asc=False)
            st.dataframe(df3)
            
  
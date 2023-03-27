import streamlit as st
from PIL import Image


st.set_page_config(
    page_title= "Home",
    page_icon= "✍️"
)

#image_path='/home/renata/Documentos/repos/ds_ao_dev/Ciclo06/logo.png'
image= Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery  in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")
st.markdown(
    """
        Growth Dashboard foi construido para acompanhar as métricas de crescimento dos entregadores e restaurantes. 
        ### Como utilizar o Growth Dashboard:
        - Visão Empresa:
            - Visão Gerencial: Métricas gerais de comportamento
            - Visão Tática: Indicadores semanais de crescimento
            - Visão Geográfica: Insights de geolocalização
        - Visão Entregador:
            - Acomapanhamento dos indicadores semananis de crescimento
        - Visão Restaurante:
            - Indicadores semanais de crescimento dos restaurantes
        ### Ask for help
        - Time de Data Science no Discord
            - @meigarom
    """
)
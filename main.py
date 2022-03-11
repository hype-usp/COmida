import streamlit as st
import pandas as pd
import numpy as np
import pickle
from scipy.interpolate import interp1d
import data

if 'ingredientes' not in st.session_state:
    st.session_state.ingredientes = ['-']
    st.session_state.ingredientes_bool = [False]

def update_ingredientes():
    receita = data.receitas[data.receitas.name == st.session_state.recipe_chosen]
    ingredientes = get_ingredientes(receita)
    st.session_state.ingredientes = ingredientes
    st.session_state.ingredientes_bool = [False]*len(st.session_state.ingredientes)

def get_ingredientes(receita):
    ings = pd.merge(pd.DataFrame(receita['ingredients'].values[0], columns=['name']), 
                    data.nutrientes[['name', 'protein', 'carb', 'lipid', 'score']], 
                    on='name')
    ings['unhealthy'] = ings['score'].apply(lambda a: a <= -15.24)
    return ings.reset_index()

embedding = pickle.load(open("embedding.pickle", "rb"))

st.title('COmida')

nome_receita = st.selectbox(
    label = 'Escolha a sua receita!', 
    options=data.receitas['name'].values,
    key='recipe_chosen', 
    on_change=update_ingredientes
)
receita = data.receitas[data.receitas.name == nome_receita]

st.write('Estes são os ingredientes da sua receita:')

ings = st.session_state.ingredientes
def heatmap(val):
    if type(val) != type('teste'):
        minimo = ings.select_dtypes(exclude=['object']).min().min()
        maximo = ings.select_dtypes(exclude=['object']).max().max()
        map = interp1d([minimo, maximo], [255, 0])
        color = map(val)
        return 'background: rgb(255, '+str(3*color)+', '+str(color)+'); color: black;'
    else:
        return None

try:
    st.dataframe(ings.style.applymap(heatmap))

    with st.expander('Escolha quais ingredientes você quer trocar:'):
        for i in range(len(st.session_state.ingredientes)):
            if st.session_state.ingredientes['unhealthy'][i]:
                st.session_state.ingredientes_bool[i] = st.checkbox(st.session_state.ingredientes['name'][i])

    chosen_ings_names = [st.session_state.ingredientes['name'][i] for i in range(len(st.session_state.ingredientes_bool)) if st.session_state.ingredientes_bool[i]]
    chosen_ings = st.session_state.ingredientes[st.session_state.ingredientes.name.isin(chosen_ings_names)].reset_index()

    trocas = []

    for ing in range(len(chosen_ings)):
        top20 = pd.merge(pd.DataFrame([i[0] for i in embedding.wv.most_similar(chosen_ings['name'].iloc[ing], topn=20)], columns=['name']),
                data.nutrientes[['name', 'protein', 'carb', 'lipid', 'score']], on='name').sort_values(by=['score'], ascending=False)
        top20['healthier'] = top20['score'].apply(lambda a: a > chosen_ings['score'].iloc[ing])
        troca = top20[top20['healthier']]['name'].values
        trocas.append(troca)

    cols = st.columns(len(chosen_ings))

    for i in range(len(chosen_ings)):
        with cols[i]:
            st.write(chosen_ings['name'][i] + ':')
            st.dataframe(pd.DataFrame(trocas[i], columns=['Ingrediente']))

except:
    st.write(ings)

import pandas as pd
import gensim

nutrientes = pd.read_csv('https://raw.githubusercontent.com/hype-usp/Grupos-de-estudos/main/COmida/nutrientes.csv', index_col=0)#[['name', 'protein', 'carb', 'lipid']]
nutrientes['score'] = nutrientes['protein'] - nutrientes['lipid']*0.5 - nutrientes['carb']

receitas = pd.read_csv('receitas_essencial.csv')[:100]
receitas['ingredients'] = receitas['ingredients'].apply(lambda a: [i[1:-1] for i in a[1:-1].split(', ')])
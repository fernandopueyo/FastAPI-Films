import csv
import json
import pandas as pd

# # Nombre del archivo TSV de entrada y archivo JSON de salida
# archivo_tsv = 'data/data.tsv'
# archivo_json = 'data/data.json'

# # Leer el archivo TSV y convertirlo a una lista de diccionarios
# datos = []
# with open(archivo_tsv, 'r', newline='', encoding='utf-8') as tsvfile:
#     tsvreader = csv.DictReader(tsvfile, delimiter='\t')
#     for fila in tsvreader:
#         datos.append(fila)

# # Escribir los datos en un archivo JSON
# with open(archivo_json, 'w', encoding='utf-8') as jsonfile:
#     json.dump(datos, jsonfile, indent=4, ensure_ascii=False)

# print(f'Se ha convertido {archivo_tsv} a {archivo_json}')


data_film = pd.read_table('data/data.tsv')

data_film.startYear.value_counts()

data_movies = data_film[data_film.titleType == 'movie']
data_movies.startYear.value_counts()
data_movies = data_movies.replace('\\N',None)
data_movies['startYear'] = pd.to_numeric(data_movies['startYear'])

years = range(2010,2024)
data_film_201023 = data_movies[data_movies['startYear'].isin(years)]

data_film_201023.to_json('data/data.json', orient='records')

# Ratings

data_films = pd.read_json('data/data.json')

data_ratings = pd.read_table('data/data_ratings.tsv')

data_ratings_films = data_ratings[data_ratings['tconst'].isin(data_films.tconst)]
data_ratings_films.tconst.nunique()
data_films.tconst.nunique()

data_ratings_films.to_json('data/data_ratings.json', orient='records')


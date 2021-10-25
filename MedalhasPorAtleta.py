import plotly.express as px
import pandas as pd
from dash import Dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output

# Leitura dos dados
dados_csv = pd.read_csv("dados/athlete_events.csv")

#ID[0],"Name"[1],"Sex"[2],"Age"[3],"Height"[4],"Weight"[5],"Team"[6],
# "NOC"[7],"Games"[8],"Year"[9],"Season"[10],"City"[11],"Sport"[12],
# "Event"[13],"Medal"[14]

agrupado_por_ano = {}
maiores_medalhistas= {}
# Monta um dicionário a partir dos anos como chaves, e dentro de cada 
# ano existe outro dicionário que contém o nome dos atletas como chaves 
# e um dicionário com as medalhas como valores. 


for linha in dados_csv.values:  
    if type(linha[14]) != str:
        continue
    nome = linha[1]
    ano = linha[9]
    medalha = linha[14]
    
    if agrupado_por_ano.get(ano) == None:
        agrupado_por_ano[ano] = {}
    if agrupado_por_ano[ano].get(nome) == None:
        agrupado_por_ano[ano][nome] = {'Gold': 0, 'Silver': 0, 'Bronze': 0}

    
    agrupado_por_ano[ano][nome][medalha]+=1

    # Guardando os elementos dentro do dicionário: maiores_medalhistas
    if maiores_medalhistas.get(nome)== None:
        maiores_medalhistas[nome]= {'Gold': 0, 'Silver': 0, 'Bronze': 0}
    
    maiores_medalhistas[nome][medalha]+=1


# Ordenando e pegando os 50 maiores medalhistas

# O método 'items()' devolve tuplas das chaves e valores de um dicionário, a função do sorted os ordena de acordo com a quantidade de medalhas em ordem decrescente.

# O método 'sorted()' vai devolver uma lista de tuplas, então depois de ser fatiada para pegar os 50 maiores(primeiros) medalhistas, ela será transformada em um dicionário pelo método 'dict()'.

maiores_medalhistas = dict(sorted(maiores_medalhistas.items(), key  = lambda item: (item[1]['Gold'], item[1]['Silver'], item[1]['Bronze']), reverse=True)[:50])      

# Ordena as chaves do dicionário 'agrupado_por_ano'.

anos_ordenados = sorted(agrupado_por_ano, reverse = True)


# Adiciona 'Total' à lista para a seleção no dropdown.

anos_ordenados.insert(0,'Total') 

# Adiciona os melhores medalhistas ao dicionário agrupado_por_ano.
 
agrupado_por_ano['Total'] = maiores_medalhistas


app = Dash(__name__)

app.layout = html.Main(
            className="medalhasPorAtleta",
            
            children = [
                html.Header(
                    children = [
                        html.Img(src="./assets/logo.svg"),
                        html.Div(
                            children=[
                                html.Img(src="./assets/left-wings.svg"),
                                html.H1('Medalhas por Atleta'),
                                html.Img(src="./assets/rigth-wings.svg"),
                            ]
                        ),
                        html.Img(src="./assets/medalhas.svg")
                    ]                               
                ),
                html.Section(
                    children = [
                        dcc.Dropdown(
                            className="drop",
                            id = "ano_selecionado",
                            options = [{"label": str(ano), "value": ano} for ano in anos_ordenados],
                            value = anos_ordenados[0],
                            style = {"width": "100px"}
                        ),
                        dcc.Graph(
                            className="grafico",
                            id = "grafico",
                            figure = [],
                                    
                        ),
                    ]
                    
                )
            ]
        )              



@app.callback(
    Output(component_id = "grafico", component_property="figure"),
    Input(component_id = "ano_selecionado", component_property = "value")
)


def atualizar_grafico(ano_selecionado):
    copia = agrupado_por_ano[ano_selecionado].copy()
    

    # Ordenação dos atletas pelas medalhas por peso: 'Gold', 'Silver' e 'Bronze'.

    copia = dict(sorted(copia.items(), key  = lambda item: (item[1]['Gold'], item[1]['Silver'], item[1]['Bronze']), reverse=True))
    
    df = {'nome' : [], 'Gold' : [], 'Silver' : [], 'Bronze' : []}  

    for nome, medalhas in zip(copia.keys(), copia.values()): # O zip permite percorrer duas listas com duas variaveis, nome: copia.keys() e medalhas: copia.values()    
        df['nome'].append(nome)
        df['Gold'].append(medalhas['Gold'])
        df['Silver'].append(medalhas['Silver'])
        df['Bronze'].append(medalhas['Bronze'])
    

    figure = px.bar(
            df,  
            x = 'nome',
            y = ['Gold','Silver','Bronze'], 
            color_discrete_map = {'Gold':'gold', 'Silver':'silver', 'Bronze':'rgb(148,93,65)'},                    
            labels ={'value':'Quantidade de medalhas', 'variable':'Medalhas', 'nome':'Atletas'}    
        )
    return figure
    

app.run_server(port=3004)

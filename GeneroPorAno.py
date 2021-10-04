from pandas import read_csv 
#importação do leitor de dados
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash import Dash, html, dcc

dados = read_csv("dados/athlete_events.csv", delimiter = ",") 
#lendo de dados do arquivo csv

agrupadosporano = {}

'''
0  'ID',
1  'Name',
2  'Sex',
3  'Age',
4  'Height',
5  'Weight',
6  'Team',
7  'NOC',
8  'Games',
9  'Year',
10 'Season',
11 'City',
12 'Sport',
13 'Event',
14 'Medal'
'''

idsLidos = set()

for linha in dados.values: 
    if linha[0] in idsLidos:
        continue
    #condicional para que os ids já armazenados no set não sejam lidos novamente

    ano = linha[9]
    temporada = linha[10]
    sexo = linha[2]
    if agrupadosporano.get(ano) == None:
    #condicional para verificar se o ano já existe dentro da dict "agrupadosporano"
        agrupadosporano[ano] = {"Summer": [], "Winter": []}
    
        
    agrupadosporano[ano][temporada].append(sexo)
    idsLidos.add(linha[0])


anos = list(agrupadosporano.keys())
anos.sort()
#ordenando os anos dentro da list em ordem crescente

seasonsDataFrame = {
    "Summer": {"Ano":[],"Homens":[], "Mulheres":[]},
    "Winter": {"Ano":[],"Homens":[], "Mulheres":[]}
}
#criando dicionário para armazenar os valores de "Ano", "Homens" e "Mulheres" dentro das keys: Summer e Winter

for ano in anos:
    for season in agrupadosporano[ano]: #
        #season pode ser Summer ou Winter
        male = 0
        female = 0
        for sexo in agrupadosporano[ano][season]:
            if sexo == "M":
                male += 1 
                continue 
            female += 1 

        if male == 0 and female == 0:
            continue
        
        seasonsDataFrame[season]["Ano"].append(ano)
        seasonsDataFrame[season]["Homens"].append(male)
        seasonsDataFrame[season]["Mulheres"].append(female)
        #armazenando o ano e a quantidade de homens e mulheres (a cada ano) nos dataframes 

        

app = Dash(__name__)
#iniciando o dash

app.layout = html.Div(
    className="container-imc-per-country",
    children=[
        html.Header(
            children=[
                html.Img(src="./assets/logo.svg"),
                html.Div(
                    children=[
                        html.Img(src="./assets/left-wings.svg"),
                        html.H1("Olimpiadas"),
                        html.Img(src="./assets/rigth-wings.svg"),
                    ]
                ),
            ]
        ),
        html.Main(
            children=[
                html.H1("Gênero por Ano", className="title"),
                html.Section(
                    [
                        dcc.Dropdown( 
                        #menu suspenso para alternar o gráfico entre as temporadas summer e winter
                            id="selectedSeason",
                            options=[{"label": "Inverno", "value":"Winter"}, {"label": "Verão", "value": "Summer"}],
                            value= "Summer",
                            style={"width": "200px"},
                        ),
                        dcc.Graph(
                            id="graph",
                            figure=[],
                        ),
                    ],
                ),
            ]
        ),
    ],
)
#layout do dash 

@app.callback(
    Output(component_id="graph", component_property="figure"),
    [Input(component_id="selectedSeason", component_property="value")],
)
#callback para atualizar o gráfico de acordo com o input do usuário 

def updateGraph(selectedSeason): 
#função para atualizar o gráfico

    df = seasonsDataFrame[selectedSeason]

    grafico = go.Figure()
    grafico.add_trace(go.Scatter(x=df["Ano"], y=df["Homens"], name = "Homens"))
    grafico.add_trace(go.Scatter(x=df["Ano"], y=df["Mulheres"], name = "Mulheres"))
    grafico.update_layout(width=1200, height=675)
    return grafico

app.run_server()
#rodando o gráfico no dash
    
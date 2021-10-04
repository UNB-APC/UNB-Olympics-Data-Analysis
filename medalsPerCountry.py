from pandas import read_csv  # IMPORTA O LEITOR DE BANCO DE DADOS
# IMPORTA A CALLBACK QUE ATUALIZA O GRAFICO
from dash.dependencies import Input, Output
import plotly.express as px  # MODULO PARA CRIAR O GRAFICO
from dash import Dash, html, dcc  # IMPORTA A PAGINA WEB

dados = read_csv(
    "dados/athlete_events.csv",
    delimiter=",",
    keep_default_na=False,
    na_values=["_"],
)  # LÊ OS DADOS


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


# sigla 7, medelha 14

agrupadoPorAno = {}  # DICT QUE ARMAZENA OS DAOS AGRUPADOS PELOS ANOS
# sigla 7, medelha 14 , temporada 8

for linha in dados.values:
    if linha[14] == "NA":  # CASO RETORNE "NA" ELE IGNORA E CONTINUA
        continue
    sigla = linha[7]  # ATRIBUI A SIGLA ALOCADA NA POSIÇÃO 7
    medalha = linha[14]  # ATRIBUI AS MEDALHAS ALOCADAS NA POSIÇÃO 14
    ano = linha[8]  # ATRIBUI O ANO  ALOCADO NA POSIÇÃO 8

    # VERIFIACAR SE ANO JÁ EXISTE, CRIA CASO NAO EXISTA
    if agrupadoPorAno.get(ano) == None:
        agrupadoPorAno[ano] = {}
    # VERIFICAR SE SIGLA JÁ EXISTE, CRIA CASO NAO EXISTA
    if agrupadoPorAno[ano].get(sigla) == None:
        agrupadoPorAno[ano][sigla] = []

    agrupadoPorAno[ano][sigla].append(medalha)  # ADICIONA MEDALHA AO ARRAY


anos = list(agrupadoPorAno.keys())  # PEGA TODOS OS ANOS
anos.sort(reverse=True)  # ORGANIZA EM ORDEM CRESCENTE

dataFrameObject = {  # ONDE SERÁ ARMAZENADO OS DADOS EM ORDEM
    "ano": [],
    "sigla": [],
    "Medalhas totais": [],
    "Medalhas de ouro": [],
    "Medalhas de prata": [],
    "Medalhas de bronze": [],
}

for ano in anos:  # PERCORRE CADA ANO
    for pais in agrupadoPorAno[ano]:  # PERCORRE CADA PAIS EM CADA ANO
        ouroTotal = 0
        bronzeTotal = 0
        prataTotal = 0
        medalhaTotal = 0
        # PERCORRE AS MEDALHAS DE CADA PAÍS EM CADA ANO
        for medalha in agrupadoPorAno[ano][pais]:
            medalhaTotal += 1
            if medalha == "Gold":  # CASO A MEDALHA SEJA DE OURO, ADICIONA 1 A MEDALHAS DE OURO
                ouroTotal += 1
                continue
            if medalha == "Silver":  # CASO A MEDALHA SEJA DE PRATA, ADICIONA 1 A MEDALHAS DE PRATAS
                prataTotal += 1
                continue
            bronzeTotal += 1  # CASO A MEDALHA NÃO SEJE DE OURO OU DE PRATA ELA ENTRA COMO BRONZE
        dataFrameObject["ano"].append(ano)  # COLOCA O VALOR NO DATAFRAME
        dataFrameObject["sigla"].append(pais)
        dataFrameObject["Medalhas totais"].append(medalhaTotal)
        dataFrameObject["Medalhas de ouro"].append(ouroTotal)
        dataFrameObject["Medalhas de prata"].append(prataTotal)
        dataFrameObject["Medalhas de bronze"].append(bronzeTotal)


app = Dash(__name__)

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
                html.H1("Medalhas por país", className="title"),
                html.Section(
                    [
                        dcc.Dropdown(  # FAZ UMA LISTA DOS ANOS
                            id="selectedYear",
                            options=[{"label": str(ano), "value": ano}
                                     for ano in anos],
                            value=anos[0],
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


@app.callback(  # ATUALIZA O GRAFICO CONFORME A ESCOLHA DO USUARIO
    Output(component_id="graph", component_property="figure"),
    [Input(component_id="selectedYear", component_property="value")],
)
def updateGraph(selectedYear):  # SELECIONA O ANO
    copy = dataFrameObject.copy()
    df = {
        "sigla": [],
        "Medalhas totais": [],
        "Medalhas totais": [],
        "Medalhas de ouro": [],
        "Medalhas de prata": [],
        "Medalhas de bronze": [],
    }

    for index in range(len(copy["ano"])):  # FILTRA OS VALORES DO ANO
        if copy["ano"][index] == selectedYear:
            df["sigla"].append(copy["sigla"][index])
            df["Medalhas totais"].append(copy["Medalhas totais"][index])
            df["Medalhas de ouro"].append(copy["Medalhas de ouro"][index])
            df["Medalhas de prata"].append(copy["Medalhas de prata"][index])
            df["Medalhas de bronze"].append(copy["Medalhas de bronze"][index])

    figure = px.choropleth(  # GRAFICO
        df,
        locations="sigla",
        color="Medalhas totais",
        color_continuous_scale="Viridis",
        hover_name="sigla",
        hover_data=[
            "Medalhas de bronze",
            "Medalhas de prata",
            "Medalhas de ouro",
        ],
        width=1200,  # LARGURA
        height=675,  # ALTURA
    )

    figure.update_geos(  # ATUALIZAR AS CARACTERISTICAS DO GRAFICO
        showocean=True,
        coastlinecolor="#610059",
        oceancolor="#b7ddf4",
        landcolor="#f7f8fa",
    )

    return figure  # RETORNA O GRAFICO


# ------------------------------------------------------------
# Running Server
# ------------------------------------------------------------
app.run_server()

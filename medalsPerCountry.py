from pandas import read_csv

from dash.dependencies import Input, Output

import plotly.express as px
from dash import Dash, html, dcc


dados = read_csv(
    "dados/athlete_events.csv",
    delimiter=",",
    keep_default_na=False,
    na_values=["_"],
)

agrupadoPorAno = {}
# sigla 7, medelha 14
for linha in dados.values:
    if linha[14] == "NA":
        continue
    sigla = linha[7]
    medalha = linha[14]
    ano = linha[8]

    if agrupadoPorAno.get(ano) == None:
        agrupadoPorAno[ano] = {}
    if agrupadoPorAno[ano].get(sigla) == None:
        agrupadoPorAno[ano][sigla] = []

    agrupadoPorAno[ano][sigla].append(medalha)


anos = list(agrupadoPorAno.keys())
anos.sort()

dataFrameObject = {
    "ano": [],
    "sigla": [],
    "Medalhas totais": [],
    "Medalhas de ouro": [],
    "Medalhas de prata": [],
    "Medalhas de bronze": [],
}

for ano in anos:
    for pais in agrupadoPorAno[ano]:
        ouroTotal = 0
        bronzeTotal = 0
        prataTotal = 0
        medalhaTotal = 0
        for medalha in agrupadoPorAno[ano][pais]:
            medalhaTotal += 1
            if medalha == "Gold":
                ouroTotal += 1
                continue
            if medalha == "Silver":
                prataTotal += 1
                continue
            bronzeTotal += 1
        dataFrameObject["ano"].append(ano)
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
                        dcc.Dropdown(
                            id="selectedYear",
                            options=[{"label": str(ano), "value": ano} for ano in anos],
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


@app.callback(
    Output(component_id="graph", component_property="figure"),
    [Input(component_id="selectedYear", component_property="value")],
)
def updateGraph(selectedYear):
    copy = dataFrameObject.copy()
    df = {
        "sigla": [],
        "Medalhas totais": [],
        "Medalhas totais": [],
        "Medalhas de ouro": [],
        "Medalhas de prata": [],
        "Medalhas de bronze": [],
    }

    for index in range(len(copy["ano"])):
        if copy["ano"][index] == selectedYear:
            df["sigla"].append(copy["sigla"][index])
            df["Medalhas totais"].append(copy["Medalhas totais"][index])
            df["Medalhas de ouro"].append(copy["Medalhas de ouro"][index])
            df["Medalhas de prata"].append(copy["Medalhas de prata"][index])
            df["Medalhas de bronze"].append(copy["Medalhas de bronze"][index])

    figure = px.choropleth(
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
        width=1200,
        height=675,
    )

    figure.update_geos(
        showocean=True,
        coastlinecolor="#610059",
        oceancolor="#b7ddf4",
        landcolor="#f7f8fa",
    )

    return figure


# ------------------------------------------------------------
# Running Server
# ------------------------------------------------------------
app.run_server()

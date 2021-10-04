from math import isnan #Is Not A Number
from dash.dependencies import Input, Output

from pandas import read_csv
import plotly.express as px
from dash import Dash
import dash_html_components as html
import dash_core_components as dcc

dados = read_csv("athlete_events.csv", delimiter = ",") #ler dados

# "ID"[0],
# "Name"[1],
# "Sex"[2],
# "Age"[3],
# "Height"[4],
# "Weight"[5],
# "Team"[6],
# "NOC"[7],
# "Games"[8],
# "Year"[9],
# "Season"[10],
# "City"[11],
# "Sport"[12],
# "Event"[13],
# "Medal"[14]

dadosUnicosPorPessoa = []
idsLidosPorAno = {}

for linha in dados.values:
  if isnan(linha[4]) or isnan(linha[5]):
    continue

  id = linha[0] # Identificador Único
  nome = linha[1]
  altura = linha[4] / 100
  peso = linha[5]
  time = linha[6]
  ano = linha[9]

  if idsLidosPorAno.get(ano) == None:
    idsLidosPorAno[ano] = set()
  elif id in idsLidosPorAno[ano]:
    continue
  
  imc = peso/(altura**2)

  dadosUnicosPorPessoa.append({"nome": nome, "imc": imc, "ano": ano})
  idsLidosPorAno[ano].add(id)

dadosUnicosPorPessoa.sort(key=lambda item: item["imc"]) # Ordena o array de acordo com o imc

agrupadoPorAno = {}
for dado in dadosUnicosPorPessoa:
  ano = dado["ano"]
  nome = dado["nome"]
  imc = dado["imc"]

  if agrupadoPorAno.get(ano) == None:
    agrupadoPorAno[ano] = { "nome":[], "imc": []}
  
  agrupadoPorAno[ano]["nome"].append(nome)
  agrupadoPorAno[ano]["imc"].append(imc)

anos = list(agrupadoPorAno.keys())
anos.sort()

app = Dash(__name__)
app.layout = html.Div(
  children=[
    dcc.Dropdown(
      id="anoSelecionado",
      options=[{ "label": str(ano), "value": ano } for ano in anos],
      value=anos[0],
      style={"width": "100px"}
    ),
    dcc.RadioItems(
      id="ordemSelecionada",
      options=[
        {"label": "Decrescente", "value": "maior"},
        {"label": "Crescente", "value": "menor"}
      ],
      value="menor"
    ),
    dcc.Graph(
      id="grafico",
      figure=[]
    )
  ]
)

@app.callback(
  Output(component_id="grafico", component_property="figure"),
  [
    Input(component_id="anoSelecionado", component_property="value"), 
    Input(component_id="ordemSelecionada", component_property="value")
  ]
)
def atualizarGrafico(anoSelecionado, ordemSelecionada):
  df = agrupadoPorAno[anoSelecionado].copy()
  if ordemSelecionada == "menor":
    df["nome"] = df["nome"][0:10]
    df["imc"] = df["imc"][0:10]
  else:
    df["nome"] = df["nome"][::-1][0:10]
    df["imc"] = df["imc"][::-1][0:10]

  grafico = px.bar(df, x="nome", y="imc")
  return grafico

app.run_server()

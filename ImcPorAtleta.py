from math import isnan #Is Not A Number
from dash.dependencies import Input, Output

from pandas import read_csv
import plotly.express as px
from dash import Dash, html, dcc

from components import header as DefaultHeader

dados = read_csv("dados/athlete_events.csv", delimiter = ",") #ler dados

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

# Agrupaento dos dados
#------------------------------------------------------------
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
#------------------------------------------------------------

# Ordenação dos dados por IMC
#------------------------------------------------------------
dadosUnicosPorPessoa.sort(key=lambda item: item["imc"]) # Ordena o array de acordo com o imc
#------------------------------------------------------------

# Criação do DataFrame
#------------------------------------------------------------
dataFrameAgrupadoPorAno = {}
for dado in dadosUnicosPorPessoa:
  ano = dado["ano"]
  nome = dado["nome"]
  imc = dado["imc"]

  if dataFrameAgrupadoPorAno.get(ano) == None:
    dataFrameAgrupadoPorAno[ano] = { "nome":[], "imc": []}
  
  dataFrameAgrupadoPorAno[ano]["nome"].append(nome)
  dataFrameAgrupadoPorAno[ano]["imc"].append(imc)
#------------------------------------------------------------

# Ordenação dos anos de forma decrescente
#------------------------------------------------------------
anos = list(dataFrameAgrupadoPorAno.keys())
anos.sort(reverse=True) # Ordena os anos de forma decrescente
#------------------------------------------------------------

# Criação do layout (vizualização)
#------------------------------------------------------------
app = Dash(__name__)
app.layout = html.Div(
  className="container",
  children=[
    DefaultHeader,
    html.H1("IMC por Atleta"),
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
#------------------------------------------------------------

# Criação do callback (função que é chamada sempre que um dos inputs são alterados)
#------------------------------------------------------------
@app.callback(
  Output(component_id="grafico", component_property="figure"),
  [
    Input(component_id="anoSelecionado", component_property="value"), 
    Input(component_id="ordemSelecionada", component_property="value")
  ]
)
def atualizarGrafico(anoSelecionado, ordemSelecionada):
  df = dataFrameAgrupadoPorAno[anoSelecionado].copy()
  if ordemSelecionada == "menor":
    df["nome"] = df["nome"][0:10]
    df["imc"] = df["imc"][0:10]
  else:
    df["nome"] = df["nome"][::-1][0:10]
    df["imc"] = df["imc"][::-1][0:10]

  grafico = px.bar(df, x="nome", y="imc")
  return grafico
#------------------------------------------------------------

# Rodar o servidor
#------------------------------------------------------------
app.run_server(port=3003)
#------------------------------------------------------------
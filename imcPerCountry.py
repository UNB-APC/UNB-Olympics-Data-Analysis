from math import isnan
from functools import reduce
from dash.dependencies import Input, Output

from pandas import read_csv
import plotly.express as px

from dash import Dash
import dash_html_components as html
import dash_core_components as dcc

# Read data
csvDataFrame = read_csv('dados/athlete_events.csv', delimiter=',')
print(csvDataFrame)
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

# Group data by Year
# ------------------------------------------------------------
groupedByYear = {}
for cells in csvDataFrame.values:
  if isnan(cells[4]) or isnan(cells[5]):
    continue

  year = cells[9] # Ano
  team = cells[7] # Time
  height = cells[4]/100 # Centimeters to meters
  weight = cells[5] # Peso
  imc = weight/(height**2)

  if groupedByYear.get(year) == None:
    groupedByYear[year] = {}
  if groupedByYear[year].get(team) == None:
    groupedByYear[year][team] = []

  groupedByYear[year][team].append(imc)
# ------------------------------------------------------------

# List All Years
# ------------------------------------------------------------
years = list(groupedByYear.keys())
years.sort()
# ------------------------------------------------------------


# Create The Main DataFrame
# ------------------------------------------------------------
dataFrameObject = {'team':[], 'year':[], 'imcAverage': []}
for year in years:
  for team in groupedByYear[year]:
    imcSum = reduce(lambda acc, current: acc+current, groupedByYear[year][team])
    imcAverage = imcSum / len(groupedByYear[year][team])

    dataFrameObject['year'].append(year)
    dataFrameObject['team'].append(team)
    dataFrameObject['imcAverage'].append(imcAverage)
# ------------------------------------------------------------


# ------------------------------------------------------------
# Create Dash Vizualization
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
            html.H1('Olimpiadas'),
            html.Img(src="./assets/rigth-wings.svg"),
          ]
        )
      ]
    ),

    html.Main(
      children=[
        html.H1(
          "Média do IMC por país",
          className="title"
        ),

        html.Section(
          [
            dcc.Dropdown(
              id="selectedYear",
              options=[{ "label": str(year), "value": year } for year in years],
              value=years[0],
              style={'width': '100px'},
            ),

            dcc.Graph(
              id="graph",
              figure=[],
            ),
          ],
        ),
      ]
    )
  ],
)

colors = [
  "#FCB131",
  "#00A651",
]

@app.callback(
  Output(component_id="graph", component_property="figure"),
  [Input(component_id="selectedYear", component_property="value")]
)
def updateGraph(selectedYear):
  copy = dataFrameObject.copy()
  df = {"team":[], "imcAverage": []}

  for index in range(len(copy["year"])):
    if copy["year"][index] == selectedYear:
      df["team"].append(copy["team"][index])
      df["imcAverage"].append(copy["imcAverage"][index])

  figure = px.choropleth(
    df,
    locations="team",
    color="imcAverage",
    hover_name="team",
    color_continuous_scale=colors,
    width=1200,
    height=675,
  )

  layout = figure.layout
  layout["paper_bgcolor"] = "#F7F8FA"
  layout["plot_bgcolor"] = "#F7F8FA"

  return figure
#------------------------------------------------------------


# Running Server
# ------------------------------------------------------------
app.run_server()
# ------------------------------------------------------------

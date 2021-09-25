from math import isnan
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
  noc = cells[7] # ISO Country Value
  team = cells[6] # Team Name
  height = cells[4]/100 # Centimeters to meters
  weight = cells[5] # Peso
  imc = weight/(height**2)

  if groupedByYear.get(year) == None:
    groupedByYear[year] = {}
  if groupedByYear[year].get(noc) == None:
    groupedByYear[year][noc] = []

  groupedByYear[year][noc].append({"imc": imc, "team": team})
# ------------------------------------------------------------

# List All Years
# ------------------------------------------------------------
years = list(groupedByYear.keys())
years.sort()
# ------------------------------------------------------------


# Create The Main DataFrame
# ------------------------------------------------------------
dataFrameObject = {'team':[], 'year':[], 'imcAverage': [], 'noc': []}
for year in years:
  for noc in groupedByYear[year]:
    imcSum = 0
    for data in groupedByYear[year][noc]:
      imcSum += data["imc"]

    imcAverage = imcSum / len(groupedByYear[year][noc])

    dataFrameObject['year'].append(year)
    dataFrameObject['noc'].append(noc)
    dataFrameObject['team'].append(groupedByYear[year][noc][0]["team"])
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

            html.Div(
              className="graph-container",
              children=[
                dcc.Graph(
                  id="graph",
                  figure=[],
                ),

                html.Div(
                  className="notListedTeams",
                  children=[
                    html.H1("Times Não Listados"),
                    html.Table(
                      children=[
                        html.Thead(
                          children=[
                            html.Tr(
                              children=[
                                html.Th("Time"),
                                html.Th("Média do IMC")
                              ]
                            )
                          ]
                        ),
                        html.Tbody(
                          id="itemsTable",
                          children=[]
                        )
                      ]
                    )
                  ]
                ),
              ]
            )
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

ISOCountries = ["ABW","AFG","AGO","AIA","ALA","ALB","AND","ARE","ARG","ARM","ASM","ATA","ATF","ATG","AUS","AUT","AZE","BDI","BEL","BEN","BES","BFA","BGD","BGR","BHR","BHS","BIH","BLM","BLR","BLZ","BMU","BOL","BRA","BRB","BRN","BTN","BVT","BWA","CAF","CAN","CCK","CHE","CHL","CHN","CIV","CMR","COD","COG","COK","COL","COM","CPV","CRI","CUB","CUW","CXR","CYM","CYP","CZE","DEU","DJI","DMA","DNK","DOM","DZA","ECU","EGY","ERI","ESH","ESP","EST","ETH","FIN","FJI","FLK","FRA","FRO","FSM","GAB","GBR","GEO","GGY","GHA","GIB","GIN","GLP","GMB","GNB","GNQ","GRC","GRD","GRL","GTM","GUF","GUM","GUY","HKG","HMD","HND","HRV","HTI","HUN","IDN","IMN","IND","IOT","IRL","IRN","IRQ","ISL","ISR","ITA","JAM","JEY","JOR","JPN","KAZ","KEN","KGZ","KHM","KIR","KNA","KOR","KWT","LAO","LBN","LBR","LBY","LCA","LIE","LKA","LSO","LTU","LUX","LVA","MAC","MAF","MAR","MCO","MDA","MDG","MDV","MEX","MHL","MKD","MLI","MLT","MMR","MNE","MNG","MNP","MOZ","MRT","MSR","MTQ","MUS","MWI","MYS","MYT","NAM","NCL","NER","NFK","NGA","NIC","NIU","NLD","NOR","NPL","NRU","NZL","OMN","PAK","PAN","PCN","PER","PHL","PLW","PNG","POL","PRI","PRK","PRT","PRY","PSE","PYF","QAT","REU","ROU","RUS","RWA","SAU","SDN","SEN","SGP","SGS","SHN","SJM","SLB","SLE","SLV","SMR","SOM","SPM","SRB","SSD","STP","SUR","SVK","SVN","SWE","SWZ","SXM","SYC","SYR","TCA","TCD","TGO","THA","TJK","TKL","TKM","TLS","TON","TTO","TUN","TUR","TUV","TWN","TZA","UGA","UKR","UMI","URY","USA","UZB","VAT","VCT","VEN","VGB","VIR","VNM","VUT","WLF","WSM","YEM","ZAF","ZMB","ZWE"]
@app.callback(
  [Output(component_id="graph", component_property="figure"), Output(component_id="itemsTable", component_property="children")],
  [Input(component_id="selectedYear", component_property="value")]
)
def updateGraph(selectedYear):
  copy = dataFrameObject.copy()
  df = {"team":[], "imcAverage": [], "noc": []}

  for index in range(len(copy["year"])):
    if copy["year"][index] == selectedYear:
      df["noc"].append(copy["noc"][index])
      df["imcAverage"].append(copy["imcAverage"][index])
      df["team"].append(copy["team"][index])

  figure = px.choropleth(
    df,
    locations="noc",
    color="imcAverage",
    hover_name="team",
    color_continuous_scale=colors,
    width=1200,
    height=675,
  )

  layout = figure.layout
  layout["paper_bgcolor"] = "#F7F8FA"
  layout["plot_bgcolor"] = "#F7F8FA"

  notListedTeams = []
  for index in range(len(df["team"])):
    if df["noc"][index] not in ISOCountries:
      notListedTeams.append({"team": df["team"][index], "imcAverage": df["imcAverage"][index]})

  TrForEachNotListedTeam = [
    html.Tr(
      children=[
        html.Td(item["team"]),
        html.Td(f'{item["imcAverage"]:.2f}')
      ]
    ) for item in notListedTeams
  ]

  return [figure, TrForEachNotListedTeam]
#------------------------------------------------------------


# Running Server
# ------------------------------------------------------------
app.run_server()
# ------------------------------------------------------------

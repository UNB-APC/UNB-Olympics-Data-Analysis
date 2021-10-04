from math import isnan # função que verifica se a variavel é NaN (Not a Number)
from dash.dependencies import Input, Output # Input e Output do callback do Dash

from pandas import read_csv # função que lê o arquivo csv
import plotly.express as px # modulo que vamos usar para criar o gráfico

from dash import Dash, html, dcc # Dash para criar a tela, html para os elementos html e dcc para os componentes do Dash

csvDataFrame = read_csv('dados/athlete_events.csv', delimiter=',') # Leitura dos arquivos
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

# Agrupamento dos dados pelo ano
# ------------------------------------------------------------
nocIMCAgrupadoPorAno = {} # Dicionario que irá armazernar o NOC e o IMC agrupado por ano
idsLidosAgrupadoPorAno = {} # Dicionario que irá armazenar os ids lidos agrupado por ano
for linha in csvDataFrame.values: # Percorre por cada linha desse array de duas dimensões
  '''
  csvDataFrame.values -> É um array de duas dimensões
  [
    ["1","A Dijiang","M",24,180,80,"China","CHN","1992 Summer",1992,"Summer","Barcelona","Basketball","Basketball Men's Basketball",NA]
    ["2","A Lamusi","M",23,170,60,"China","CHN","2012 Summer",2012,"Summer","London","Judo","Judo Men's Extra-Lightweight",NA]
  ]
  '''
  idDoAtleta = linha[0]
  noc = linha[7] # Codigo ISO
  time = linha[6]
  altura = linha[4] # Altura em centimetros
  peso = linha[5]
  ano = linha[9]

  if isnan(altura) or isnan(peso): # Verifica se o peso ou a altura não é um número
    continue # Se caso um dos dois não for, ele pula essa linha do array

  if idsLidosAgrupadoPorAno.get(ano) == None: # Verifica se já existe um set para esse ano
    idsLidosAgrupadoPorAno[ano] = set() # Se caso não, ele cria um para o ano
  elif idDoAtleta in idsLidosAgrupadoPorAno[ano]: # Se caso já existir, ele verifica se o id está nesse set
    continue # Se caso estiver, ele pula essa linha do array

  if nocIMCAgrupadoPorAno.get(ano) == None: # Verifica se já existe um dict para esse ano
    nocIMCAgrupadoPorAno[ano] = {} # Se não, ele cria um dict vazio para o ano
  if nocIMCAgrupadoPorAno[ano].get(noc) == None: # Verifica se já existe um array para esse NOC
    nocIMCAgrupadoPorAno[ano][noc] = [] # Se não, ele cria um array vazio para esse NOC

  imc = peso/((altura/100)**2) # Calcula o IMC
  nocIMCAgrupadoPorAno[ano][noc].append({"imc": imc, "time": time}) # Adiciona um dict com imc e time no array
  idsLidosAgrupadoPorAno[ano].add(idDoAtleta) # No final de tudo ele adiciona esse id no set de ids
# ------------------------------------------------------------


# Listamento de todos os anos
# ------------------------------------------------------------
anos = [ano for ano in nocIMCAgrupadoPorAno] # Cria um array de anos para cada ano dentro do dict de dados agrupados por ano
anos.sort() # Ordena de forma crescente esses anos
# ------------------------------------------------------------


# Criação e agrupamento dos DataFrame que serão usado no grafico
# ------------------------------------------------------------
dataFrameAgrupadoPorAno = {} # Cria um dicionario para armazenar os dataframes agrupados por ano
for ano in anos: # Percorre todos os anos do array de anos
  for noc in nocIMCAgrupadoPorAno[ano]: # Percorre todos os NOCs desse agrupamento de IMC do ano
    somaDosIMC = 0
    for dado in nocIMCAgrupadoPorAno[ano][noc]: # Percorre todos os items do array nocIMCAgrupadoPorAno[ano][noc]  ->  {"imc": 0, "time": "BRA"}
      somaDosIMC += dado["imc"]

    mediaImc = somaDosIMC / len(nocIMCAgrupadoPorAno[ano][noc])

    if dataFrameAgrupadoPorAno.get(ano) == None: # Verifica se já existe um dataframe para esse ano
      dataFrameAgrupadoPorAno[ano] = {'time':[], 'ano':[], 'mediaImc': [], 'noc': []} # Se não existir, ele cria um dataframe para o ano 
    
    # As linhas abaixo adicionam cada dado ao seu respectivo array do ano
    dataFrameAgrupadoPorAno[ano]['ano'].append(ano)
    dataFrameAgrupadoPorAno[ano]['noc'].append(noc)
    dataFrameAgrupadoPorAno[ano]['time'].append(dado["time"])
    dataFrameAgrupadoPorAno[ano]['mediaImc'].append(mediaImc)
# ------------------------------------------------------------


# Criação o layout do Dash, onde vai ter o gráfico
# ------------------------------------------------------------
app = Dash(__name__) # Inicializa a tela do Dash

app.layout = html.Div( # Cria uma div (elemento html), como elemento raiz do layout 
  className="container-imc-per-country", # Define uma classe para a estilização no css
  children=[ # Define os elementos filhos
    html.Header( # Cria um Header (elemento html) para o site
      children=[ # Define os elementos filhos
        html.Img(src="./assets/logo.svg"), # Cria uma img (elemento html) para mostar a logo das olimpiadas
        html.Div( # Cria uma div (elemento html) para agrupar imagens com texto e formar um elemento só
          children=[ # Define os elementos filhos
            html.Img(src="./assets/left-wings.svg"), # Cria uma img (elemento html) para uma "asa" da logo
            html.H1('Olimpiadas'), # Cria um h1 (elemento html) para colocarmos o título da logo
            html.Img(src="./assets/rigth-wings.svg"), # Cria uma img (elemento html) para outra "asa" da logo
          ]
        )
      ]
    ),

    html.Main( # Cria uma main (elemento html) para criarmos o layout principal
      children=[ # Determina os filhos do elemento main
        html.H1( # Cria um h1 para colocarmos um titulo para o grafico
          "Média do IMC por país", # Valor do texto do h1
          className="title" # Classe para estilizarmos no css
        ),

        html.Section( # Cria uma section (elemento html), para criarmos um local para os elementos do grafico
          children=[ # Determina os filhos do elemento section
            dcc.Dropdown( # Cria um componente Dropdown do Dash 
              id="anoSelecionado", # Determina um id para o callback do Dash encontrar o elemento
              options=[{ "label": str(ano), "value": ano } for ano in anos], # Para cada ano do array de anos, ele cria uma opção
              value=anos[0], # Determina o valor inicial como o primeiro elemento do array de anos
              style={'width': '100px'}, # Determina a largura do dropdown, apenas estilização
            ),

            html.Div( # Cria uma div (elemento html) para colocarmos o grafico e a tabela dos times nao listados
              className="graph-container", # Define uma classe para estilizarmos no css
              children=[ # Define os elementos filhos
                dcc.Graph( # Cria o componente de grafico do Dash
                  id="grafico", # Define um id para o componenete para o callback encontrar o elemento
                  figure=px.choropleth(), # Define um grafico inicial, vazio, que será alterado de acordo com o usuário
                ),

                html.Div( # Cria uma div (elemento html) para a tabela dos times não listados
                  className="notListedTeams", # Determina uma classe para a estilização no css
                  children=[ # Define os elementos filhos
                    html.H1("Times Não Listados"), # Cria um h1 (elemento html) para o titulo da tabela
                    html.Table( # Cria uma table (elemento html) para a tabela
                      children=[ # Define os elementos filhos
                        html.Thead( # Cria um thead (elemento html) para o cabeçalho da tabela
                          children=[ # Define os elementos filhos
                            html.Tr( # Cria uma tr (elemento html) para criar uma linha para o cabeçalho
                              children=[ # Define os filhos do elemento tr
                                html.Th("Time"), # Cria th (elemento html) para o titulo chamado "Time" para o cabeçalho
                                html.Th("Média do IMC") # Cria th (elemento html) para o titulo chamado "Média do IMC" para o cabeçalho
                              ]
                            )
                          ]
                        ),
                        html.Tbody( # Cria um tbody (elemento html) para os itens da tabela
                          id="itensDaTabela", # Define um id para o callback encontrar o elemento
                          children=[] # Define os elementos filhos como um array vazio para ser alterado de acordo com o usuário
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

cores = [ # Array com as cores para a medição do gráfico
  "#FCB131",
  "#00A651",
]

#Array de codigos ISO aceitos pelo Dash
codigosISO = ["ABW","AFG","AGO","AIA","ALA","ALB","AND","ARE","ARG","ARM","ASM","ATA","ATF","ATG","AUS","AUT","AZE","BDI","BEL","BEN","BES","BFA","BGD","BGR","BHR","BHS","BIH","BLM","BLR","BLZ","BMU","BOL","BRA","BRB","BRN","BTN","BVT","BWA","CAF","CAN","CCK","CHE","CHL","CHN","CIV","CMR","COD","COG","COK","COL","COM","CPV","CRI","CUB","CUW","CXR","CYM","CYP","CZE","DEU","DJI","DMA","DNK","DOM","DZA","ECU","EGY","ERI","ESH","ESP","EST","ETH","FIN","FJI","FLK","FRA","FRO","FSM","GAB","GBR","GEO","GGY","GHA","GIB","GIN","GLP","GMB","GNB","GNQ","GRC","GRD","GRL","GTM","GUF","GUM","GUY","HKG","HMD","HND","HRV","HTI","HUN","IDN","IMN","IND","IOT","IRL","IRN","IRQ","ISL","ISR","ITA","JAM","JEY","JOR","JPN","KAZ","KEN","KGZ","KHM","KIR","KNA","KOR","KWT","LAO","LBN","LBR","LBY","LCA","LIE","LKA","LSO","LTU","LUX","LVA","MAC","MAF","MAR","MCO","MDA","MDG","MDV","MEX","MHL","MKD","MLI","MLT","MMR","MNE","MNG","MNP","MOZ","MRT","MSR","MTQ","MUS","MWI","MYS","MYT","NAM","NCL","NER","NFK","NGA","NIC","NIU","NLD","NOR","NPL","NRU","NZL","OMN","PAK","PAN","PCN","PER","PHL","PLW","PNG","POL","PRI","PRK","PRT","PRY","PSE","PYF","QAT","REU","ROU","RUS","RWA","SAU","SDN","SEN","SGP","SGS","SHN","SJM","SLB","SLE","SLV","SMR","SOM","SPM","SRB","SSD","STP","SUR","SVK","SVN","SWE","SWZ","SXM","SYC","SYR","TCA","TCD","TGO","THA","TJK","TKL","TKM","TLS","TON","TTO","TUN","TUR","TUV","TWN","TZA","UGA","UKR","UMI","URY","USA","UZB","VAT","VCT","VEN","VGB","VIR","VNM","VUT","WLF","WSM","YEM","ZAF","ZMB","ZWE"]

@app.callback( # Define um callback, uma função que é chamada sempre que o input é alterado
  [
    Output(component_id="grafico", component_property="figure"), # Define o primeiro output, que é a propriedade "figure" do elemento com id = "grafico"
    Output(component_id="itensDaTabela", component_property="children") # Define o segundo output, que é a propriedade "children" do elemento com id = "itensDaTabela"
  ],
  [Input(component_id="anoSelecionado", component_property="value")] # Define o input, que é a propriedade "value" do elemento com id = "selectedYear"
)
def atualizarGrafico(anoSelecionado): # Função que atualiza o grafico, será chamada sempre que o ano selecionado for alterado
  df = dataFrameAgrupadoPorAno[anoSelecionado]

  grafico = px.choropleth(
    df,
    locations="noc",
    color="mediaImc",
    hover_name="time",
    color_continuous_scale=cores,
    width=1200,
    height=675,
  )

  layout = grafico.layout
  layout["paper_bgcolor"] = "#F7F8FA"
  layout["plot_bgcolor"] = "#F7F8FA"

  timesNaoListados = []
  for index in range(len(df["time"])):
    if df["noc"][index] not in codigosISO:
      timesNaoListados.append({"time": df["time"][index], "mediaImc": df["mediaImc"][index]})

  TrParaCadaTimeNaoListado = [ # Cria um Tr para cada item dentro do array timesNaoListados
    html.Tr( # Cria um Tr (elemento html) para criar uma linha para a tabela
      children=[ # Determina os elementos filhos da tr
        html.Td(item["time"]), # Cria uma coluna que vai ter o time
        html.Td(f'{item["mediaImc"]:.2f}') # Cria uma coluna que vai ter a media do Imc
      ]
    ) for item in timesNaoListados
  ]

  return [grafico, TrParaCadaTimeNaoListado] # Retorna em ordem para os outputs, o grafico e os itens da tabela
#------------------------------------------------------------


# Running Server
# ------------------------------------------------------------
app.run_server() # Roda o servidor "Flask" do Dash
# ------------------------------------------------------------

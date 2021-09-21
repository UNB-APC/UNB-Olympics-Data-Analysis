from pandas import read_csv
from pandas.core.frame import DataFrame #importação do leitor de dados

dados = read_csv("dados/athlete_events.csv", delimiter = ",")

agruparporano = {}

for linha in dados.values: #atribuir sexo aos anos 
    ano = linha[9]
    sexo = linha[2]
    if agruparporano.get(ano) == None:
        agruparporano[ano] = []
    agruparporano[ano].append(sexo)

anos = list(agruparporano.keys())
anos.sort()
DataFrame = {"Ano":[], "Homens":[], "Mulheres":[]}

for ano in anos:
    male = 0
    female = 0
    for sexo in agruparporano[ano]:
        if sexo == "M":
            male += 1
            continue
        female += 1
        DataFrame["Ano"].append(ano)
        DataFrame["Homens"].append(male)
        DataFrame["Mulheres"].append(female)
    print(ano, male, female)
        
        
           

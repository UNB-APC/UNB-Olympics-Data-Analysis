from dash import html

header = html.Header(
  children=[
    html.Img(src="./assets/logo.svg"),
      html.Div(
        children=[
        html.Img(src="./assets/left-wings.svg"),
        html.H1("Olimpiadas"),
        html.Img(src="./assets/rigth-wings.svg"),
        ]
      )
  ]
)

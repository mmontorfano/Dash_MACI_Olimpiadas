from dash import Dash, Input, Output, dcc, html
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

data = pd.read_csv("olimpiadas.csv")
data = data.dropna(subset=['Weight', 'Height','Age'])


def sex(df, season):
    return df[df['Season'] == season].groupby(['Year', 'Sex'])['Sex'].count().unstack()

def plot_timeline(df, season):
    timeline = px.line(
        data_frame=sex(df, season),
        x=sex(df, season).index,
        y=['F', 'M'])
    return timeline

app = Dash(__name__)
server = app.server

app.layout = dbc.Container(
    children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Tendencia de Participación Hombres y Mujeres en Olimpiadas"),
                        dcc.Graph(id="id_timeline", figure=plot_timeline(data,"Summer")),
                        dcc.RadioItems( 
                            id='season-radio',
                            options=[{'label': 'Winter', 'value': 'Winter'},
                                     {'label': 'Summer', 'value': 'Summer'}],
                            value='Summer'
                        )
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.H1("Tendencia de Participación Hombres y Mujeres en Olimpiadas"),
                        
                      
                    ]
                ),
            ]
        ),
    ],
    fluid=True,
)

@app.callback(Output('id_timeline', 'figure'),
              [Input('season-radio', 'value')])

def update_timeline(season):
    df = sex(data, season)
    fig = px.line(data_frame=df, x=df.index, y=['F', 'M'], title=f"Medallas por género en la temporada {season}")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port="5000")

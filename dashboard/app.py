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

def burbujas(df, season):
    data1 = df[df['Season']==season].groupby('Sport').agg({"ID":"count", "Height": "mean","Weight":"mean", "Age":"mean" })
    data1['IMC'] = data1['Weight'] / ((data1['Height']/100)**2)
    return data1

def plot_burbujas(df, season):
    scatter = px.scatter(
        data_frame=burbujas(df, season),
        x='IMC', 
        y='Age', 
        size='ID',
        color= burbujas(df, season).index,
        hover_name=burbujas(df, season).index,
        size_max=50)
    return scatter

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
                    width=7,
                ),
                dbc.Col(
                    [
                      html.H1("Cositar olimpiadas"),
                      dcc.Graph(id="id_burbujas", figure=plot_burbujas(data,"Summer")),
                    ]
                ),
            ]
        ),
    ],
)

@app.callback(Output('id_timeline', 'figure'),
              [Input('season-radio', 'value')])

def update_season(season):
    timeline = plot_timeline(data, season)
    burbujas = plot_burbujas(data, season)
    return timeline, burbujas

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port="5000")

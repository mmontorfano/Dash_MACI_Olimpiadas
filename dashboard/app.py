from dash import Dash, Input, Output, dcc, html
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from plotly.offline import iplot
import plotly.figure_factory as ff

# Cargar el conjunto de datos
data = pd.read_csv("athlete_events.csv")
data = data.dropna(subset=['Weight', 'Height','Age'])
data_region = pd.read_csv("noc_regions.csv")

def world(df, df2, season):
    data = pd.merge(df, df2, on='NOC', how='left')
    summer_gold_df = data.loc[(data['Season'] == season) & (data['Medal'] == 'Gold')]
    gold_medals_df = summer_gold_df.groupby(['Year', 'region', 'Event']).agg({'Medal': 'count'}).reset_index()
    gold_medals_df['Gold Medals'] = gold_medals_df['Medal'] >= 1
    gold_medals_by_region_df = gold_medals_df.groupby(['Year', 'region']).agg({'Gold Medals': 'sum'}).reset_index()
    return gold_medals_by_region_df

def plot_world(df):
    geo_world = px.scatter_geo(df, locations='region', locationmode='country names', size='Gold Medals', color='Gold Medals', projection='natural earth', animation_frame='Year')
    return geo_world

def medal(df, df2, pais, season):
    dt = pd.merge(df, df2, on='NOC', how='left')
    medals = pd.get_dummies(dt['Medal'])
    dt = pd.concat([dt, medals], axis=1)
    dt = dt[dt['Season'] == season]
    country = pais
    table = pd.pivot_table(dt[dt['region'] == country], values=['Gold', 'Silver', 'Bronze'], index=['ID', 'Name'], aggfunc=sum, fill_value=0)
    table['Total'] = table.sum(axis=1)
    top_10 = table.sort_values(by=['Gold', 'Silver', 'Bronze'], ascending=[False, False, False]).head(10)
    top_10 = top_10.iloc[::-1]
    return top_10[['Gold', 'Silver', 'Bronze']].reset_index().melt(id_vars=['ID', 'Name'], value_vars=['Gold', 'Silver', 'Bronze'], var_name='Medal', value_name='Count')

def plot_medallero(df,pais):
    colors = {'Gold': '#ffd700', 'Silver': '#c0c0c0', 'Bronze': '#cd7f32'}
    medallero = px.bar(df, 
                        x='Count', 
                        y='Name', 
                        orientation='h', 
                        color='Medal', 
                        color_discrete_map=colors, 
                        title=f'Top 10 {pais} Athletes with the Most Olympic Medals')
    return medallero
 

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

def imc(df):
    df['IMC'] = df['Weight'] / ((df['Height']/100)**2)
    return df

#def histograma_imc(df):
#    fig = px.histogram(data_frame=imc(df), x='IMC', color='Sex', nbins=50, marginal='rug',
#                        labels={'IMC': 'Indice de Masa Corporal (IMC)'}, 
#                        title='Distribución del IMC para Hombres y Mujeres')
#    return fig

def histograma_imc(df):

    female_h = df[df['Sex']=='F']['IMC'].dropna()
    male_h = df[df['Sex']=='M']['IMC'].dropna()

    hist_data = [female_h, male_h]
    group_labels = ['Female IMC', 'Male IMC']

    fig = ff.create_distplot(hist_data, group_labels, show_hist=True, show_rug=False)
    fig['layout'].update(title='Athlets IMC distribution plot')
    return fig

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container(
    children=[
            dbc.Row(dbc.Col(html.H1("Dashboard analítico de Olimpiadas (120 años)", style={"textAlign": "center","color": "blue"}))),                             # titulo
            dbc.Row(dbc.Col(html.H1("Descripcion de dataframe y objetivo del dashhboard", style={"textAlign": "center","color": "black","font-size": "20px"}))),  # detalle de objetivo del dashhboard
    
            dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H1("Mapa coropletico", style={"textAlign": "center","color": "black","font-size": "20px"}),
                                dcc.Graph(id="id_geoworld", figure=plot_world(world(data, data_region, "Summer")))
                            
                            ],
                            width=7,
                        ),
                        dbc.Col(
                            [
                            html.H1("Cositar olimpiadas", style={"textAlign": "center","color": "black","font-size": "20px"}),
                            dcc.Graph(id="id_medallero", figure=plot_medallero(medal(data,data_region,"Argentina","Summer"), "Argentina")),
                            ]
                        ),
                    ]
                ),
    
            dbc.Row(
                    [
                        
                        dbc.Col(
                            [
                            html.H1("Cositar olimpiadas", style={"textAlign": "center","color": "black","font-size": "20px"}),
                            dcc.Graph(id="id_burbujas", figure=plot_burbujas(data,"Summer")),
                            ]
                        ),

                        dbc.Col(
                            [
                                html.H1("Tendencia de Participación Hombres y Mujeres en Olimpiadas", style={"textAlign": "center","color": "black","font-size": "20px"}),
                                dcc.Graph(id="id_boxplot", figure=histograma_imc(imc(data))),
                            
                            ],
                            width=4,
                        ),
                        
                    ]
                ),
                
            dbc.Row(
                [
                    dbc.Col(
                            [
                                html.H1("Tendencia de Participación Hombres y Mujeres en Olimpiadas", style={"textAlign": "center","color": "black","font-size": "20px"}),
                                dcc.Graph(id="id_boxplot", figure=histograma_imc(imc(data))),
                            
                            ],
                            width=4,
                        ),

                    dbc.Col(
                            [
                                html.H1("Tendencia de Participación Hombres y Mujeres en Olimpiadas", style={"textAlign": "center","color": "black","font-size": "20px"}),
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
                ]
            ),
    ],
)

@app.callback(
            [Output('id_timeline', 'figure'),
            Output('id_medallero', 'figure'),
            Output('id_burbujas', 'figure'),
            Output('id_geoworld', 'figure')],
            [Input('season-radio', 'value')])

def update_season(season):
    timeline = plot_timeline(data, season)
    medallero = plot_medallero(medal(data, data_region, "Argentina", season), "Argentina")
    burbujas = plot_burbujas(data, season)
    geo_world = plot_world(world(data, data_region, season))
    return timeline, medallero, burbujas, geo_world

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port="5000")

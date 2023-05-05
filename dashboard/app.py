from dash import Dash, Input, Output, dcc, html
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from plotly.offline import iplot
import plotly.figure_factory as ff
import plotly.graph_objs as go
from plotly import tools
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)
import plotly.express as px

# Cargar el conjunto de datos
data = pd.read_csv("athlete_events.csv")
data = data.dropna(subset=['Weight', 'Height','Age'])
data_region = pd.read_csv("noc_regions.csv")
paises_unicos = sorted(data_region['region'].dropna().unique().tolist())


def world(df, df2, season, medalla):
    data = pd.merge(df, df2, on='NOC', how='left')
    summer_gold_df = data.loc[(data['Season'] == season) & (data['Medal'] == medalla)]
    gold_medals_df = summer_gold_df.groupby(['Year', 'region', 'Event']).agg({'Medal': 'count'}).reset_index()
    gold_medals_df['N° Medals'] = gold_medals_df['Medal'] >= 1
    gold_medals_by_region_df = gold_medals_df.groupby(['Year', 'region']).agg({'N° Medals': 'sum'}).reset_index()
    return gold_medals_by_region_df

def plot_world(df):
    geo_world = px.choropleth(df, locations='region', locationmode='country names', color='N° Medals', projection='equirectangular', animation_frame='Year')
    geo_world.update_layout(
        height=450,
        width=750,
        paper_bgcolor='#F4FAFD'
    )
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
                        ).update_layout(xaxis_title="N° de medallas", yaxis_title="Deportista", legend=dict(orientation='h',yanchor="bottom", y=1.02, xanchor="right",x=1),xaxis=dict(tickmode='linear', dtick=1, tickfont=dict(size=10)))
    medallero.update_layout(paper_bgcolor='#F4FAFD')
    return medallero


def sex(df, season):
    return df[df['Season'] == season].groupby(['Year', 'Sex'])['Sex'].count().unstack()

def plot_timeline(df, season):
    etiquetas = {'F': 'Femenino', 'M': 'Masculino'}
    timeline = px.line(
        data_frame=sex(df, season),
        x=sex(df, season).index,
        y=['F', 'M']
        , width=650, height=550).update_layout(xaxis_title="Años", yaxis_title="Cantidad de participantes",legend_orientation='h')
    timeline.update_layout(paper_bgcolor='#D5E0E0')
    timeline.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
    ))
    timeline['data'][0]['line']['color']='#AE62B5'
    timeline['data'][1]['line']['color']='#40704E'
    timeline.for_each_trace(lambda t: t.update(name = etiquetas[t.name],
                                      legendgroup = etiquetas[t.name],
                                      hovertemplate = t.hovertemplate.replace(t.name, etiquetas[t.name])
                                     ))
    return timeline

def burbujas(df, season):
    data1 = df[df['Season']==season].groupby('Sport').agg({"ID":"count", "Height": "mean","Weight":"mean", "Age":"mean" })
    return data1

def plot_burbujas(df, season):
    scatter = px.scatter(
        data_frame=burbujas(df, season),
        x='Weight',
        y='Height',
        size='ID',
        color= burbujas(df, season).index,
        hover_name=burbujas(df, season).index,
        size_max=50).update_layout(xaxis_title="Peso", yaxis_title="Altura")
    scatter.update_layout(paper_bgcolor='#D1ECFA')
    return scatter

def imc(df):
    df['IMC'] = df['Weight'] / ((df['Height']/100)**2)
    return df

def dis_olim(df,season, sport):
    etiquetas = {'F': 'Femenino', 'M': 'Masculino'}
    dff = df[(df['Season'] == season) & (df['Sport'] == sport)]
    dff = dff.sort_values(by='Year', ascending=False)
    fig = px.histogram(dff, x='Age',color='Sex', animation_frame='Year', nbins=30,color_discrete_map = {'F':'#AE62B5','M':'#40704E'}, width=600, height=550)
    fig.update_layout(paper_bgcolor='#D5E0E0',xaxis_title="Edad", yaxis_title="Cantidad de participantes")
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1))
    fig.for_each_trace(lambda t: t.update(name = etiquetas[t.name],
                                      legendgroup = etiquetas[t.name],
                                      hovertemplate = t.hovertemplate.replace(t.name, etiquetas[t.name])
                                     ))
    return fig

def sports_season(data, season):
    deportes_season = data[data['Season']==season]['Sport'].unique().tolist()
    return sorted(deportes_season)


def deportes(df):
    sports = (df.groupby(['Sport'])['Sport'].nunique()).index
    return sports


def draw_boxplot(df,season):
   df_S = df[df['Season']==season]
   fig = px.box(df_S, x="Age", y="Sport", color="Season", orientation="h")
   fig.update_layout(
       xaxis_title="Edad",
       yaxis_title="Deporte",
       font=dict(
           family="Old Standard TT, serif",
           size=12,
           color="black"
       ),
       height=600,
   )
   fig.update_layout(paper_bgcolor='#D1ECFA',showlegend=False)
   return fig


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container(
    children=[
            dbc.Row(
                    [

                        dbc.Col(
                            [
                            html.H1(".", style={"textAlign": "left","color": "#337BA0","font-size": "5px"}),
                            html.H1("Dashboard analítico de Olimpiadas", style={"textAlign": "center","color": "white","font-size": "50px"}),
                            html.H1("Enfocado en amantes de la historia deportiva y escolares interesados en datos relevantes de los JJ.OO", style={"textAlign": "center","color": "white","font-size": "18px"}),

                            ],width=6,
                            style={"background-color": "#337BA0"}

                        ),

                        dbc.Col(
                            [
                            html.H1(".", style={"textAlign": "left","color": "#337BA0","font-size": "5px"}),
                            html.H1("Visualización de análisis de set de datos históricos de los Juegos Olimpicos desde Atenas 1896 a Rio 2016 ", style={"textAlign": "left","color": "white","font-size": "18px"}),
                            html.H1("Se debe escoger la temporada en la cual se desarrollo el juego olímpico", style={"textAlign": "left","color": "white","font-size": "18px"}),
                            dcc.Dropdown(
                                    id='season-radio',
                                    options=[{'label': 'Summer', 'value': 'Summer'},
                                            {'label': 'Winter', 'value': 'Winter'}],
                                    value='Summer',
                                    style={'width': '300px'}
                                        ),
                            html.H1(".", style={"textAlign": "left","color": "#337BA0","font-size": "5px"}),
                            ],width=6,                 
                            style={"background-color": "#337BA0"}
                        ),

                    ]
                ),
            dbc.Row(
                    [
                        
                        dbc.Col(
                            [
                           html.H1("Distribución de medallas por el mundo",style={"textAlign": "left","color": "black","font-size": "25px","border-bottom": "1px solid black", "padding": "1px"}),
                            html.H1("Medallas por el mundo a través del tiempo ", style={"textAlign": "left","color": "black","font-size": "18px"}),
                            html.H1("Escoger el tipo de medalla para ver su evolución en el tiempo ", style={"textAlign": "left","color": "black","font-size": "12px"}),
                            dcc.RadioItems(
                                    id='medalla-radio',
                                    options=[{'label': 'Gold  ', 'value': 'Gold'},
                                            {'label': 'Silver  ', 'value': 'Silver'},
                                            {'label': 'Bronze', 'value': 'Bronze'}],
                                    value='Gold',
                                    inline=True),
                            dcc.Graph(id="id_geoworld", figure=plot_world(world(data, data_region, "Summer","Gold")))

                            ],width=4,
                            style={"border-bottom": "1px solid black", "padding": "10px","background-color": "#F4FAFD"}
    
                            
                        ),

                        dbc.Col(
                            [
                            html.H1(".", style={"textAlign": "left","color": "#F4FAFD","font-size": "25px","border-bottom": "1px solid black", "padding": "1px"}),
                            html.H1("Medallero histórico Top 10 por país",style={"textAlign": "left","color": "black","font-size": "18px"}),
                            html.H1("Escoger el pais para visualizar su medallero ", style={"textAlign": "left","color": "black","font-size": "12px"}),
                            dcc.Dropdown(
                                    id='id_dropdown',
                                    options=paises_unicos,
                                    value="USA"),
                            dcc.Graph(id="id_medallero", figure=plot_medallero(medal(data,data_region,"Argentina","Summer"), "Argentina")),
                            ],width=4,
                            style={"border-bottom": "1px solid black", "padding": "10px","background-color": "#F4FAFD"}
                            
                        ),
                        dbc.Col(
                            [
                            html.H1("Comparativos entre deportes", style={"textAlign": "left","color": "black","font-size": "25px","border-bottom": "1px solid black", "padding": "1px"}),
                            html.H1("Comparación de peso, altura y N° de participantes", style={"textAlign": "left","color": "black","font-size": "18px"}),

                                dcc.Graph(id="id_burbujas", figure=plot_burbujas(data,"Summer")),
                            ],width=4,
                            style={"border-left": "1px solid black", "padding": "10px","background-color": "#D1ECFA"}
                            
                        ),


                    ]
                ),


            dbc.Row(
                    [
                        dbc.Col(
                            [
                            html.H1("Participación de género", style={"textAlign": "left","color": "black","font-size": "25px","border-bottom": "1px solid black", "padding": "1px"}),
                            html.H1("Evolución de participación", style={"textAlign": "left","color": "black","font-size": "18px"}),
                            dcc.Graph(id="id_timeline", figure=plot_timeline(data,"Summer")),
                            ],
                            width=4,
                            style={"background-color": "#D5E0E0"}
                        ),
                        dbc.Col(
                                [
                                html.H1(".", style={"textAlign": "left","color": "#D5E0E0","font-size": "25px","border-bottom": "1px solid black", "padding": "1px"}),
                                html.H1("Distribución de edad por deporte y género", style={"textAlign": "left","color": "black","font-size": "18px"}),
                                html.H1("Escoger el deporte que desea analizar ", style={"textAlign": "left","color": "black","font-size": "15px"}),
                                dcc.Dropdown(
                                    id='id_dropdown_deporte', 
                                    options=sports_season(data,"Summer"),
                                    value="Football"
                                ),
                                dcc.Graph(id="id_histograma", figure=dis_olim(data,'Summer','Football')),

                                ],
                                width=4,
                                style={"background-color": "#D5E0E0"}
                            ),

                        dbc.Col(
                            [
                            html.H1("Comparación de distribución de edad participantes", style={"textAlign": "left","color": "black","font-size": "18px"}),
                            dcc.Graph(id="id_boxplot", figure=draw_boxplot(data,"Summer")),
                            ],
                            width=4,
                            style={"border-left": "1px solid black", "padding": "10px","background-color": "#D1ECFA"}
                            
                        ),
                    ]
                ),

    ],
    fluid=True,
)

@app.callback(
    [Output('id_timeline', 'figure'),
     Output('id_medallero', 'figure'),
     Output('id_burbujas', 'figure'),
     Output('id_geoworld', 'figure'),
     Output('id_boxplot', 'figure'),
     Output('id_histograma', 'figure'),
     Output('id_dropdown_deporte', 'options')],
    [Input('season-radio', 'value'),
     Input('id_dropdown', 'value'),
     Input('medalla-radio', 'value'),
     Input('id_dropdown_deporte', 'value')])

def update(season, pais, medalla,sports):
    timeline = plot_timeline(data, season)
    medallero = plot_medallero(medal(data, data_region, pais, season), pais)
    burbujas = plot_burbujas(data, season)
    geo_world = plot_world(world(data, data_region, season, medalla))
    boxplot = draw_boxplot(data, season)
    histograma = dis_olim(data,season,sports)
    dropdown = sports_season(data, season) 
    return timeline, medallero, burbujas, geo_world, boxplot,histograma, dropdown
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port="8000")

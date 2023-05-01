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
paises_unicos = data_region['region'].unique().tolist()

def world(df, df2, season, medalla):
    data = pd.merge(df, df2, on='NOC', how='left')
    summer_gold_df = data.loc[(data['Season'] == season) & (data['Medal'] == medalla)]
    gold_medals_df = summer_gold_df.groupby(['Year', 'region', 'Event']).agg({'Medal': 'count'}).reset_index()
    gold_medals_df['N° Medals'] = gold_medals_df['Medal'] >= 1
    gold_medals_by_region_df = gold_medals_df.groupby(['Year', 'region']).agg({'N° Medals': 'sum'}).reset_index()
    return gold_medals_by_region_df

def plot_world(df):
    #geo_world = px.choropleth(df, locations='region', locationmode='country names', size='N° Medals', color='N° Medals', projection='natural earth', animation_frame='Year', title=f'Distribución de medallas por año')
    geo_world = px.choropleth(df, locations='region', locationmode='country names', color='N° Medals', projection='natural earth', animation_frame='Year', title=f'Distribución de medallas por año')  
    geo_world.update_layout(
        height=800,
        width=1000,
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
                        title=f'Medallero olímpico Top 10 {pais} ')
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
    fig['layout'].update(title='Distribución de IMC de atletas')
    return fig

def deportes(df):
    sports = (df.groupby(['Sport'])['Sport'].nunique()).index
    return sports

def draw_trace(dataset, sport):
    df = dataset[dataset['Sport']==sport];
    trace = go.Box(
        x = df['Age'],
        name=sport,
        marker=dict(
                    line=dict(
                    color='black',
                    width=0.8),
                ),
        text=df['City'], 
        orientation = 'h'
    )
    return trace

def draw_group(df,season,height=800):
    df_S = df[df['Season']==season]
    tmp = df_S.groupby(['Year', 'City','Season', 'Age'])['Sport'].value_counts()
    df1 = pd.DataFrame(data={'Athlets': tmp.values}, index=tmp.index).reset_index()
    data = list()
    sports = deportes(df_S)
    sports=sorted(sports, reverse=True)
    
    for sport in sports:
        data.append(draw_trace(df1, sport))


    layout = dict(title = "Edad de atletas por deporte" ,
              xaxis = dict(title = 'Edad',showticklabels=True),
              yaxis = dict(title = 'Deporte'+' '+season, showticklabels=True, tickfont=dict(
                family='Old Standard TT, serif',
                size=8,
                color='black'),), 
              hovermode = 'closest',
              showlegend=False,
                  width=600,
                  height=height,
             )
    fig = dict(data=data, layout=layout)
    return fig

#def draw_boxplot(df,season):
#    df_S = df[df['Season']==season]
#    fig = px.box(df_S, x="Age", y="Sport", color="Season", orientation="h")
#    fig.update_layout(
#        title="Age Distribution by Sport and Season",
#        xaxis_title="Age",
#        yaxis_title="Sport",
#        font=dict(
#            family="Old Standard TT, serif",
#            size=12,
#            color="black"
#        ),
#        height=800,
#    )
#    return fig


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container(
    children=[
            dbc.Row(dbc.Col(html.H1("Dashboard analítico de Olimpiadas (120 años)", style={"textAlign": "center","color": "black"}))),                             # titulo
            dbc.Row(dbc.Col(html.H1(".", style={"textAlign": "left","color": "white","font-size": "15px"}))),  # detalle de objetivo del dashhboard
            dbc.Row(dbc.Col(html.H1(".", style={"textAlign": "left","color": "white","font-size": "15px"}))),  # detalle de objetivo del dashhboard
            dbc.Row(dbc.Col(html.H1("Visualización de análisis de set de datos históricos de los Juegos Olimpicos desde Atenas 1896 a Rio 2016 ", style={"textAlign": "center","color": "black","font-size": "15px"}))),  # detalle de objetivo del dashhboard
            dbc.Row(dbc.Col(html.H1(".", style={"textAlign": "left","color": "white","font-size": "15px"}))),  # detalle de objetivo del dashhboard
            dbc.Row(dbc.Col(html.H1(".", style={"textAlign": "left","color": "white","font-size": "15px"}))),  # detalle de objetivo del dashhboard
            dbc.Row(dbc.Col(html.H1(".", style={"textAlign": "left","color": "white","font-size": "15px"}))),  # detalle de objetivo del dashhboard

            dbc.Row(
                    [
                        dbc.Col(
                            [
                            html.H1("Distribución de medallas por el mundo anualmente",style={"textAlign": "center","color": "black","font-size": "30px"}),
                            dcc.RadioItems( 
                                    id='medalla-radio',
                                    options=[{'label': 'Gold', 'value': 'Gold'},
                                            {'label': 'Silver', 'value': 'Silver'},
                                            {'label': 'Bronze', 'value': 'Bronze'}],
                                    value='Gold'),
                            dcc.Graph(id="id_geoworld", figure=plot_world(world(data, data_region, "Summer","Gold")))
                            
                            ],
                        ),
                        
                    ]
                ),
            dbc.Row(
                [
                    dbc.Col(
                            [
                            dcc.Dropdown(
                                    id='id_dropdown', 
                                    options=paises_unicos, 
                                    value="Chile"),
                            dcc.Graph(id="id_medallero", figure=plot_medallero(medal(data,data_region,"Argentina","Summer"), "Argentina")),
                            ]
                        ),
                ]
            ),
            dbc.Row(
                    [
                        
                        dbc.Col(
                            [
                            dcc.RadioItems( 
                                    id='season-radio',
                                    options=[{'label': 'Winter', 'value': 'Winter'},
                                            {'label': 'Summer', 'value': 'Summer'}],
                                    value='Summer'
                                ),
                            html.H1("Scatter", style={"textAlign": "center","color": "black","font-size": "20px"}),
                            dcc.Graph(id="id_burbujas", figure=plot_burbujas(data,"Summer")),
                            ]
                        ),

                        dbc.Col(
                            [
                                html.H1("Distribución", style={"textAlign": "center","color": "black","font-size": "20px"}),
                                dcc.Graph(id="id_histograma", figure=histograma_imc(imc(data))),
                            
                            ],
                            width=4,
                        ),
                        
                    ]
                ),
                
            dbc.Row(
                [
                    dbc.Col(
                            [
                            html.H1("Boxplot", style={"textAlign": "center","color": "black","font-size": "20px"}),
                            dcc.Graph(id="id_boxplot", figure=draw_group(data,"Summer")),    
                            
                            ],
                            width=7,
                        ),

                    dbc.Col(
                            [
                                html.H1("Tendencia de Participación Hombres y Mujeres en Olimpiadas", style={"textAlign": "center","color": "black","font-size": "20px"}),
                                dcc.Graph(id="id_timeline", figure=plot_timeline(data,"Summer")),
                                
                            ],
                        ),
                ]
            ),
            
    ],
)

@app.callback(
    [Output('id_timeline', 'figure'),
     Output('id_medallero', 'figure'),
     Output('id_burbujas', 'figure'),
     Output('id_geoworld', 'figure'),
    Output('id_boxplot', 'figure')],
    [Input('season-radio', 'value'),
     Input('id_dropdown', 'value'),
     Input('medalla-radio', 'value')])

def update(season, pais, medalla):
    timeline = plot_timeline(data, season)
    medallero = plot_medallero(medal(data, data_region, pais, season), pais)
    burbujas = plot_burbujas(data, season)
    geo_world = plot_world(world(data, data_region, season, medalla))
    boxplot = draw_group(data, season)
    return timeline, medallero, burbujas, geo_world, boxplot

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port="8000")

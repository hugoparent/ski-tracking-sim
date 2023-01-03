import dash
import numpy
import pandas as pd
from dash import dcc, html, callback, ctx, State
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

mapbox_access_token = "pk.eyJ1IjoiaHVnb3BhcmVudCIsImEiOiJjbGF3ZHNyNWcwNWVvM3BzMjQyY213bzhmIn0.WBeiT-Molpx6kqiEiVxk1A"

#import data
DATASET = "https://raw.githubusercontent.com/hugoparent/ski-tracking-sim/main/output_data/output.csv"
df = pd.read_csv(DATASET)
df_in = df.copy()
# get number of rows
min_time = 0
max_time = n_rows = df_in.shape[0]
min_altitude = df_in['relativeAltitude'].min()
max_altitude = df_in['relativeAltitude'].max()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE], eager_loading=True)
server = app.server

app.layout = html.Div([
            # title
            dbc.Row([
                dbc.Col([html.H1('Montblanc Ski Tracking Simulator', style={'textAlign': 'center','margin-top':'15px'})]),
            ]),
            # First Row
            dbc.Label("Select Data for Simulation", html_for='file-selection',style={'margin-left': '10px'}),
            dbc.Row([
                    dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(
                                    id="file-select",
                                    options=[],
                                    placeholder="verbier_am.csv",#default value
                                ),
                            ],style={'margin-left': '10px'}),
                            dbc.Col([
                                dbc.Button("Load Data", id="load-data",  color="success", size="sm", style={'padding':'.45em'}),
                            ]),
                            dbc.Col(html.P(id='file-info')
                            ),
                        ],
                    ),
                ],
            ),
            # Second Row
            dbc.CardGroup([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                    html.H4('Current Data',className='h1'),
                                    html.P(id='live-update-text',className='card-text'),
                            ], style={'textAlign': 'center'}),
                            ]#, id='current-data-card'
                        )],style={'margin-right': '10px'}),
                ], width=3),
                dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                    dcc.Graph(id='live-update-graph'),#,style={'height': '45vh'}),
                            ])
                        ),
                ], width=9),
            ], style={'margin': '10px'}),
            # Third Row
            dbc.CardGroup([
                dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.H4('Cumulative Data', className='h1'),
                                    html.P(id='live-update-state', className='card-text'),
                                ], style={'textAlign': 'center'})
                            ])
                        ],style={'margin-right': '10px'}),
                ], width=3),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                dcc.Graph(id='live-update-map'),
                            ])
                        ),
                    ]),
                ], width=9),
            ], style={'margin': '10px'}),
            # Fourth Row
            dbc.Row([
                dbc.Col([
                        dbc.Button("Play/Stop", id="play",  color="warning", size="sm", style={'padding':'.45em'}),
                ], style={'margin-left': '10px'},width='auto'),
                dbc.Col([
                        dcc.Slider(min=0,
                           max=3600,
                           step=60,
                           value=0,
                           marks={i: '{}'.format(i) for i in range(0, 3600, 180)},
                           id='my-slider'
                           )
                ],width=11, style={'margin-right': '10px'}),
            ]),
            dcc.Interval(
                disabled=True,
                id='interval-component',
                interval=1000, # in milliseconds
                n_intervals=0
            )
        ])


# Callback for slider
@app.callback(
    Output("my-slider", "value"),
    Input('interval-component', 'n_intervals'),
    State('my-slider', 'value'),
    prevent_initial_call=True,
)
def update_output(n, selected_value):
    interval = 30
    max_time = 3600/interval
    selected_value = (n % max_time) * interval
    return selected_value

@app.callback(
    Output("interval-component", "disabled"),
    Input("play", "n_clicks"),
    State("interval-component", "disabled"),
)
def toggle(n, playing):
    if n:
        return not playing
    return playing


# Callback for current user data
@app.callback(Output('live-update-text', 'children'),
              Input('my-slider', 'value'))
def update_metrics(n):
    current_time = df_in['run_time'][n]
    current_alt = df_in['relativeAltitude'][n]
    current_state = df_in['state'][n]
    current_speed = df_in['speed'][n]
    current_top_speed = df_in['top_speed_run'][n]
    current_distance = df_in['distance_run'][n]
    if current_state == 0:
        return [
            html.P('State: Idle', className='text-danger display-6'),
            html.P('Not Tracking', className='text-danger display-6')
        ]
    elif current_state == 1:
        return [
            html.P('State: Skiing', className='text-success display-6'),
            html.P('Active Time: {}'.format(current_time),className='h3'),
            html.P('Altitude Change: {0:0.2f}m'.format(current_alt),className='h3'),
            html.P('Speed: {0:0.2f}m/s'.format(current_speed) + '  (Top: {0:0.2f}m/s)'.format(current_top_speed),className='h3'),
            html.P('Distance: {0:0.2f}m'.format(current_distance),className='h3')
        ]
    else:
        return [
            html.P('State: Lift', className='text-warning display-6'),
            html.P('Not Tracking', className='text-warning display-6')
        ]


# Update Altitude Graph
@app.callback(Output('live-update-graph', 'figure'),
              Input('my-slider', 'value'))
def update_graph_live(n):
    lst_graph_time = df_in[:n].index.to_list()
    lst_graph_altitude = df_in['relativeAltitude'][:n].to_list()
    current_state = df_in['state'][n]

    if current_state == 0:
        color = 'firebrick'
    elif current_state == 1:
        color = 'green'
    else:
        color = 'goldenrod'

    # graph altitude per time plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=lst_graph_time,
                             y=lst_graph_altitude,
                             line=dict(color=color, width=2)))

    fig.update_layout(title=None,
                      xaxis_title=None,
                      yaxis_title='Altitude (m)',
                      xaxis_range=[min_time,max_time],
                      yaxis_range=[min_altitude-50, max_altitude + 50],
                      height = 350,
                      margin=dict(t=0, b=0, l=0, r=0),
                      template='plotly_dark',
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)'
                      )
    # change color of last drawn point

    return fig

# keep opacity positive for the last 200 points or more
def compute_opacity(n):
    list_opacity = []
    threshold = 500
    for i in range(0,n):
        if ((1 / threshold) * i - ((n - threshold) / threshold)) <= 0:
            list_opacity.append(0)
        else:
            list_opacity.append((1 / threshold) * i - ((n - threshold) / threshold))
    return list_opacity


# Update Map
@app.callback(Output('live-update-map', 'figure'),
              Input('my-slider', 'value'))
def update_graph_map(n):
    current_state = df_in['state'][n]
    if current_state == 0:
        color = 'firebrick'
    elif current_state == 1:
        color = 'green'
    else:
        color = 'goldenrod'

    if n != 0:
        lst_map_lat = df_in['latitude'][:n].to_list()
        lst_map_lon = df_in['longitude'][:n].to_list()
        mean_qty = 20
        avg_lat = sum(lst_map_lat[-mean_qty:])/mean_qty
        avg_lon = sum(lst_map_lon[-mean_qty:])/mean_qty

    else:
        lst_map_lat = [df_in['latitude'][0]]
        lst_map_lon = [df_in['longitude'][0]]
        avg_lat = df_in['latitude'][0]
        avg_lon = df_in['longitude'][0]

    scaled_opacity_0_1 = compute_opacity(n)

    fig_mapbox = go.Figure(go.Scattermapbox(
        lat= lst_map_lat,
        lon= lst_map_lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=4,
            color=color,
            opacity = scaled_opacity_0_1
        )
    ))
    fig_mapbox.add_trace(go.Scattermapbox(
        lat=[lst_map_lat[-1]],
        lon=[lst_map_lon[-1]],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=8,
            color='yellow'
        )
    ))

    fig_mapbox.update_layout(
        height = 400,
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            style='mapbox://styles/hugoparent/clbno9247000114oqq5w62y59',
            bearing=0,
            center=dict(
                lat=avg_lat,
                lon=avg_lon
            ),
            pitch=0,
            zoom=14,
        ),
        margin=dict(t=0, b=0, l=0, r=0),
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False

    )
    return fig_mapbox



@app.callback(Output('live-update-state', 'children'),
              Input('my-slider', 'value'))
def update_cumul(n):
    total_time = df_in['activity_time'][n]
    n_runs = df_in['n_runs'][n]
    top_speed = df_in['top_speed_total'][n]
    max_altitude_total = df_in['max_altitude_total'][n]
    distance_total = df_in['distance_total'][n]
    if n<60:
        return [
            html.P('Number of Runs: 0', className='display-6'),
            html.P('Total Active Time: 0', className='h3'),
            html.P('Top Speed: 0 m/s', className='h3'),
            html.P('Distance: 0 m', className='h3')
        ]
    else:
        return [
            html.P('Number of Runs: {:.0f}'.format(n_runs), className='display-6'),
            html.P('Total Active Time: {:.0f}s'.format(total_time), className='h3'),
            html.P('Top Speed: {0:0.1f}m/s'.format(top_speed), className='h3'),
            html.P('Distance: {:.0f}m'.format(distance_total), className='h3')
        ]
if __name__ == '__main__':

    app.run_server(debug=False)



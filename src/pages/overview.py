from dash import register_page, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import requests
import json
import numpy as np
import dash_bootstrap_components as dbc
from .filtercomponent import create_filter_panel, apply_filters


register_page(__name__, path='/', name='overview')

def preprocess_data(df):
    df['Date Of Stop'] = pd.to_datetime(df['Date Of Stop'], format='%m/%d/%Y')
    df['Year'] = df['Date Of Stop'].dt.year
    df['Month'] = df['Date Of Stop'].dt.month
    df['Month_Name'] = df['Date Of Stop'].dt.strftime('%B')
    
    def clean_fine(value):
        if pd.isna(value) or value == 'MA':
            return 0
        
       
        cleaned = str(value).replace('$', '').replace('MA', '').replace(',', '').strip()
        return float(cleaned or 0)
        
    df['Fine_x'] = df['Fine'].apply(clean_fine)
    df['Contr.Acc Fine'] = df['Contr.Acc Fine'].apply(clean_fine)
    df['Total_Fine'] = df.apply(
        lambda row: row['Contr.Acc Fine'] if row['Contributed To Accident'] == True 
        else row['Fine_x'], axis=1
    )
    
    
    df['Fatal_Count'] = (df['Fatal'] == 'Yes').astype(int)
    
    df = df[df['Latitude'].notna() & df['Longitude'].notna()]
    df = df[
        (df['Latitude'] >= 37.5) & (df['Latitude'] <= 40) &
        (df['Longitude'] >= -79.5) & (df['Longitude'] <= -75)
    ]
    
    df['Lat_Bin'] = np.round(df['Latitude'], 2)
    df['Lon_Bin'] = np.round(df['Longitude'], 2)
    df['Count'] = 1
    
    def discretize_fatal(count):
        if count == 0:
            return 0
        elif count == 1:
            return 1
        else:
            return 2
                
    df['Fatal_Count_Discrete'] = (df['Fatal'] == 'Yes').astype(int).apply(discretize_fatal)
    return df

def aggregate_data(df):
    agg_df = df.groupby(['Lat_Bin', 'Lon_Bin']).agg({
        'Total_Fine': 'sum',
        'Count': 'sum',
        'Fatal_Count': 'sum',
        'Fatal_Count_Discrete': 'max'
    }).reset_index().rename(columns={
        'Lat_Bin': 'Latitude', 
        'Lon_Bin': 'Longitude', 
        'Count': 'Violation_Count'
    })
    
    agg_df['Fatal_Count_Discrete'] = agg_df['Fatal_Count'].apply(
        lambda x: 0 if x == 0 else (1 if x == 1 else 2)
    )
    return agg_df


df = pd.read_csv("Maryland_Traffic_Violation.csv")
df = preprocess_data(df)
df['County'] = 'Montgomery'

maryland_geojson = requests.get(
    "https://raw.githubusercontent.com/frankrowe/maryland-geojson/master/maryland-counties.geojson"
).json()


layout = html.Div([
    html.Div([
        # Left Panel
        html.Div([
            html.Img(
                src='/assets/Countylogo.png',
                alt='Montgomery County logo',
                style={
                    'display': 'block',
                    'margin': '0 auto',
                    'width': '80%',
                    'height': 'auto',
                    'marginBottom': '30px'
                }
            ),
            
           html.Div(
    create_filter_panel(df),
    style={'padding': '10px'}
)
        ],
         style={
    'marginTop': '5%',
    'width': '300px',
    'height': '900px',
    'backgroundColor': 'white',
    'padding': '20px',
    'borderTop': '3px solid black',
    'borderBottom': '3px solid black',
    'borderLeft': '3px solid black',
    'border-top-left-radius': '10px',
    'border-bottom-left-radius': '10px',
    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)' 
  
}),
        
        # Right Panel
        html.Div([
      
            html.Div([
                html.P(
                    "Traffic Violation Overview Dashboard",
                    style={
                        'textAlign': 'left',
                        'marginLeft': '20px',
                        'paddingTop': '10px',
                        'fontWeight': 'bold',
                        'fontSize': 30,
                        'color': 'black',
                        'fontFamily':'Sans-Serif'
                    }
                )
            ],
            style={
                'width': '860px',
                'height': '70px',
                'backgroundColor': 'white',
                'position': 'absolute',
                'top': '15px',
                'left': '20px',
                 'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
            }),
            
            # Stats Panel
            html.Div([
                html.Div([
                    html.Div([
                        html.P("Total Violations", 
                               style={'fontSize': 14, 'fontFamily':'Monospace','margin': 0}),
                        html.P(id='total-violations',
                               style={'fontSize': 24, 'fontWeight': 'bold', 'fontFamily':'Sans-Serif','margin': 0})
                    ], style={'flex': 1, 'textAlign': 'center'}),
                    
                    html.Div([
                        html.P("Total Fines", 
                               style={'fontSize': 14, 'fontFamily':'Monospace', 'margin': 0}),
                        html.P(id='total-fines',
                               style={'fontSize': 24, 'fontWeight': 'bold', 'fontFamily':'Sans-Serif','margin': 0})
                    ], style={'flex': 1, 'textAlign': 'center'}),
                    
                    html.Div([
                        html.P("Total Locations", 
                               style={'fontSize': 14, 'fontFamily':'Monospace', 'margin': 0}),
                        html.P(id='total-locations',
                               style={'fontSize': 24, 'fontWeight': 'bold','fontFamily':'Sans-Serif', 'margin': 0})
                    ], style={'flex': 1, 'textAlign': 'center'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '20px'})
            ],
            style={
                'width': '460px',
                'height': '95px',
                'backgroundColor': 'white',
                'position': 'absolute',
                'top': '95px',
                'left': '20px',
                 'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
            }),
            
            # Left Chart Panel
            html.Div([
                html.Div([
                    dcc.RadioItems(
                        id='trend-type',
                        options=[
                            {'label': 'Total Violations', 'value': 'violations'},
                            {'label': 'Total Fines', 'value': 'fines'}
                        ],
                        value='violations',
                        className='radio-items',
                        inline=True,
                         style={
                    'fontSize': '12px',
                    'fontWeight': 'bold',
                    'fontFamily': 'Monospace',
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'width': '100%',
                   'padding': '10px 20px'  
                },
                  labelStyle={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginRight': '10px',
                    'gap': '8px'
                },
                    ),
                    dcc.Graph(
                        id='yearly-trend',
                        style={'height': '250px'}
                    )
                ])
            ],
            style={
                'width': '460px',
                'height': '295px',
                'backgroundColor': 'white',
                'position': 'absolute',
                'top': '200px',
                'left': '20px',
                 'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
            }),
            
            # Map Panel
            html.Div([
                html.Div([
                    dcc.RadioItems(
                        id='visualization-type',
                        options=[
                            {'label': 'Total Fines', 'value': 'fine'},
                            {'label': 'Violation Count', 'value': 'violation'},
                            {'label': 'Fatal Cases', 'value': 'fatal'}
                        ],
                        value='fine',
                        className='radio-items',
                        inline=True,
                       style={
                    'fontSize': '12px',
                    'fontWeight': 'bold',
                    'fontFamily': 'Monospace',
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'width': '100%',
                    'padding': '10px 20px'  
                },
                  labelStyle={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginRight': '10px',
                    'gap': '8px'
                },
                    ),
                    dcc.Graph(
                        id='violation-map',
                        style={'height': '330px'}
                    )
                ])
            ],
            style={
                'width': '390px',
                'height': '400px',
                'backgroundColor': 'white',
                'position': 'absolute',
                'top': '95px',
                'left': '490px',
                    'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
            }),
            
            # Bottom Left Panel
            html.Div([
    html.Div([
        dcc.RadioItems(
            id='chart-type',
            options=[
                {'label': 'Violation Types', 'value': 'violation'},
                {'label': 'Arrest Types', 'value': 'arrest'}
            ],
            value='violation',
            className='radio-items',
            inline=True,
            style={
                'fontSize': '12px',
                'fontWeight': 'bold',
                'fontFamily': 'Monospace',
                'display': 'flex',
                'justifyContent': 'space-between',
                'width': '100%',
                'padding': '10px 20px'
            },
            labelStyle={
                'display': 'flex',
                'alignItems': 'center',
                'marginRight': '10px',
                'gap': '8px'
            },
        ),
        dcc.Graph(
            id='violation-type-pie',
            style={'height': '330px'}
        )
    ])
],
style={
    'width': '400px',
    'height': '375px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '505px',
    'left': '20px',
    'borderRadius': '5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
}),
            
            # Bottom Right Panel
            html.Div([
                html.Div([
                    dcc.RadioItems(
                        id='subagency-metric',
                        options=[
                            {'label': 'Violation Count', 'value': 'count'},
                            {'label': 'Total Fines', 'value': 'fines'}
                        ],
                        value='count',
                        className='radio-items',
                        inline=True,
                          style={
                    'fontSize': '12px',
                    'fontWeight': 'bold',
                    'fontFamily': 'Monospace',
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'width': '100%',
                   'padding': '10px 20px'  
                },
                  labelStyle={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginRight': '10px',
                    'gap': '8px'
                },
                    ),
                    dcc.Graph(
                        id='subagency-bar',
                        style={'height': '320px'}
                    )
                ])
            ],
            style={
                'width': '450px',
                'height': '375px',
                'backgroundColor': 'white',
                'position': 'absolute',
                'top': '505px',
                'left': '430px',
                'borderRadius': '5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
            }),
        ],
        style={
            'marginTop': '5%',
            'width': '900px',
            'height': '900px',
            'backgroundColor': '#EEEEEE',
            'padding': '20px',
            'border': '3px solid black',
            'position': 'relative',
            'border-top-right-radius': '10px',
    'border-bottom-right-radius': '10px',
    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)' 
        }),
    ],
    style={
        'display': 'flex',
        'width': '1200px',
        'height': '1080px',
        'backgroundColor': 'white',
        'margin': '0 auto',
        
    })
])

@callback(
    Output('subagency-bar', 'figure'),
    [Input('subagency-metric', 'value'),
     Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value')]
)
def update_subagency_bar(metric_type, selected_year, selected_month, selected_states):
    filtered_df = df.copy()
    
   
    filtered_df = apply_filters(df, selected_year, selected_month, selected_states)

   
    def shorten_subagency(name):
        if 'District' in name:
            return name[:name.find('District') + len('District')] + "  "  
        elif 'Headquarters' in name:
            return name[:name.find('Headquarters') + len('Headquarters')] + "  "  
        return name + "  " 

 
    filtered_df['SubAgency'] = filtered_df['SubAgency'].apply(shorten_subagency)
    
   
    if metric_type == 'count':
        subagency_data = filtered_df.groupby('SubAgency').size().reset_index(name='Count')
        subagency_data = subagency_data.sort_values('Count', ascending=True)
        x_title = 'Number of Violations'
        value_col = 'Count'
    else: 
        subagency_data = filtered_df.groupby('SubAgency')['Total_Fine'].sum().reset_index()
        subagency_data = subagency_data.sort_values('Total_Fine', ascending=True)
        x_title = 'Total Fines ($)'
        value_col = 'Total_Fine'

 
    bar_fig = px.bar(
        subagency_data,
        x=value_col,
        y='SubAgency',
        orientation='h',
        title='Violations by SubAgency' if metric_type == 'count' else 'Fines by SubAgency',
        
    )

 
    bar_fig.update_layout(
        title=dict(
            x=0.5,
            xanchor='center',
            font=dict(size=14, weight='bold', family='Sans-Serif', color='black')
        ),
        xaxis=dict(
            title=dict(
                text=x_title,
                font=dict(size=10, weight = 'bold')
            ),
            tickformat=',.0f'
        ),
        yaxis=dict(
            title=None,
            automargin=True,
              
            tickfont=dict(size=8, weight='bold')
      
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
        height=320,
       
    )

   
    bar_fig.update_traces(
        hovertemplate=(
            '<b>%{y}</b><br>' +
            ('Violations: %{x:,.0f}' if metric_type == 'count' else 'Total Fines: $%{x:,.2f}') +
            '<extra></extra>'
        ),
        marker_color='#4169E1',
        marker=dict(cornerradius = 5)
    )

   
    
    return bar_fig

@callback(
    Output('yearly-trend', 'figure'),
    [Input('trend-type', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value')]
)
def update_yearly_trend(trend_type, selected_month, selected_states):
    filtered_df = df.copy()
    
    #
    if selected_month != 'all':
        filtered_df = filtered_df[filtered_df['Month'] == int(selected_month)]
    if 'all' not in selected_states:
        filtered_df = filtered_df[filtered_df['Driver State'].isin(selected_states)]
    
    
    yearly_data = filtered_df.groupby('Year').agg({
        'Total_Fine': 'sum',
        'Year': 'size'  
    }).rename(columns={'Year': 'Violation_Count'})
    
  
    if trend_type == 'violations':
        y_data = yearly_data['Violation_Count']
        title = 'Yearly Violation Trends'
        y_title = 'Total Violations'
        hover_template = '<b>Year: %{x}</b><br>Violations: %{y:,.0f}<extra></extra>'
    else: 
        y_data = yearly_data['Total_Fine']
        title = 'Yearly Fine Trends'
        y_title = 'Total Fines ($)'
        hover_template = '<b>Year: %{x}</b><br>Total Fines: $%{y:,.2f}<extra></extra>'
    
 
    trend_fig = px.line(
        x=yearly_data.index,
        y=y_data,
        markers=True
    )
    

    trend_fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            y=0.99,
            xanchor='center',
            font=dict(size=14, weight= 'bold', family='Sans-Serif', color='black')
        ),
        xaxis=dict(
            title=dict(
                text='Year',
                font=dict(size=10, weight= 'bold')  
            ),
            tickmode='array',
            ticktext=[f"'{str(year)[-2:]}"  for year in yearly_data.index],
            tickvals=yearly_data.index,
            tickangle=0
            
        ),
        yaxis=dict(
            title=dict(
                text=y_title,
                font=dict(size=10, weight= 'bold')  
            ),
            tickformat=',.0f' if trend_type == 'violations' else ',.0f'
        ),
        margin=dict(l=50, r=20, t=40, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False
    )
    

    trend_fig.update_traces(
        mode='lines+markers',
        line=dict(width=2),
        marker=dict(size=8),
        hovertemplate=hover_template
    )
    
    
    return trend_fig

@callback(
    Output('violation-type-pie', 'figure'),
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('chart-type', 'value')]  
)
def update_violation_pie(selected_year, selected_month, selected_states, chart_type):
    filtered_df = df.copy()
    
    filtered_df = apply_filters(df, selected_year, selected_month, selected_states)
    
 
    violation_colors = ['#D72631', '#A2D5C6', '#077B8A', '#5C3C92']
    arrest_colors = ['#D72631', '#A2D5C6', '#077B8A', '#5C3C92']
    
    if chart_type == 'violation':
        type_counts = filtered_df['Violation Type'].value_counts()
        total_count = type_counts.sum()
        
        type_percentages = (type_counts / total_count * 100).round(1)
        labels = [f"{vtype}<br>({pct}%)" for vtype, pct in zip(type_counts.index, type_percentages)]
        
        title = "Distribution of Violation Types"
        colors = violation_colors
        
    else: 
      
        type_counts = filtered_df['Arrest Type'].value_counts().head(4)
        total_count = type_counts.sum()
        
        
        type_percentages = (type_counts / total_count * 100).round(1)
        labels = [f"{vtype}({pct}%)" for vtype, pct in zip(type_counts.index, type_percentages)]
        
        title = "Top 4 Arrest Types"
        colors = arrest_colors
    
   
    pie_fig = px.pie(
        values=type_counts.values,
        names=labels,
        hole=0,
        color_discrete_sequence=colors  
    )
    
 
    pie_fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(size=14, weight= 'bold', family='Sans-Serif', color='black')
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.8,
            xanchor="center",
            x=0.5,
            font=dict(size=8, weight='bold')
        ),
        margin=dict(l=10, r=10, t=80, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=330
    )
    

    pie_fig.update_traces(
        textposition='inside',
        textinfo='percent',
        insidetextfont=dict(size=10),
        hovertemplate="<b>%{label}</b><br>" +
                      "Count: %{value}<br>" +
                      "<extra></extra>"
    )
    
    return pie_fig

@callback(
    [Output('total-violations', 'children'),
     Output('total-fines', 'children'),
     Output('total-locations', 'children')],
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value')]
)
def update_stats(selected_year, selected_month, selected_states):
    filtered_df = df.copy()
    
    filtered_df = apply_filters(df, selected_year, selected_month, selected_states)
    
    total_violations = len(filtered_df)
    total_fines = f"${filtered_df['Total_Fine'].sum():,.2f}"
    total_locations = len(filtered_df['Location'].unique())
    
    return f"{total_violations:,}", total_fines, f"{total_locations:,}"

@callback(
    Output('violation-map', 'figure'),
    [Input('visualization-type', 'value'),
     Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value')]
)
def update_map(viz_type, selected_year, selected_month, selected_states):
    filtered_df = df.copy()
    
    filtered_df = apply_filters(df, selected_year, selected_month, selected_states)
    agg_data = aggregate_data(filtered_df)
    
    
    if viz_type == 'fine':
        z_data = agg_data['Total_Fine']
        colorscale = 'Cividis'
        hover_template = 'Lat: %{lat}<br>Lon: %{lon}<br>Total Fines: $%{z:.2f}'
        colorbar_title = 'Total Fines'
        map_title = 'Distribution of Total Fines'
    elif viz_type == 'violation':
        z_data = agg_data['Violation_Count']
        colorscale = 'Viridis'
        hover_template = 'Lat: %{lat}<br>Lon: %{lon}<br>Violations: %{z}'
        colorbar_title = 'Violation Count'
        map_title = 'Distribution of Violations'
    else:  
        z_data = agg_data['Fatal_Count_Discrete']
        colorscale = [[0, 'rgb(255,255,255)'], 
                     [0.5, 'rgb(255,150,150)'], 
                     [1, 'rgb(255,0,0)']]        
        hover_template = 'Lat: %{lat}<br>Lon: %{lon}<br>Fatal Category: %{z}'
        colorbar_title = 'Fatal Category'
        map_title = 'Distribution of Fatal Incidents'

    map_fig = px.density_mapbox(
        agg_data,
        lat='Latitude',
        lon='Longitude',
        z=z_data,
        radius=20,
        opacity=0.7,
        zoom=6.5,
        mapbox_style="white-bg",
        color_continuous_scale=colorscale
    )

  
    for feature in maryland_geojson["features"]:
        geometry = feature["geometry"]
        properties = feature["properties"]
        county_name = properties.get("name", "Unknown")

        if geometry["type"] == "Polygon":
            for poly in geometry["coordinates"]:
                lon = [coord[0] for coord in poly]
                lat = [coord[1] for coord in poly]
                map_fig.add_trace(
                    dict(
                        type="scattermapbox",
                        lon=lon,
                        lat=lat,
                        fill="toself",
                        fillcolor="rgb(243, 243, 243)",
                        mode="lines",
                        line=dict(width=1.2, color='rgb(255, 255, 255)'),
                        showlegend=False,
                        hoverinfo="text",
                        text=county_name
                    )
                )
        elif geometry["type"] == "MultiPolygon":
            for multi_poly in geometry["coordinates"]:
                for poly in multi_poly:
                    lon = [coord[0] for coord in poly]
                    lat = [coord[1] for coord in poly]
                    map_fig.add_trace(
                        dict(
                            type="scattermapbox",
                            lon=lon,
                            lat=lat,
                            fill="toself",
                            fillcolor='rgb(243, 243, 243)',
                            mode="lines",
                            line=dict(width=1.2, color='rgb(255, 255, 255)'),
                            showlegend=False,
                            hoverinfo="text",
                            text=county_name
                        )
                    )

     
        if geometry["type"] == "Polygon":
            lon, lat = zip(*geometry["coordinates"][0])
            centroid_lon = np.mean(lon)
            centroid_lat = np.mean(lat)
        else:
            all_lon = []
            all_lat = []
            for poly in geometry["coordinates"]:
                for coord in poly[0]:
                    all_lon.append(coord[0])
                    all_lat.append(coord[1])
            centroid_lon = np.mean(all_lon)
            centroid_lat = np.mean(all_lat)

        map_fig.add_trace(
            dict(
                type="scattermapbox",
                lon=[centroid_lon],
                lat=[centroid_lat],
                mode="text",
                text=[county_name.upper()],
                textfont=dict(size=8, color="black", weight=600),
                showlegend=False
            )
        )

        map_fig.update_layout(
            title=dict(
                text=map_title,
                x=0.5,
                y=0.95,
                xanchor='center',
                font=dict(size=14, weight='bold', family='Sans-Serif', color='black')
            ),
            mapbox=dict(
                center=dict(lat=39.0458, lon=-76.6413),
                zoom=6.5,
                style="white-bg"
            ),
            margin={"r": 0, "t": 40, "l": 0, "b": 0}, 
            paper_bgcolor='white',
            plot_bgcolor='#ADD8E6'
        )

    if viz_type == 'fatal':
        map_fig.update_layout(
            coloraxis=dict(
                colorbar=dict(
                    len=0.5,
                    thickness=10,
                    x=1,
                    y=0.5,
                    tickfont=dict(size=10),
                    title=dict(
                        text=colorbar_title,
                        side='right',
                        font=dict(size=10)
                    ),
                    tickvals=[0, 1, 2],
                    ticktext=['0', '1', '2'],
                    ticks='outside'
                ),
                cmin=0,
                cmax=2
            )
        )
    else:
        map_fig.update_layout(
            coloraxis=dict(
                colorbar=dict(
                    len=0.5,
                    thickness=10,
                    x=1,
                    y=0.5,
                    tickfont=dict(size=10),
                    title=dict(
                        text=colorbar_title,
                        side='right',
                        font=dict(size=10)
                    )
                )
            )
        )
    
    map_fig.update_traces(
        hovertemplate=hover_template
    )

    return map_fig


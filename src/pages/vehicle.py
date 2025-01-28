from dash import register_page, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from .filtercomponent import create_filter_panel, apply_filters

register_page(__name__, path='/vehicle', name='vehicle')

def clean_make_name(make):
    manufacturer_mapping = {
        'TOYO': 'TOYOTA', 'HOND': 'HONDA', 'NISS': 'NISSAN',
        'CHEV': 'CHEVROLET', 'FORD': 'FORD', 'HYUN': 'HYUNDAI',
        'LEXU': 'LEXUS', 'INFI': 'INFINITI', 'MITS': 'MITSUBISHI',
        'VOLV': 'VOLVO', 'DODG': 'DODGE', 'JEEP': 'JEEP',
        'SUBA': 'SUBARU', 'MERZ': 'MERCEDES-BENZ', 'MASE': 'MASERATI',
        'BMW': 'BMW', 'AUDI': 'AUDI', 'VOLK': 'VOLKSWAGEN',
        'KIA': 'KIA', 'MAZU': 'MAZDA'
    }
    
    make = str(make).strip().upper()
    if make == 'NAN' or make == 'UNKNOWN' or make == '':
        return None
    prefix = make[:4]
    return manufacturer_mapping.get(prefix, make)

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
    df['Clean_Make'] = df['Make'].apply(clean_make_name)
    return df

df = pd.read_csv("Maryland_Traffic_Violation.csv")
processed_df = preprocess_data(df)
processed_df['County'] = 'Montgomery'


def apply_vehicle_type_filter(df, vehicle_type):
    if vehicle_type == 'both':
        return df
    is_commercial = vehicle_type == 'commercial'
    return df[df['Commercial Vehicle'] == ('Yes' if is_commercial else 'No')]


layout = html.Div([
    html.Div([
        html.Img(
            src='assets/Countylogo.png',
            alt='County Logo',
            style={
                'display': 'block',
                'margin': '0 auto',
                'width': '80%',
                'height': 'auto',
            }
        ),
        html.Div(
            create_filter_panel(processed_df),
            style={ 'marginTop': '20px', 'padding': '10px'}
        ),
        html.Div([
            html.Label('Vehicle Type', style={
                      'fontWeight': 'bold', 
                    'fontFamily':'Monospace',
                      'display': 'block'}),
            
            dcc.Dropdown(
                id='vehicle-commercial-filter',
                options=[
                    {'label': 'Both', 'value': 'both'},
                    {'label': 'Commercial', 'value': 'commercial'},
                    {'label': 'Non-Commercial', 'value': 'non-commercial'}
                ],
                value='both',
                clearable=False,
                style={'width': '100%', }
            )
        ], style={'padding': '20px', 'marginTop': '-20px'}),
    ], style={
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
    
    html.Div([
        html.Div([
            html.P("Vehicle Analysis Dashboard",
                  style={
                      'textAlign': 'left',
                      'marginLeft': '20px',
                      'paddingTop': '10px',
                      'fontWeight': 'bold',
                      'fontSize': 30,
                      'color': 'black',
                      'fontFamily': 'Sans-Serif'
                  })
        ], style={
            'width': '860px',
            'height': '70px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '15px',
            'left': '20px',
             'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
        }),
        
        html.Div([
            dcc.Graph(id='top-makes-violations')
        ], style={
            'width': '200px',
            'height': '180px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '95px',
            'left': '680px',
             'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
        }),
        
        #HAZMAT
         html.Div([
    html.Div(id='hazmat-text', style={
        'textAlign': 'center',
        'fontSize': '24px',
        'fontWeight': 'bold',
        'marginTop': '10px'
    })
], style={
    'width': '200px',
    'height': '110px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '285px',
    'left': '680px',
     'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
}),
        html.Div([
            dcc.Graph(id='vehicle-type-chart')
        ], style={
            'width': '200px',
            'height': '180px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '405px',
            'left': '680px',
             'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
        }),
        #Top Left
               
    html.Div([
        html.Div(id='top-manufacturer-details')
    ], style={
        'width': '210px',
        'height': '100px',
        'backgroundColor': 'white',
        'position': 'absolute',
        'top': '95px',
        'left': '20px',
         'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
    }),
                #Top Middle
         html.Div([
        html.Div(id='top-manufacturer-year')
    ], style={
        'width': '210px',
        'height': '100px',
        'backgroundColor': 'white',
        'position': 'absolute',
        'top': '95px',
        'left': '240px',
         'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
    }),
     #Top Right    
        html.Div([
        html.Div(id='top-manufacturer-color')
    ], style={
        'width': '210px',
        'height': '100px',
        'backgroundColor': 'white',
        'position': 'absolute',
        'top': '95px',
        'left': '460px',
         'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
    }),
        html.Div([
    dcc.Graph(id='manufacturer-map', style={'height': '100%'})
], style={
    'width': '320px',
    'height': '250px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '205px',
    'left': '20px',
     'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
}),
        

html.Div([
    dcc.Graph(id='manufacturer-distribution')
], style={
    'width': '320px',
    'height': '250px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '205px',
    'left': '350px',
     'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
}),
html.Div([
    html.Div([
        dcc.RadioItems(
            id='incident-type',
            options=[
                {'label': 'Alcohol Incidents', 'value': 'alcohol'},
                {'label': 'Seatbelt Incidents', 'value': 'seatbelt'}
            ],
            value='alcohol',
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
    ]),
    dcc.Graph(id='funnel-chart')
], style={
    'width': '320px',
    'height': '200px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '465px',
    'left': '20px',
     'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
}),
 html.Div([
            html.Div(id='commercial-license-text', style={
                'textAlign': 'center',
                'fontSize': '24px',
                'fontWeight': 'bold',
                'marginTop': '30px'
            })
        ], style={
            'width': '320px',
            'height': '120px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '465px',
            'left': '350px',
             'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
        }),
  html.Div([
    dcc.Graph(id='violation-type-donut')
  ], style={
    'width': '320px',
    'height': '150px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '730px',
    'left': '20px',
     'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
  }),
  

 
 html.Div([
    dcc.Graph(id='vehicle-year-distribution')
], style={
    'width': '335px',
    'height': '285px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '595px',
    'left': '545px',
     'borderRadius':'5px',
    
}),

html.Div(id='year-stats-text', style={
    'width': '200px',
    'height': '285px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '595px',
    'left': '350px',
    'padding': '10px',
    
}),
    ], style={
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
    })
    
], style={
    'display': 'flex',
    'width': '1200px',
    'height': '1080px',
    'backgroundColor': 'white',
    'margin': '0 auto',
})



@callback(
    [Output('manufacturer-map', 'figure'),
     Output('manufacturer-distribution', 'figure')],
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('vehicle-commercial-filter', 'value')]
)
def update_vehicle_maps(selected_year, selected_month, selected_states, vehicle_type):
    filtered_df = processed_df.copy()
    filtered_df = apply_filters(filtered_df, selected_year, selected_month, selected_states)
    filtered_df = apply_vehicle_type_filter(filtered_df, vehicle_type)
    

    stops_by_location = filtered_df.groupby(['Driver_City_Latitude', 'Driver_City_Longitude', 'Clean_Make']).size().reset_index(name='stops')
    
    manufacturer_colors = {
        'TOYOTA': '#FF0000', 'HONDA': '#0000FF', 'NISSAN': '#808080',
        'CHEVROLET': '#FFD700', 'FORD': '#0000A0', 'HYUNDAI': '#00FF00',
        'LEXUS': '#800080', 'INFINITI': '#FFA500', 'MITSUBISHI': '#FF69B4',
        'VOLVO': '#4B0082', 'DODGE': '#FF4500', 'JEEP': '#006400',
        'SUBARU': '#8B4513', 'MERCEDES-BENZ': '#C0C0C0', 'MASERATI': '#000080',
        'BMW': '#4169E1', 'AUDI': '#808000', 'VOLKSWAGEN': '#9400D3',
        'KIA': '#FF1493', 'MAZDA': '#00CED1'
    }

    map_fig = go.Figure()

    for make in manufacturer_colors:
        make_data = stops_by_location[stops_by_location['Clean_Make'] == make]
        map_fig.add_trace(go.Scattergeo(
            lon=make_data['Driver_City_Longitude'],
            lat=make_data['Driver_City_Latitude'],
            mode='markers',
            name=make,
            marker=dict(
                size=6,
                opacity=0.7,
                color=manufacturer_colors[make]
            ),
            hovertemplate="<b>%{text}</b>",
            text=[make] * len(make_data)
        ))

    map_fig.update_layout(
        title=dict(
            text='Vehicle Manufacturer Distribution Map',
            font=dict(
                family='Sans-Serif',
                size=14,
                color='black',
                weight='bold'
            ),
            x=0.5,
            y=0.95
        ),
        geo=dict(
            scope='usa',
            projection_scale=1,
            center=dict(lat=38.0, lon=-95.0),
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            showsubunits=True,
            subunitcolor='rgb(255, 255, 255)',
            domain=dict(x=[0, 1], y=[0, 1])
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=250,
        width=300,
        autosize=False,
        paper_bgcolor='white',
        showlegend=False
    )

   
    make_counts = filtered_df['Clean_Make'].value_counts()
    dist_fig = go.Figure()
    
    for make, count in make_counts.items():
        if make in manufacturer_colors:
            dist_fig.add_trace(go.Bar(
                x=[make],
                y=[count],
                name=make,
                marker_color=manufacturer_colors[make]
            ))

    dist_fig.update_layout(
        title=dict(
            text='Vehicle Manufacturer Distribution',
            font=dict(
                family='Sans-Serif',
                size=14,
                color='black',
                weight='bold'
            ),
            x=0.5,
            y=0.95
        ),
        barmode='group',
        margin=dict(l=40, r=20, t=30, b=40),
        height=250,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            tickangle=45,
            title=None,
            tickfont=dict(size=8)
        ),
        yaxis=dict(
            title='Number of Stops',
            titlefont=dict(size=10, weight='bold'),
            tickfont=dict(size=8)
        )
    )

    return map_fig, dist_fig


@callback(
    Output('top-makes-violations', 'figure'),
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('vehicle-commercial-filter', 'value')]
)
def update_top_makes(selected_year, selected_month, selected_states, vehicle_type):
    filtered_df = processed_df.copy()
    filtered_df = apply_filters(filtered_df, selected_year, selected_month, selected_states)
    filtered_df = apply_vehicle_type_filter(filtered_df, vehicle_type)
    
    make_counts = filtered_df['Clean_Make'].value_counts()
    make_percentages = (make_counts / len(filtered_df) * 100).round(1)
    make_percentages = make_percentages[~make_percentages.index.isnull()].head(1)
    
    value = make_counts.values[0]
    percentage = make_percentages.values[0]
    manufacturer = make_percentages.index[0]

    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        values=[100],
        hole=0.7,
        direction='clockwise',
        sort=False,
        rotation=270,
        showlegend=False,
        textinfo='none',
        marker=dict(colors=['#E0E0E0'], line=dict(color='#D3D3D3', width=1))
    ))
    
    # Second trace for the actual percentage
    fig.add_trace(go.Pie(
        values=[percentage, 100 - percentage],
        hole=0.7,
        direction='clockwise',
        sort=False,
        rotation=270,
        showlegend=False,
        textinfo='none',
        marker=dict(
            colors=['#00798c', 'rgba(0,0,0,0)'],
            line=dict(color='#D3D3D3', width=1.2)
        )
    ))
    
    fig.add_annotation(
        text=f"{value:,}<br>{manufacturer}",
        x=0.5, y=0.7,
        font=dict(size=18, weight='bold', family='Monospace', color='black'),
        showarrow=False
    )
    
    fig.update_layout(
       margin=dict(l=10, r=10, t=20, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=200,
        height=180,
        showlegend=False
    )
    
    return fig

@callback(
    Output('vehicle-type-chart', 'figure'),
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('vehicle-commercial-filter', 'value')]
)
def update_vehicle_type(selected_year, selected_month, selected_states, vehicle_type):
    filtered_df = processed_df.copy()
    filtered_df = apply_filters(filtered_df, selected_year, selected_month, selected_states)
    filtered_df = apply_vehicle_type_filter(filtered_df, vehicle_type)
    
    filtered_df['Clean_Type'] = filtered_df['VehicleType'].str.split(' - ').str[1]
    type_counts = filtered_df['Clean_Type'].value_counts()
    total_vehicles = len(filtered_df)
    
    top_type = type_counts.index[0]
    top_count = type_counts.values[0]
    percentage = (top_count / total_vehicles * 100).round(1)
    
    fig = go.Figure()
    
    
    fig.add_trace(go.Pie(
        values=[100],
        hole=0.7,
        direction='clockwise',
        sort=False,
        rotation=270,
        showlegend=False,
        textinfo='none',
        marker=dict(colors=['#E0E0E0'], line=dict(color='#D3D3D3', width=1))
    ))
    
  
    fig.add_trace(go.Pie(
        values=[percentage, 100 - percentage],
        hole=0.7,
        direction='clockwise',
        sort=False,
        rotation=270,
        showlegend=False,
        textinfo='none',
        marker=dict(
            colors=['#edae49', 'rgba(0,0,0,0)'],
            line=dict(color='#D3D3D3', width=1.2)
        )
    ))
    
    fig.add_annotation(
        text=f"{top_count:,}<br>{top_type}",
        x=0.5, y=0.5,
         font=dict(size=16, weight='bold', family='Monospace', color='black'),
        showarrow=False
    )
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=200,
        height=180,
        showlegend=False
    )
    
    return fig

@callback(
    Output('commercial-license-text', 'children'),
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('vehicle-commercial-filter', 'value')]
)
def update_commercial_license(selected_year, selected_month, selected_states, vehicle_type):
    filtered_df = processed_df.copy()
    filtered_df = apply_filters(filtered_df, selected_year, selected_month, selected_states)
    filtered_df = apply_vehicle_type_filter(filtered_df, vehicle_type)
    
    commercial_vehicles = filtered_df[filtered_df['Commercial Vehicle'] == 'Yes']
    total_commercial = len(commercial_vehicles)
    commercial_with_license = len(commercial_vehicles[commercial_vehicles['Commercial License'] == 'Yes'])
    
    if total_commercial > 0:
        percentage = round((commercial_with_license / total_commercial * 100), 1)
    else:
        percentage = 0

    return html.Div([
        html.Div(f"{percentage:.1f}%", style={'fontSize': '24px', 'fontWeight': 'bold', 'fontFamily':'Sans-Serif'}),
        html.Div("Commercially Licensed", style={'fontSize': '20px', 'fontFamily':'Monospace', 'fontWeight': 'bold'})
    ])


@callback(
    Output('funnel-chart', 'figure'),
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('vehicle-commercial-filter', 'value'),
     Input('incident-type', 'value')]
)
def update_funnel_chart(selected_year, selected_month, selected_states, vehicle_type, incident_type):
    filtered_df = processed_df.copy()
    filtered_df = apply_filters(filtered_df, selected_year, selected_month, selected_states)
    filtered_df = apply_vehicle_type_filter(filtered_df, vehicle_type)
    
    if incident_type == 'alcohol':
       
        alcohol_violations = filtered_df[filtered_df['Alcohol'] == 'Yes']
        total_alcohol = len(alcohol_violations)
        alcohol_accidents = len(alcohol_violations[alcohol_violations['Accident'] == 'Yes'])
        alcohol_injuries = len(alcohol_violations[
            (alcohol_violations['Accident'] == 'Yes') & 
            (alcohol_violations['Personal Injury'] == 'Yes')
        ])
        alcohol_fatalities = len(alcohol_violations[
            (alcohol_violations['Accident'] == 'Yes') & 
            (alcohol_violations['Fatal'] == 'Yes')
        ])
        
        values = [total_alcohol, alcohol_accidents, alcohol_injuries, alcohol_fatalities]
        labels = ['Alcohol Violations', 'Resulted in Accidents', 'Caused Injuries', 'Resulted in Fatalities']
        colors = ['#C0392B', '#CD6155', '#D98880', '#E6B0AA']
        title = 'Alcohol-Related Incidents Severity'
        
    else:
        
        total_accidents = len(filtered_df[filtered_df['Accident'] == 'Yes'])
        no_belts = len(filtered_df[
            (filtered_df['Accident'] == 'Yes') & 
            (filtered_df['Belts'] == 'No')
        ])
        belt_injuries = len(filtered_df[
            (filtered_df['Accident'] == 'Yes') & 
            (filtered_df['Belts'] == 'No') &
            (filtered_df['Personal Injury'] == 'Yes')
        ])
        belt_fatalities = len(filtered_df[
            (filtered_df['Accident'] == 'Yes') & 
            (filtered_df['Belts'] == 'No') &
            (filtered_df['Personal Injury'] == 'Yes') &
            (filtered_df['Fatal'] == 'Yes')
        ])
        
        values = [total_accidents, no_belts, belt_injuries, belt_fatalities]
        labels = ['Total Accidents', 'No Seatbelt Used', 'Personal Injury', 'Fatality']
        colors = ['#2980B9', '#5499C7', '#7FB3D5', '#A9CCE3']
        title = 'Seatbelt-Related Accident Progression'
    
    fig = go.Figure()
    fig.add_trace(go.Funnel(
        name='Incidents',
        y=labels,
        x=values,
        textinfo="value+percent initial",
        textposition="inside",
        textfont=dict(size=8, weight='bold'),
        marker=dict(color=colors)
    ))
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=10),
        height=200,
        width = 320,
        showlegend=False,
        title=dict(
            text=title,
            x=0.5,
            y=0.97,
            xanchor='center',
            yanchor='top',
            font=dict(size=14, weight='bold', family='Sans-Serif', color='black')
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        yaxis=dict(
        tickfont=dict(size=8, weight='bold'),  

    ))
    
    return fig

@callback(
    [Output('vehicle-year-distribution', 'figure'),
     Output('year-stats-text', 'children')],
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('vehicle-commercial-filter', 'value')]
)
def update_vehicle_year_distribution(selected_year, selected_month, selected_states, vehicle_type):
    filtered_df = processed_df.copy()
    filtered_df = apply_filters(filtered_df, selected_year, selected_month, selected_states)
    filtered_df = apply_vehicle_type_filter(filtered_df, vehicle_type)
    
   
    unknown_sections_df = filtered_df[filtered_df['Section'] == 'Unknown Section']
    
  
    unknown_sections_df['Manufacture Year'] = pd.to_numeric(unknown_sections_df['Manufacture Year'], errors='coerce')
    
   
    year_range_df = unknown_sections_df[unknown_sections_df['Manufacture Year'].between(2011, 2013)]
    if not year_range_df.empty:
        top_year = year_range_df['Manufacture Year'].mode().iloc[0]
        top_year_count = len(year_range_df[year_range_df['Manufacture Year'] == top_year])
        total_unknown = len(unknown_sections_df)
        percentage = (top_year_count / total_unknown * 100) if total_unknown > 0 else 0
        
        
        top_year_charges = year_range_df[year_range_df['Manufacture Year'] == top_year]['Description'].mode().iloc[0]
    else:
        top_year = "N/A"
        percentage = 0
        top_year_charges = "N/A"
    
 
    def categorize_year(year):
        if pd.isna(year):
            return "Unknown"
        year = int(year)
        if year <= 1970:
            return "Vintage (≤1970)"
        elif 1971 <= year <= 1990:
            return "Classic (1971-1990)"
        elif 1991 <= year <= 2010:
            return "Modern (1991-2010)"
        elif 2011 <= year <= 2024:
            return "Current (2011-2024)"
    
    unknown_sections_df['Year_Category'] = unknown_sections_df['Manufacture Year'].apply(categorize_year)
  
  
    year_counts = unknown_sections_df['Year_Category'].value_counts().reindex([
        'Vintage (≤1970)', 'Classic (1971-1990)', 
        'Modern (1991-2010)', 'Current (2011-2024)'
    ])
    
    
    fig = go.Figure()
    
  
    fig.add_trace(go.Bar(
        x=year_counts.index,
        y=year_counts.values,
        name='Count',
        marker_color='#4287F5',
        marker = dict(cornerradius = 5),
        opacity=0.7
    ))
    

    fig.add_trace(go.Scatter(
        x=year_counts.index,
        y=year_counts.values,
        name='Frequency',
        line=dict(color='#ff4444', width=2),
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title=dict(
            text='SERO Violations by Vehicles by Age',
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(size=14, family='Sans-Serif', weight='bold', color='black')
        ),
        xaxis=dict(
            title='Age Category',
            tickangle=45,
            titlefont=dict(size=10, weight='bold'),
            tickfont=dict(size=8),
            title_standoff=0
        ),
        yaxis=dict(
            title='Number of Vehicles',
            titlefont=dict(size=10, weight = 'bold'),
            tickfont=dict(size=8),
            range=[0, max(year_counts.values) * 1.1] if not year_counts.empty else [0, 1]
        ),
        margin=dict(l=40, r=20, t=40, b=80),  
        height=280,
        width=320,
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        bargroupgap=0 
    )
    
   
    year_stats = html.Div([
        html.Div(f"{int(top_year) if top_year != 'N/A' else 'N/A'}", 
                style={'fontSize': '30px', 'fontWeight': 'bold', 'fontFamily': 'Sans-Serif', 'marginTop':'20px', 'marginLeft':'55px'}),
        html.Div("Frequent Year", 
                style={'fontSize': '16px', 'fontFamily': 'Monospace', 'marginLeft':'40px'}),
        html.Div(f"{percentage:.1f}%", 
                style={'fontSize': '24px', 'fontWeight': 'bold', 'marginTop': '20px', 'marginLeft':'65px'}),
        html.Div("of SERO Defects", 
                style={'fontSize': '14px', 'fontFamily': 'Monospace', 'marginLeft':'45px'}),
        html.Div(top_year_charges, 
                style={'fontSize': '18px', 'fontFamily': 'Monospace', 'wordWrap': 'break-word', 'textAlign':'center', 'marginTop':'30px', 'fontWeight': 'bold',})
    ])
    
    return fig, year_stats

@callback(
    Output('hazmat-text', 'children'),
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('vehicle-commercial-filter', 'value')]
)
def update_hazmat_count(selected_year, selected_month, selected_states, vehicle_type):
    filtered_df = processed_df.copy()
    filtered_df = apply_filters(filtered_df, selected_year, selected_month, selected_states)
    filtered_df = apply_vehicle_type_filter(filtered_df, vehicle_type)
    
    hazmat_count = len(filtered_df[filtered_df['HAZMAT'] == 'Yes'])
    
    return html.Div([
        html.Div(f"{hazmat_count:,}", style={'fontSize': '24px', 'fontWeight': 'bold', 'fontFamily': 'Sans-Serif', 'marginTop':'20px'}),
        html.Div("HAZMAT Violations", style={'fontSize': '18px', 'fontFamily': 'Monospace', 'fontWeight': 'bold'})
    ])
    
@callback(
    Output('violation-type-donut', 'figure'),
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('vehicle-commercial-filter', 'value')]
)
def update_violation_type(selected_year, selected_month, selected_states, vehicle_type):
    filtered_df = processed_df.copy()
    filtered_df = apply_filters(filtered_df, selected_year, selected_month, selected_states)
    filtered_df = apply_vehicle_type_filter(filtered_df, vehicle_type)
 
    violation_counts = filtered_df['Violation Type'].value_counts()
    
 
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', 
              '#D4A5A5', '#9B6B6B', '#77A8A8', '#6B4E71', '#BAA5FF']
    
    # Create donut chart
    fig = go.Figure()
    fig.add_trace(go.Pie(
        values=violation_counts,
        labels=violation_counts.index,
        hole=0.6,
        marker=dict(colors=colors[:len(violation_counts)]),
        textinfo='none'
    ))
    
    fig.update_layout(
        margin=dict(l=0, r=10, t=30, b=0),
        height=125,
        width=250,
        paper_bgcolor='white',
        plot_bgcolor='white',
        title=dict(
            text='Violation Types',
            x=0.65,
            y=0.92,
            xanchor='center',
            yanchor='top',
            font=dict(
                size=12,
                family='Sans-Serif',
                color='black',
                weight='bold'
            )
        ),
        legend=dict(
            x=1.0,
            y=0.5,
            font=dict(size=10, weight='bold'),
            xanchor='left',
            yanchor='middle',
            orientation='v'
        )
    )
    
    return fig

@callback(
    [Output('top-manufacturer-details', 'children'),
     Output('top-manufacturer-year', 'children'),
     Output('top-manufacturer-color', 'children')],
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('vehicle-commercial-filter', 'value')]
)
def update_top_manufacturer_kpis(selected_year, selected_month, selected_states, vehicle_type):
    filtered_df = processed_df.copy()
    filtered_df = apply_filters(filtered_df, selected_year, selected_month, selected_states)
    filtered_df = apply_vehicle_type_filter(filtered_df, vehicle_type)
    
 
    top_make = filtered_df['Clean_Make'].value_counts().index[0]
    top_make_count = filtered_df['Clean_Make'].value_counts().values[0]
    
    top_make_df = filtered_df[filtered_df['Clean_Make'] == top_make]
    
   
    top_year = top_make_df['Manufacture Year'].mode().iloc[0]
    year_count = len(top_make_df[top_make_df['Manufacture Year'] == top_year])
    
   
    top_model = top_make_df['Model'].mode().iloc[0]
    model_count = len(top_make_df[top_make_df['Model'] == top_model])
    
   
    top_color = top_make_df['Color'].mode().iloc[0]
    color_count = len(top_make_df[top_make_df['Color'] == top_color])
    
    # Create KPI components
    make_kpi = html.Div([
        html.Div(f"Most Common Model", 
                style={'fontSize': '16px', 'textAlign': 'center', 'fontFamily':'Monospace'}),
        html.Div(f"{top_model}", 
                style={'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center', 'fontFamily':'Sans-Serif'}),
       
    ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '5px'})
    
    year_kpi = html.Div([
        html.Div(f"Most Common Year", 
                style={'fontSize': '16px', 'textAlign': 'center', 'fontFamily':'Monospace'}),
        html.Div(f"{int(top_year)}", 
                style={'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center', 'fontFamily':'Sans-Serif'}),
      
       
    ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '5px'})
    
    color_kpi = html.Div([
         html.Div(f"Most Common Color", 
                style={'fontSize': '16px', 'textAlign': 'center', 'fontFamily':'Monospace'}),
       
        html.Div(f"{top_color}", 
                style={'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center', 'fontFamily':'Sans-Serif'}),
       
    ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '5px'})
    
    return make_kpi, year_kpi, color_kpi
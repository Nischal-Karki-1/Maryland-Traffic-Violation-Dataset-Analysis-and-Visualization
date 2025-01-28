from dash import register_page, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go 
from math import ceil

register_page(__name__, path='/demographics', name='demographics')


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
    
    return df

df = pd.read_csv("Maryland_Traffic_Violation.csv")
processed_df = preprocess_data(df)
processed_df['County'] = 'Montgomery'

from dash import html, dcc, callback, Output, Input
import plotly.express as px


@callback(
    [Output('search-metric-radio', 'style'),
     Output('demographics-radio-container', 'style')],
    [Input('demographics-toggle', 'value')]
)
def toggle_radio_buttons(show_demographics):
    if show_demographics:
        search_style = {'display': 'none'}
        demographics_style = {
            'textAlign': 'center',
          
            
        }
    else:
        search_style = {
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'backgroundColor': 'white',
            'padding': '10px',
            'fontSize': '15px',
            'fontWeight': 'bold'
        }
        demographics_style = {'display': 'none'}
    
    return search_style, demographics_style

@callback(
    Output('search-donut', 'figure'),
    [Input('demographics-toggle', 'value'),
     Input('demographics-radio', 'value'),
     Input('search-metric-radio', 'value'),
     Input('race-filter', 'value'),
     Input('gender-filter', 'value')]
)
def update_chart(show_demographics, demographics_type, search_metric, selected_race, selected_gender):
    filtered_df = processed_df.copy()
    
    if selected_race != 'all':
        filtered_df = filtered_df[filtered_df['Race'] == selected_race]
    if selected_gender != 'all':
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
    if show_demographics:
        if demographics_type == 'race':
            data = filtered_df['Race'].value_counts()
        else:
            data = filtered_df['Gender'].value_counts()
            data.index = data.index.map({'M': 'Male', 'F': 'Female', 'U': 'Unidentified'})
        
        value_counts = data.reset_index()
        value_counts.columns = ['Category', 'Count']
        title = f"Distribution by {'Race' if demographics_type == 'race' else 'Gender'}"
        
    else:
        if search_metric == 'search_conducted':
            data = filtered_df['Search Conducted'].fillna('Unknown')
            title = "Search Conducted Distribution"
            value_counts = data.value_counts().reset_index()
        
        elif search_metric == 'search_disposition':
            data = filtered_df[filtered_df['Search Conducted'] == 'Yes']['Search Disposition'].fillna('Unknown')
            value_counts = data.value_counts().nlargest(4).reset_index()
            title = "Search Dispositions"
        
        else:  # search_outcome
            data = filtered_df[filtered_df['Search Conducted'] == 'Yes']['Search Outcome'].fillna('Unknown')
            value_counts = data.value_counts().reset_index()
            title = "Search Outcomes Distribution"
        
        value_counts.columns = ['Category', 'Count']
    
    value_counts['Percentage'] = (value_counts['Count'] / value_counts['Count'].sum() * 100).round(1)
    value_counts['Label'] = value_counts.apply(lambda x: f"{x['Category']} ({x['Percentage']}%)", axis=1)
    
    fig = px.pie(
        value_counts,
        values='Count',
        names='Label',
        hole=0.6,
        color_discrete_sequence=px.colors.qualitative.Set3,
        title=title
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.7,
            xanchor="center",
            x=0.5,
            font=dict(size=8, weight='bold')
        ),
        margin=dict(t=50, l=10, r=10, b=20),
        height=280,
        title_x=0.5,
        title_y=0.97,
          title_font=dict(size=14, family='Sans-Serif', color='black', weight='bold')
        
    )
    
    fig.update_traces(
        textposition='none',
        textinfo='none',
        hovertemplate="<b>%{label}</b><br>" +
                    "Count: %{value}<extra></extra>"
    )
    
    return fig

@callback(
    Output('choropleth-map', 'figure'),
    [Input('map-type-radio', 'value'),
     Input('race-filter', 'value'),
     Input('gender-filter', 'value')]
)
def update_map(selected_map_type, selected_race, selected_gender):
    filtered_df = processed_df.copy()
    
    if selected_race != 'all':
        filtered_df = filtered_df[filtered_df['Race'] == selected_race]
    if selected_gender != 'all':
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
    location_col = {
        'state': 'State',
        'dl_state': 'DL State',
        'driver_state': 'Driver State'
    }[selected_map_type]
    
    stops_by_location = filtered_df[location_col].value_counts().reset_index()
    stops_by_location.columns = ['state', 'stops']
    
    fig = px.choropleth(
        stops_by_location,
        locations='state',
        locationmode='USA-states',
        color='stops',
        scope='usa',
        color_continuous_scale='Blues',
        labels={'stops': 'Number of Stops'}
    )
    

    fig.add_scattergeo(
        locations=stops_by_location['state'],
        locationmode='USA-states',
        text=stops_by_location['state'],
        mode='text',
        textfont=dict(size=8, color='black'),
        showlegend=False
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
        coloraxis_colorbar=dict(
            len=0.5,
            thickness=10,
            yanchor="middle",
            y=0.5,
            xanchor="right",
            x=0.98,
            tickfont=dict(size=10),
            title=dict(text="Stops", side="right", font=dict(size= 10) )
        )
    )
    
    return fig

@callback(
    Output('radar-chart', 'figure'),
    [Input('race-filter', 'value'),
     Input('gender-filter', 'value')]
)
def update_radar(selected_race, selected_gender):
    filtered_df = processed_df.copy()
    
    if selected_race != 'all':
        filtered_df = filtered_df[filtered_df['Race'] == selected_race]
    if selected_gender != 'all':
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]

    filtered_df['Belts'] = filtered_df['Belts'].map({'Yes': 1, 'No': 0}).fillna(0)
    filtered_df['Personal Injury'] = filtered_df['Personal Injury'].map({'Yes': 1, 'No': 0}).fillna(0) 
    filtered_df['Property Damage'] = filtered_df['Property Damage'].map({'Yes': 1, 'No': 0}).fillna(0)
    filtered_df['Alcohol'] = filtered_df['Alcohol'].map({'Yes': 1, 'No': 0}).fillna(0)
    filtered_df['Fatal'] = filtered_df['Fatal'].map({'Yes': 1, 'No': 0}).fillna(0)

    metrics = ['Belts', 'Personal Injury', 'Property Damage', 'Fatal', 'Alcohol']
    
    genders_to_plot = ['M', 'F', 'U'] if selected_gender == 'all' else [selected_gender]
    
    gender_labels = {
        'M': 'Male',
        'F': 'Female',
        'U': 'Unidentified'
    }

 
    base_color = '#6B4E71'  
    gender_colors = {
        'M': base_color,
        'F': '#9B6B9E',  
        'U': '#4E3D52'  
    }
    
    fig = go.Figure()
    all_values = []
    
    for gender in genders_to_plot:
        gender_df = filtered_df[filtered_df['Gender'] == gender]
        values = []
        for metric in metrics:
            value = gender_df[metric].mean() * 100
            values.append(value)
            all_values.append(value)
        
        values.append(values[0])
        metrics_plot = metrics + [metrics[0]]

        hex_color = gender_colors[gender].lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics_plot,
            name=gender_labels[gender],
            fill='toself',
            fillcolor=f'rgba{rgb + (0.3,)}',
            line=dict(color=gender_colors[gender], width=4),
            hovertemplate="<b>%{theta}</b><br>" +
                         f"Gender: {gender_labels[gender]}<br>" +
                         "Rate: %{r:.1f}%<br>" +
                         "<extra></extra>"
        ))

    max_value = max(all_values)
    
    def get_smart_breaks(max_val):
        max_val = ceil(max_val)
        if max_val <= 5: return list(range(0, ceil(max_val) + 1))
        elif max_val <= 10: return list(range(0, ceil(max_val / 2) * 2 + 2, 2))
        elif max_val <= 20: return list(range(0, ceil(max_val / 5) * 5 + 5, 5))
        elif max_val <= 50: return list(range(0, ceil(max_val / 10) * 10 + 10, 10))
        else: return list(range(0, ceil(max_val / 20) * 20 + 20, 20))

    axis_values = get_smart_breaks(max_value)
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, axis_values[-1]],
                tickformat='g',
                tickvals=axis_values,
                ticktext=[f'{int(v)}%' for v in axis_values],
                tickfont=dict(size=10),
                gridcolor=base_color,
                linecolor=base_color,
                linewidth=2
            ),
            angularaxis=dict(
                tickfont=dict(size=10, weight='bold'),
                rotation=90,
                direction="clockwise",
                gridcolor=base_color,
                linecolor=base_color,
                linewidth=2,
                period=5,
                type='category'
            ),
            bgcolor='white',
            gridshape='linear'
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=8, weight='bold')
        ),
        margin=dict(l=0, r=10, t=80, b=0),
        height=320,
        paper_bgcolor='white',
        title=dict(
            text='Incident Distribution by Type',
            x=0.5,
            y=0.92,
            xanchor='center',
            yanchor='top',
            font=dict(size=14, weight='bold', family='Sans-Serif', color='black')
        )
    )
    
    return fig

@callback(
    Output('display-content', 'children'),
    [Input('display-type-radio', 'value'),
     Input('race-filter', 'value'),
     Input('gender-filter', 'value')]
)
def update_display_content(display_type, selected_race, selected_gender):
    filtered_df = processed_df.copy()
    
    if selected_race != 'all':
        filtered_df = filtered_df[filtered_df['Race'] == selected_race]
    if selected_gender != 'all':
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
    if display_type == 'arrest_type':
        arrest_counts = filtered_df['Arrest Type'].value_counts().reset_index()
        arrest_counts.columns = ['Arrest Type', 'Count']
        total_arrests = arrest_counts['Count'].sum()
        arrest_counts['Percentage'] = (arrest_counts['Count'] / total_arrests * 100).round(1)
        arrest_counts['Label'] = arrest_counts.apply(
            lambda x: f"{x['Count']} ({x['Percentage']}%)", axis=1
        )
        
        arrest_counts['Short Label'] = arrest_counts['Arrest Type'].str[0]
        
        fig = px.bar(
            arrest_counts,
            x='Short Label',
            y='Count',
            text='Label',
            labels={'Short Label': 'Arrest Type', 'Count': 'Number of Arrests'}
        )
        
        fig.update_layout(
            margin=dict(l=10, r=20, t=50, b=10),
            showlegend=False,
            plot_bgcolor='white',
            xaxis=dict(
                tickangle=0,
                title=None,
                tickfont=dict(size=10),
                showgrid=False
            ),
            yaxis=dict(
                title=dict(
                    text='Number of Arrests',
                    font=dict(size=10, weight='bold'),
                ),
                tickfont=dict(size=10),
              
               
            ),
            height=280,  
            title=dict(
                text='Distribution of Arrest Types',
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top',
                font=dict(size=14, weight='bold', family='Sans-Serif')
                
            )
        )
        
        fig.update_traces(
            marker_color='#4287F5',
            textposition='outside',
            textangle=0,
            hovertemplate="<b>Arrest Type %{x}</b><br>" +
                         "Count: %{y}<extra></extra>",
                          marker=dict(cornerradius=5)
        )
        
        return dcc.Graph(
            figure=fig,
            config={'displayModeBar': False}
        )
    
    else:
        section_counts = filtered_df['Description'].value_counts().head(5).reset_index()
        section_counts.columns = ['Section', 'Count']
        total_count = section_counts['Count'].sum()
        section_counts['Percentage'] = (section_counts['Count'] / total_count * 100).round(1)
        
        return html.Div([
             html.P("Top 5 Violation Sections",
                      style={
                          'textAlign': 'center',
                          'fontWeight': 'bold',
                          'fontSize': 14,
                          'color': 'black',
                          'fontFamily':'Sans-Serif'
                      }),
            html.Table([
                html.Thead(html.Tr([
                    html.Th('Section', style={'padding': '8px', 'textAlign': 'left', 'backgroundColor': '#f8f9fa', 'fontSize': '12px', 'width': '70%', 'fontFamily': 'monospace'}),
                    html.Th('Count', style={'padding': '8px', 'textAlign': 'right', 'backgroundColor': '#f8f9fa', 'fontSize': '12px', 'width': '15%', 'fontFamily': 'monospace'}),
                    html.Th('%', style={'padding': '8px', 'textAlign': 'right', 'backgroundColor': '#f8f9fa', 'fontSize': '12px', 'width': '15%', 'fontFamily': 'monospace'})
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(
                            row['Section'],
                            style={
                                'padding': '8px', 
                                'borderBottom': '1px solid #e9ecef',
                                'fontSize': '10px',
                                'lineHeight': '1.2',
                                'wordWrap': 'break-word',
                                'fontFamily': 'monospace',
                                'color': '#6c757d'
                            }
                        ),
                        html.Td(
                            f"{row['Count']:,}", 
                            style={
                                'padding': '8px', 
                                'textAlign': 'right', 
                                'borderBottom': '1px solid #e9ecef',
                                'fontSize': '10px',
                                'whiteSpace': 'nowrap',
                                'fontFamily': 'monospace',
                                'color': '#6c757d'
                            }
                        ),
                        html.Td(
                            f"{row['Percentage']}%", 
                            style={
                                'padding': '8px', 
                                'textAlign': 'right', 
                                'borderBottom': '1px solid #e9ecef',
                                'fontSize': '10px',
                                'whiteSpace': 'nowrap',
                                'fontFamily': 'monospace',
                                'color': '#6c757d'
                            }
                        )
                    ]) for i, row in section_counts.iterrows()
                ])
            ], style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'tableLayout': 'fixed',
                'backgroundColor': 'white'
            })
        ], style={
            'height': '280px',
            'overflowY': 'auto',
            'padding': '10px',
            
        })
        
@callback(
    [Output('avg-stops', 'children'),
     Output('avg-fine', 'children'),
     Output('search-rate', 'children'),
     Output('violation-rate', 'children'),
     Output('court-rate', 'children')],
    [Input('race-filter', 'value'),
     Input('gender-filter', 'value')]
)
def update_kpis(selected_race, selected_gender):
   
    filtered_df = processed_df.copy()
    
    if selected_race != 'all':
        filtered_df = filtered_df[filtered_df['Race'] == selected_race]
    if selected_gender != 'all':
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
  
    stops_by_demographic = filtered_df.groupby(['Race', 'Gender', 'Year', 'Month']).size().reset_index(name='stops')
    avg_stops = stops_by_demographic['stops'].mean()
    
    
    avg_fine = filtered_df['Total_Fine'].mean()
    

    total_stops = len(filtered_df)
    search_rate = (filtered_df['Search Conducted'].fillna('No').eq('Yes').sum() / total_stops * 100 
                  if total_stops > 0 else 0)
    
    
    violation_count = filtered_df.groupby(['Date Of Stop', 'Time Of Stop', 'Latitude', 'Longitude']).size().mean()
    violation_rate = (violation_count - 1) * 100
    
    
    original_fines = df.loc[filtered_df.index] 
    court_appearances = (
        ((original_fines['Fine'].astype(str) == 'MA') | 
         (original_fines['Contr.Acc Fine'].astype(str) == 'MA')).sum()
    )
    court_rate = (court_appearances / total_stops * 100 if total_stops > 0 else 0)
    print(court_appearances)
    

    formatted_outputs = [
        f"{avg_stops:.1f}",
        f"${avg_fine:.2f}",
        f"{search_rate:.1f}%",
        f"{violation_rate:.1f}%",
        f"{court_rate:.1f}%"
    ]
    
    return formatted_outputs


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
        # Race Filter
        html.Div([
            html.Label('Race', style={'fontWeight': 'bold', 'fontFamily':'Monospace'}),
            dcc.Dropdown(
                id='race-filter',
                options=[
                    {'label': 'All Races', 'value': 'all'},
                    {'label': 'Asian', 'value': 'ASIAN'},
                    {'label': 'Black', 'value': 'BLACK'},
                    {'label': 'Hispanic', 'value': 'HISPANIC'},
                    {'label': 'White', 'value': 'WHITE'},
                    {'label': 'Other', 'value': 'OTHER'}
                ],
                value='all',
                clearable=False
            )
        ], style={'marginTop': '40px', 'padding': '20px'}),
        
        # Gender Filter
        html.Div([
            html.Label('Gender', style={'fontWeight': 'bold', 'fontFamily':'Monospace'}),
            dcc.Dropdown(
                id='gender-filter',
                options=[
                    {'label': 'All Genders', 'value': 'all'},
                    {'label': 'Male', 'value': 'M'},
                    {'label': 'Female', 'value': 'F'},
                    {'label': 'Unidentified', 'value': 'U'},
                ],
                value='all',
                clearable=False
            )
        ], style={ 'padding': '0px 20px 20px 20px'}),
        
        # Demographics Percentage Checkbox
        html.Div([
            dbc.Checkbox(
                id='demographics-toggle',
                value=False
            ),
            html.Label('Demographics Percentage', 
                      style={'marginLeft': '5px', 'fontSize':'14px', 'fontWeight':'bold', 'fontFamily':'Monospace'}),
        ], style={'marginTop': '20px', 'display': 'flex', 'alignItems': 'center', 'marginLeft': '20px'})
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
    
    # Right Panel
    html.Div([
            # Header
            html.Div([
                html.P("Demographics Analysis Dashboard",
                      style={
                          'textAlign': 'left',
                          'marginLeft': '20px',
                          'paddingTop': '10px',
                          'fontWeight': 'bold',
                          'fontSize': 30,
                          'color': 'black',
                          'fontFamily':'Sans-Serif'
                      })
            ], style={
                'width': '860px',
                'height': '70px',
                'backgroundColor': 'white',
                'position': 'absolute',
                'top': '15px',
                'left': '20px',
                 'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
              'borderRadius':'5px'
            }),
            
            # KPIs Container
            html.Div([
                html.Div([
                    # KPI boxes
                    html.Div([
                        html.P("Average Stops",
                              style={'fontSize': 15, 'margin': 0,'fontFamily':'Monospace'}),
                        html.P(id='avg-stops',
                              style={'fontSize': 24, 'fontWeight': 'bold', 'margin': 0,'fontFamily':'Sans-Serif'})
                    ], style={'flex': 1, 'textAlign': 'center'}),
                    
                    html.Div([
                        html.P("Average Fine Amount",
                              style={'fontSize': 15,  'margin': 0,'fontFamily':'Monospace'}),
                        html.P(id='avg-fine',
                              style={'fontSize': 24, 'fontWeight': 'bold', 'margin': 0,'fontFamily':'Sans-Serif'})
                    ], style={'flex': 1, 'textAlign': 'center'}),
                    
                    html.Div([
                        html.P("Search Con. Rate",
                              style={'fontSize': 15, 'margin': 0, 'fontFamily':'Monospace'}),
                        html.P(id='search-rate',
                              style={'fontSize': 24, 'fontWeight': 'bold', 'margin': 0, 'fontFamily':'Sans-Serif'})
                    ], style={'flex': 1, 'textAlign': 'center'}),
                    
                    html.Div([
                        html.P("Violation Rate",
                              style={'fontSize': 15,  'margin': 0, 'fontFamily':'Monospace'}),
                        html.P(id='violation-rate',
                              style={'fontSize': 24, 'fontWeight': 'bold', 'margin': 0, 'fontFamily':'Sans-Serif'})
                    ], style={'flex': 1, 'textAlign': 'center'}),
                    
                    html.Div([
                        html.P("Court Appear Rate",
                              style={'fontSize': 15,  'margin': 0, 'fontFamily':'Monospace'}),
                        html.P(id='court-rate',
                              style={'fontSize': 24, 'fontWeight': 'bold', 'margin': 0,'fontFamily':'Sans-Serif'})
                    ], style={'flex': 1, 'textAlign': 'center'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '20px'})
            ], style={
                'width': '860px',
                'height': 'auto',
                'backgroundColor': 'white',
                'position': 'absolute',
                'top': '95px',
                'left': '20px',
                 'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
              'borderRadius':'5px'
            }),
         html.Div([
    # Search metric radio buttons (original)
    html.Div([
        dcc.RadioItems(
            id='search-metric-radio',
            options=[
                {'label': ' Search Conducted ', 'value': 'search_conducted'},
                {'label': ' Search Dispotition ', 'value': 'search_disposition'},
                {'label': ' Search Outcome ', 'value': 'search_outcome'}
            ],
            value='search_conducted',
            inline=True,
            className='radio-items',
             style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'width': '100%',
        'padding': '0 20px'
    },
    labelStyle={
        'display': 'flex',
        'alignItems': 'center',
        'marginRight': '10px',
        'gap': '8px',
        'fontSize': '12px',
        'fontWeight': 'bold',
        'fontFamily': 'Monospace'
    }
        ),
    ], style={'textAlign': 'center'}),
    
    # Add demographics radio buttons here
   html.Div([
    dcc.RadioItems(
        id='demographics-radio',
        options=[
            {'label': ' Race ', 'value': 'race'},
            {'label': ' Gender ', 'value': 'gender'}
        ],
        value='race',
        inline=True,
        className='radio-items',
         style={
                    'fontSize': '12px',
                    'fontWeight': 'bold',
                    'fontFamily': 'Monospace',
                    'marginTop':'10px',
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'width': '100%',
                    'padding': '0 20px' 
                },
                  labelStyle={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginRight': '10px',
                    'gap': '8px'
                },
    )
], id='demographics-radio-container', style={'display': 'none'}),
    # Donut chart
    dcc.Graph(
        id='search-donut',
    
        config={'displayModeBar': False}
    )
], style={
    'width': '355px',
    'height': '335px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '205px',
    'left': '20px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
    'borderRadius':'5px'
}),

           html.Div([
    html.Div([
        dcc.RadioItems(
            id='map-type-radio',
            options=[
                {'label': ' State ', 'value': 'state'},
                {'label': ' DL State ', 'value': 'dl_state'},
                {'label': ' Driver State ', 'value': 'driver_state'}
            ],
            value='state',
            inline=True,
            className='radio-items',
             style={
                    'fontSize': '12px',
                    'fontWeight': 'bold',
                    'fontFamily': 'Monospace',
                     'marginTop':'10px',
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'width': '100%',
                    'padding': '0 20px'  
                },
                  labelStyle={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginRight': '10px',
                    'gap': '8px'
                },
        ),
    ], style={'textAlign': 'center'}),
    
    dcc.Graph(
        id='choropleth-map',
        config={'displayModeBar': False}
    )
], style={
    'width': '495px',
    'height': '335px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '205px',
    'left': '385px',
     'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
    'borderRadius':'5px'
}),
        html.Div([
            dcc.Graph(
                id='radar-chart',
                config={'displayModeBar': False}
            )
        ], style={
            'width': '410px',
            'height': '330px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '550px',
            'left': '20px',
             'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
    'borderRadius':'5px'
        }),

html.Div([
    dcc.RadioItems(
        id='display-type-radio',
        options=[
            {'label': ' Arrest Type ', 'value': 'arrest_type'},
            {'label': ' Section ', 'value': 'section'}
        ],
        value='arrest_type',
        inline=True,
        className='radio-items',
         style={
                    'fontSize': '12px',
                    'fontWeight': 'bold',
                    'fontFamily': 'Monospace',
                    'display': 'flex',
                     'marginTop':'10px',
                    'justifyContent': 'space-between',
                    'width': '100%',
                    'padding': '0 20px' 
                },
                  labelStyle={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginRight': '10px',
                    'gap': '8px'
                },
    ),
    html.Div(id='display-content')
], style={
    'width': '440px',
    'height': '330px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '550px',
    'left': '440px',
    'padding': '10px',
      'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
    'borderRadius':'5px'
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
        })
    ], style={
        'display': 'flex',
        'width': '1200px',
        'height': '1080px',
        'backgroundColor': 'white',
        'margin': '0 auto',
    })



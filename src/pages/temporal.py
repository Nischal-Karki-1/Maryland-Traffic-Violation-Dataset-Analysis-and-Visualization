from dash import register_page, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from datetime import datetime
from .filtercomponent import create_filter_panel, apply_filters


register_page(__name__, path='/temporal', name='temporal')

def categorize_time(hour):
    
    if 5 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 22:
        return 'Evening'
    else:
        return 'Night'
    
def get_season(date):
    month = date.month
    day = date.day
    
    if month == 12 or month <= 3:
        return 'Winter'
    elif month == 4 or month == 5 or (month == 6 and day < 21):
        return 'Spring'
    elif (month == 6 and day >= 21) or month == 7 or month == 8 or (month == 9 and day < 21):
        return 'Summer'
    else:
        return 'Autumn'

def preprocess_data(df):

   
    df['Date Of Stop'] = pd.to_datetime(df['Date Of Stop'], format='%m/%d/%Y', errors='coerce')
    df['Year'] = df['Date Of Stop'].dt.year
    df['Month'] = df['Date Of Stop'].dt.month
    df['Month_Name'] = df['Date Of Stop'].dt.strftime('%B')
    df['Day'] = df['Date Of Stop'].dt.day
    df['Hour'] = pd.to_datetime(df['Time Of Stop']).dt.hour
    df['DayOfWeek'] = df['Date Of Stop'].dt.dayofweek
    df['TimePeriod'] = df['Hour'].apply(categorize_time)
    df['Season'] = df['Date Of Stop'].apply(get_season)

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
 
    df = df.dropna(subset=['Date Of Stop'])
    
    return df

@callback(
    [Output('device-violation', 'children'),
     Output('non-device-violation', 'children')],
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('weekday-toggle', 'value'),
     Input('weekend-toggle', 'value')]
)
def update_kpi_boxes(selected_year, selected_month, selected_states, weekday_filter, weekend_filter):
    filtered_df = apply_filters(processed_df, selected_year, selected_month, selected_states)
    
    
    device_violations = filtered_df[filtered_df['Section'] == 'Unknown Section']
    top_device = device_violations['Charge Description'].mode().iloc[0]
    device_count = len(device_violations[device_violations['Charge Description'] == top_device])
    
  
    non_device = filtered_df[filtered_df['Section'] != 'Unknown Section']
    top_non_device = non_device['Section'].mode().iloc[0]
    non_device_count = len(non_device[non_device['Section'] == top_non_device])
    
    device_box = html.Div([
        html.H6('Top Device Violation', 
                style={'fontSize': '12px', 'fontWeight': 'bold', 'marginBottom': '7px', 'fontFamily': 'Monospace'}),
        html.P(f"{device_count:,}",
               style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#3B3F46', 'fontFamily': 'Sans-Serif', 'textAlign': 'center', 'marginBottom': '2px'}),
        html.P(top_device,
               style={'fontSize': '16px',  'fontFamily': 'Monospace','fontWeight': 'bold',  'wordWrap': 'break-word', 'textAlign': 'center', 'marginBottom': '5px'}),
    ])
    
    non_device_box = html.Div([
        html.H6('Top Non-Device Violation',
                style={'fontSize': '12px', 'fontWeight': 'bold', 'marginBottom': '7px', 'fontFamily': 'Monospace'}),
        html.P(f"{non_device_count:,}",
               style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#3B3F46', 'fontFamily': 'Sans-Serif', 'textAlign': 'center', 'marginBottom': '2px'}),
        html.P(top_non_device,
               style={'fontSize': '16px',  'fontFamily': 'Monospace','fontWeight': 'bold',  'wordWrap': 'break-word', 'textAlign': 'center', 'marginBottom': '5px'}),
    ])
    
    return device_box, non_device_box

@callback(
    Output('gender-distribution', 'figure'),
    [Input('violation-type-radio', 'value'),
     Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('weekday-toggle', 'value'),
     Input('weekend-toggle', 'value')]
)
def update_gender_distribution(violation_type, selected_year, selected_month, 
                             selected_states, weekday_filter, weekend_filter):
    filtered_df = apply_filters(processed_df, selected_year, selected_month, selected_states)
    
    day_filters = []
    if weekday_filter:
        day_filters.extend([0, 1, 2, 3, 4])
    if weekend_filter:
        day_filters.extend([5, 6])
    
    if day_filters:
        filtered_df = filtered_df[filtered_df['DayOfWeek'].isin(day_filters)]
    
    if violation_type == 'device':
        violations_df = filtered_df[filtered_df['Section'] == 'Unknown Section']
    else:
        violations_df = filtered_df[filtered_df['Section'] != 'Unknown Section']
    
    top_violations = violations_df['Charge Description'].value_counts().nlargest(5).index
    
    male_counts = []
    female_counts = []
    
    for violation in top_violations:
        violation_data = violations_df[violations_df['Charge Description'] == violation]
        male_count = len(violation_data[violation_data['Gender'] == 'M'])
        female_count = len(violation_data[violation_data['Gender'] == 'F'])
        male_counts.append(male_count)
        female_counts.append(female_count)
    
    short_labels = [v[:20] + '...' if len(v) > 20 else v for v in top_violations]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=short_labels,
        x=[-x for x in male_counts],
        orientation='h',
        name='Male',
        marker_color='#4287F5',
        text=male_counts,
        textposition='outside',
         marker=dict(cornerradius=5)
    ))
    
    fig.add_trace(go.Bar(
        y=short_labels,
        x=female_counts,
        orientation='h',
        name='Female',
        marker_color='#ff4444',
        text=female_counts,
        textposition='outside',
        marker=dict(cornerradius=5)
    ))
    
    max_value = max(max(male_counts), max(female_counts))
    
    title_text = 'Gender Distribution by ' + ('Device Violations' if violation_type == 'device' else 'Non-Device Violations')
    
    fig.update_layout(
        title=dict(
            text=title_text,
            x=0.5,
            xanchor='center',
            y=0.97,
            yanchor='top',
            font=dict(size=14, weight='bold',family='Sans-Serif', color='black')
        ),
        barmode='relative',
        bargap=0.2,
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=200,
        margin=dict(l=40, r=40, t=50, b=50),
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.15,
            xanchor='right',
            x=0.85
        ),
        xaxis=dict(
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1,
            range=[-max_value, max_value],
            tickmode='array',
            tickvals=[-max_value, -max_value/2, 0, max_value/2, max_value],
            ticktext=[str(max_value), str(int(max_value/2)), '0', str(int(max_value/2)), str(max_value)]
        ),
        yaxis=dict(
            tickfont=dict(size=8, weight='bold')
        )
    )
    
    return fig


@callback(
    Output('stacked-area', 'figure'),
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('weekday-toggle', 'value'),
     Input('weekend-toggle', 'value')]
)
def update_stacked_area(selected_year, selected_month, selected_states, 
                       weekday_filter, weekend_filter):
   
    filtered_df = apply_filters(processed_df, selected_year, selected_month, selected_states)
    
    
    day_filters = []
    if weekday_filter:
        day_filters.extend([0, 1, 2, 3, 4])
    if weekend_filter:
        day_filters.extend([5, 6])
    
    if day_filters:
        filtered_df = filtered_df[filtered_df['DayOfWeek'].isin(day_filters)]
    
    belts_violations = filtered_df[filtered_df['Belts'] == 'No']
    alcohol_violations = filtered_df[filtered_df['Alcohol'] == 'Yes']
    
    belts_monthly = belts_violations.groupby('Month_Name').size().reset_index(name='Belts')
    alcohol_monthly = alcohol_violations.groupby('Month_Name').size().reset_index(name='Alcohol')

    monthly_data = pd.merge(belts_monthly, alcohol_monthly, on='Month_Name', how='outer').fillna(0)
    
  
    month_abbrev = {
        'January': 'Jan', 'February': 'Feb', 'March': 'Mar',
        'April': 'Apr', 'May': 'May', 'June': 'Jun',
        'July': 'Jul', 'August': 'Aug', 'September': 'Sep',
        'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
    }
    
    
    month_order = list(month_abbrev.keys())
    monthly_data['Month_Name'] = pd.Categorical(monthly_data['Month_Name'], 
                                              categories=month_order, ordered=True)
    monthly_data = monthly_data.sort_values('Month_Name')
    monthly_data['Month_Name'] = monthly_data['Month_Name'].map(month_abbrev)
    

    fig = go.Figure()
    
  
    categories = [
        ('Belts', 'Seat Belt Violations', '#E63946'),    
        ('Alcohol', 'Alcohol Violations', '#2A9D8F')     
    ]
    
    for col, name, color in categories:
        fig.add_trace(go.Scatter(
            x=monthly_data['Month_Name'],
            y=monthly_data[col],
            name=name,
            mode='lines',
            stackgroup='one',
            line=dict(width=0.5),
            fillcolor=color
        ))
    
   
    fig.update_layout(
        title=dict(
            text='Monthly Traffic Violations Distribution',
            x=0.5,
            y=0.9,
            xanchor='center',
            yanchor='top',
            font=dict(size=14, weight= 'bold', family='Sans-Serif', color='black')
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title=dict(text='Month', font=dict(size=10, weight='bold')),
            tickangle=45
        ),
        yaxis=dict(
            title=dict(text='Number of Violations', font=dict(size=10, weight='bold')),
        ),
        height=180,  
        margin=dict(l=40, r=40, t=50, b=10), 
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.9,
            xanchor='right',
            x=1
        )
    )
    
    return fig
@callback(
    Output('double-line-graph', 'figure'),
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('weekday-toggle', 'value'),
     Input('weekend-toggle', 'value'),
     Input('single-plot-toggle', 'value')]
)
def update_double_line_graph(selected_year, selected_month, selected_states, 
                           weekday_filter, weekend_filter, single_plot):
 
    filtered_df = apply_filters(processed_df, selected_year, selected_month, selected_states)
    
   
    day_filters = []
    if weekday_filter:
        day_filters.extend([0, 1, 2, 3, 4])
    if weekend_filter:
        day_filters.extend([5, 6])
    
    if day_filters:
        filtered_df = filtered_df[filtered_df['DayOfWeek'].isin(day_filters)]
    
    filtered_df['Hour'] = pd.to_datetime(filtered_df['Time Of Stop']).dt.hour
    
    device_defects = filtered_df[filtered_df['Section'] == 'Unknown Section'].groupby('Hour').size()
    non_device_defects = filtered_df[filtered_df['Section'] != 'Unknown Section'].groupby('Hour').size()
    
   
    hours = list(range(24))
    device_defects = device_defects.reindex(hours, fill_value=0)
    non_device_defects = non_device_defects.reindex(hours, fill_value=0)
    
    fig = go.Figure()
    
    if single_plot:
     
        total_violations = device_defects + non_device_defects
        fig.add_trace(go.Scatter(
            x=hours,
            y=total_violations,
            mode='lines+markers',
            name='Total Violations',
            line=dict(color='#26547c', width=2), 
            marker=dict(size=6)
        ))
    else:
       
        fig.add_trace(go.Scatter(
            x=hours,
            y=device_defects,
            mode='lines+markers',
            name='Device Defect Violations',
            line=dict(color='#ef476f', width=2),  
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=hours,
            y=non_device_defects,
            mode='lines+markers',
            name='Non-Device Defect Violations',
            line=dict(color='#ffd166', width=2),  
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title=dict(
            text='Hourly Distribution of Violations',
            font=dict(
                family='Sans-Serif',
                size=14,
                color='black',
                weight='bold'
            ),
            x=0.5,
            y=0.85
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title=dict(
                text='Hour of Day', 
                font=dict(
                  
                    size=10, 
                    weight='bold'
                )
            ),
            tickmode='linear',
            tick0=0,
            dtick=2,
            range=[-0.5, 23.5]
        ),
        yaxis=dict(
            title=dict(
                text='Number of Violations', 
                font=dict(
                  
                    size=10, 
                    weight='bold'
                )
            ),
        ),
        height=300,
        margin=dict(l=40, r=40, t=60, b=40),  
        showlegend=False,  
       
    )
    
    return fig

@callback(
    Output('seasonal-chart', 'figure'),
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('weekday-toggle', 'value'),
     Input('weekend-toggle', 'value'),
     Input('metric-radio', 'value')]
)
def update_seasonal_chart(selected_year, selected_month, selected_states, 
                         weekday_filter, weekend_filter, selected_metric):
   
    filtered_df = apply_filters(processed_df, selected_year, selected_month, selected_states)
    
 
    day_filters = []
    if weekday_filter:
        day_filters.extend([0, 1, 2, 3, 4])
    if weekend_filter:
        day_filters.extend([5, 6])
    
    if day_filters:
        filtered_df = filtered_df[filtered_df['DayOfWeek'].isin(day_filters)]
    
    
    if selected_metric == 'violation':
        seasonal_data = filtered_df.groupby('Season').size()
    elif selected_metric == 'accident':
        seasonal_data = filtered_df[filtered_df['Accident'] == 'Yes'].groupby('Season').size()
    elif selected_metric == 'contributed_accident':
        seasonal_data = filtered_df[filtered_df['Contributed To Accident'] == True].groupby('Season').size()
    else:  
        seasonal_data = filtered_df.groupby('Season')['Total_Fine'].mean()
    
   
    season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
    seasonal_data = seasonal_data.reindex(season_order)
    
  
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=season_order,
        y=seasonal_data.values,
        mode='lines+markers',
        line=dict(color='rgb(66, 135, 245)', width=2),
        marker=dict(size=8, color='rgb(8, 81, 156)')
    ))
    

    title_text = {
        'violation': 'Seasonal Distribution of Violations',
        'accident': 'Seasonal Distribution of Accidents',
        'contributed_accident': 'Seasonal Distribution of Contributed Accidents',
        'fine': 'Average Fine Amount by Season'
    }
    
    y_axis_title = {
        'violation': 'Number of Violations',
        'accident': 'Number of Accidents',
        'contributed_accident': 'Number of Contri. Accidents',
        'fine': 'Average Fine Amount ($)'
    }
    
    fig.update_layout(
        title=dict(
            text=title_text[selected_metric],
            font=dict(size=14, weight='bold', family= 'Sans-Serif', color='black'),
            x=0.5,
            y=0.95
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title=dict(text='Season', font=dict(size=10, weight='bold')),
          
            
        ),
        yaxis=dict(
            title=dict(text=y_axis_title[selected_metric], font=dict(size=10, weight='bold')),
        
            showgrid=True
        ),
        height=180,
        margin=dict(l=40, r=40, t=40, b=40)  
    )
    
    return fig

@callback(
    [Output('injury-chart', 'figure'),
     Output('fatal-chart', 'figure')],
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('weekday-toggle', 'value'),
     Input('weekend-toggle', 'value')]
)
def update_gauge_charts(selected_year, selected_month, selected_states, 
                       weekday_filter, weekend_filter):
    filtered_df = apply_filters(processed_df, selected_year, selected_month, selected_states)
    

    day_filters = []
    if weekday_filter:
        day_filters.extend([0, 1, 2, 3, 4])
    if weekend_filter:
        day_filters.extend([5, 6])
    
    if day_filters:
        filtered_df = filtered_df[filtered_df['DayOfWeek'].isin(day_filters)]
    
    
    total_accidents = len(filtered_df[filtered_df['Accident'] == 'Yes'])
    injury_count = len(filtered_df[filtered_df['Personal Injury'] == 'Yes'])
    fatal_count = len(filtered_df[filtered_df['Fatal'] == 'Yes'])
    
   
    injury_percentage = (injury_count / total_accidents * 100) if total_accidents > 0 else 0
    fatal_percentage = (fatal_count / total_accidents * 100) if total_accidents > 0 else 0

    def create_gauge_chart(percentage, count, title, is_injury=True):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=count,  
            gauge={
                'axis': {'range': [0, total_accidents], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': "#ff4444"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "black",
                'steps': [
                    {'range': [0, total_accidents/3], 'color': '#ffebee'},
                    {'range': [total_accidents/3, 2*total_accidents/3], 'color': '#ffcdd2'},
                    {'range': [2*total_accidents/3, total_accidents], 'color': '#ef9a9a'}
                ],
            },
            number={
                'font': {'size': 24, 'family': 'Sans-Serif', 'weight': 'bold'},
                'valueformat': "," 
            },
            domain={'y': [0.15, 0.85], 'x': [0, 1]}
        ))

        fig.update_layout(
            paper_bgcolor='white',
            margin=dict(l=5, r=5, t=15, b=5),
            height=100,
            
            
            annotations=[
                dict(
                    text=title,
                    x=0.5,
                    y=0.15,
                    showarrow=False,
                    font=dict(size=12, family='Monospace', weight='bold'),
                    yanchor='top'
                ),
                dict(
                    text=f"{percentage:.1f}% of Accidents",
                    x=0.5,
                    y=-0.1,
                    showarrow=False,
                    font=dict(size=10, family='Monospace'),
                    yanchor='top'
                )
            ]
        )
        
        return fig
    
    injury_fig = create_gauge_chart(injury_percentage, injury_count, "Personal Injury", True)
    fatal_fig = create_gauge_chart(fatal_percentage, fatal_count, "Fatal", False)
    
    return injury_fig, fatal_fig

@callback(
    Output('top-right-chart', 'figure'),
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('state-filter', 'value'),
     Input('weekday-toggle', 'value'),
     Input('weekend-toggle', 'value'),
     Input('plot-type-toggle', 'value')]
)
def update_temporal_visualization(selected_year, selected_month, selected_states, 
                                weekday_filter, weekend_filter, show_boxplot):
    
    filtered_df = apply_filters(processed_df, selected_year, selected_month, selected_states)
    
    
    day_filters = []
    if weekday_filter:
        day_filters.extend([0, 1, 2, 3, 4])
    if weekend_filter:
        day_filters.extend([5, 6])
    
    if day_filters:
        filtered_df = filtered_df[filtered_df['DayOfWeek'].isin(day_filters)]
    
    
    period_order = ['Morning', 'Afternoon', 'Evening', 'Night']
    

    title_parts = []
    if selected_year:
        title_parts.append(f"Year: {selected_year}")
    if selected_month:
        title_parts.append(f"Month: {selected_month}")
    if selected_states:
        title_parts.append(f"States: {', '.join(selected_states)}")
    
    filter_text = ' | '.join(title_parts) if title_parts else 'All Data'
    
    if show_boxplot:
     
        fig = go.Figure()
        
        for period in period_order:
            period_data = filtered_df[filtered_df['TimePeriod'] == period]['Hour']
            
            fig.add_trace(go.Box(
                y=period_data,
                name=period,
                boxpoints='outliers',
                fillcolor='rgb(66, 135, 245)',  
                line=dict(color='rgb(8, 81, 156)'),  
                marker=dict(color='rgb(8, 81, 156)')  
            ))
        
        fig.update_layout(
            title=dict(
                text=f'Distribution of Stop Times by Period',
                font=dict(size=14, weight= 'bold', family='Sans-Serif'),
                y=0.8,
                x=0.5,
                xanchor='center',
                yanchor='top'
            ),
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            yaxis=dict(
                title=dict(text='Hour of day', font=dict(size=10, weight='bold')),
                range=[0, 24],
                tickmode='linear',
                tick0=0,
                dtick=4
            ),
            xaxis=dict(
                title=dict(text='Time Period', font=dict(size=10, weight='bold')),
            ),
            height=285,
            margin=dict(l=40, r=40, t=100, b=40)
        )
    else:
    
        period_counts = filtered_df['TimePeriod'].value_counts().reindex(period_order).fillna(0)
        
        
        fig = go.Figure(data=[
            go.Bar(
                x=period_counts.index,
                y=period_counts.values,
                textposition='auto',
                width=0.7,  
                marker_color='rgb(66, 135, 245)',
                marker=dict(cornerradius=5)  
            )
        ])
        
        fig.update_layout(
            title=dict(
                text=f'Number of Stops by Time Period',
                font=dict(size=14, weight= 'bold', family='Sans-Serif', color='black'),
                y=0.8,
                x=0.5,
                xanchor='center',
                yanchor='top'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            bargap=0.2,  
            xaxis=dict(
                title=dict(text='Time Period', font=dict(size=10, weight='bold')),
            ),
            yaxis=dict(
                title=dict(text='Number of Stops', font=dict(size=10, weight='bold')),
            ),
            height=285,
             margin=dict(l=40, r=40, t=100, b=40)
        )
    
    return fig


df = pd.read_csv("Maryland_Traffic_Violation.csv")
processed_df = preprocess_data(df)
processed_df['County'] = 'Montgomery'


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
                'marginBottom': '30px'
            }
        ),
        html.Div(
            create_filter_panel(processed_df),
            style={'padding': '10px'}
        ),
        html.Div([
            html.Div([
                dbc.Checkbox(
                    id='weekday-toggle',
                    value=True
                ),
                html.Label('Weekdays (Mon-Fri)', 
                          style={'marginLeft': '5px', 'fontSize': '14px', 'fontWeight': 'bold', 'fontFamily': 'Monospace'}),
            ], style={'marginTop': '20px', 'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                dbc.Checkbox(
                    id='weekend-toggle',
                    value=True
                ),
                html.Label('Weekends (Sat-Sun)', 
                          style={'marginLeft': '5px', 'fontSize': '14px', 'fontWeight': 'bold', 'fontFamily': 'Monospace'}),
            ], style={'marginTop': '10px', 'display': 'flex', 'alignItems': 'center'}),
        ], style={'marginTop': '20px'})
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
            html.P("Temporal Analysis Dashboard",
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
            dbc.Checkbox(
                id='plot-type-toggle',
                value=False,
                style={'marginRight': '8px'}
            ),
            html.Label('Show Box Plot', 
                      style={'fontSize': '12px', 'fontWeight': 'bold', 'fontFamily':'Monospace', }),
        ], style={
            'position': 'absolute',
            'top': '105px',
            'left': '485px',
            'zIndex': '1',
            'display': 'flex',
            'alignItems': 'center',
            'backgroundColor': 'white',
            'padding': '5px',
        
        }),
        
        
        html.Div([
            dcc.Graph(
                id='top-right-chart',
                config={'displayModeBar': False}
            )
        ], style={
            'width': '400px',
            'height':'295px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '95px',
            'left': '480px',
             'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
        }),

        html.Div([
            html.Div([
        html.Div([
        dcc.RadioItems(
            id='metric-radio',
            options=[
                {'label': 'Violations', 'value': 'violation'},
                {'label': 'Accidents', 'value': 'accident'},
                {'label': 'Contr. Accidents', 'value': 'contributed_accident'},
                {'label': 'Fines', 'value': 'fine'}
            ],
            value='violation',
           inline=False,  
                className='radio-group',
                style={
                    'fontSize': '12px',
                    'fontWeight': 'bold',
                    'fontFamily': 'Monospace',
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
        ], style={
            'width': '100%',  
            'padding': '10px'
        }),
        dcc.Graph(
            id='seasonal-chart',
            config={'displayModeBar': False}
        )
    ])
           
        ], style={
            
            'width': '450px',
            'height': '210px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '95px',
            'left': '20px',
            'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
              'borderRadius':'5px'
        }),
        #Middle Left
       
            html.Div([
    html.Div(id='device-violation')
], style={
    'width': '225px',
    'height': '95px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '325px',
    'left': '20px',
    'padding': '10px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
    'borderRadius':'5px'
}),

html.Div([
    html.Div(id='non-device-violation')
], style={
    'width': '215px',
    'height': '95px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '325px',
    'left': '255px',
    'padding': '10px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
    'borderRadius':'5px'
}),
#Bottom Left
 html.Div([
    dcc.RadioItems(
        id='violation-type-radio',
        options=[
            {'label': 'Device Violations', 'value': 'device'},
            {'label': 'Non-Device Violations', 'value': 'non-device'}
        ],
        value='device',
        style={'fontFamily': 'Monospace', 'fontWeight': 'bold', 'fontSize':'12px', 'display':'flex', 'alignItems':'center',  'justifyContent': 'space-between',
                    'width': '100%',
                    'padding': '10px 20px'  },
        labelStyle={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginRight': '15px',
                    'gap': '8px'
                },
    ),
    
    dcc.Graph(
        id='gender-distribution',
        config={'displayModeBar': False}
    )
], style={
    'width': '450px',
    'height': '230px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '430px',
    'left': '20px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
    'borderRadius':'5px'
}),
 
 #Bottom left left
html.Div([
    dcc.Graph(
        id='stacked-area',
        config={'displayModeBar': False}
    )
], style={
    'width': '450px',
    'height': '200px',
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '680px',
    'left': '20px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
    'borderRadius':'5px'
}),
# Double line graph
           html.Div([
    # Single plot toggle
    html.Div([
        dbc.Checkbox(
            id='single-plot-toggle',
            value=False,
            style={'marginRight': '8px'}
        ),
        html.Label('Single Plot', 
                  style={'fontSize': '12px', 'fontWeight': 'bold', 'fontFamily': 'Monospace'}),
    ], style={
        'position': 'absolute',
        'top': '575px',
        'left': '485px',
        'zIndex': '1',
        'display': 'flex',
        'alignItems': 'center',
        'backgroundColor': 'white',
        'padding': '5px',
        
    }),
    
    # Graph
    html.Div([
        dcc.Graph(
            id='double-line-graph',
            config={'displayModeBar': False}
        )
    ], style={
        'width': '400px',
        'height':'310px',
        'backgroundColor': 'white',
        'position': 'absolute',
        'top': '570px',
        'left': '480px',
        'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
    'borderRadius':'5px'
    })
]),

html.Div([
    # Title div
    html.Div([
        html.H6("Road Safety Metrics",
                style={
                    'fontSize': '14px', 
                    'fontWeight': 'bold', 
                    'fontFamily': 'Sans-Serif',
                    'margin': '0px',
                    'padding': '10px',
                    'textAlign': 'center'
                })
    ]),
    
    # Gauge charts container
    html.Div([
        html.Div([
            dcc.Graph(
                id='injury-chart',
                config={'displayModeBar': False}
            )
        ], style={'display': 'inline-block', 'width': '50%'}),
        
        html.Div([
            dcc.Graph(
                id='fatal-chart',
                config={'displayModeBar': False}
            )
        ], style={'display': 'inline-block', 'width': '50%'})
    ], style={
        'display': 'flex',
        'padding': '5px',
        'alignItems': 'center',
        'justifyContent': 'space-between'
    })
], style={
    'width': '400px',
    'height': '160px',  
    'backgroundColor': 'white',
    'position': 'absolute',
    'top': '400px',
    'left': '480px',
    'padding': '5px',
    'borderRadius':'5px',
    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)'
})
            

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
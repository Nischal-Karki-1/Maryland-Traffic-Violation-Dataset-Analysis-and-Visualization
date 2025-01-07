from dash import html, dcc


def create_year_filter(df, filter_id='year-filter'):
    return html.Div([
        html.Label('Select Year', 
                  style={'fontWeight': 'bold', 
                       
                        'display': 'block',
                        'fontFamily':'Monospace'}),
        dcc.Dropdown(
            id=filter_id,
            options=[{'label': 'All Years', 'value': 'all'}] + [
                {'label': str(year), 'value': year}
                for year in sorted(df['Year'].unique())
            ],
            value='all',
            style={'width': '100%'}
        )
    ], style={'marginBottom': '20px'})

def create_month_filter(filter_id='month-filter'):
    return html.Div([
        html.Label('Select Month', 
                  style={'fontWeight': 'bold', 
                     
                        'display': 'block',
                        'fontFamily':'Monospace'}),
        dcc.Dropdown(
            id=filter_id,
            options=[{'label': 'All Months', 'value': 'all'}] + [
                {'label': month, 'value': str(i)}
                for i, month in enumerate(
                    ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December'], 1
                )
            ],
            value='all',
            style={'width': '100%'}
        )
    ], style={'marginBottom': '20px'})

def create_state_filter(df, filter_id='state-filter'):
    return html.Div([
        html.Label('Driver State', 
                style={'fontWeight': 'bold', 
                     
                      'display': 'block',
                      'fontFamily':'Monospace'}),
        dcc.Dropdown(
            id=filter_id,
            options=[{'label': 'All States', 'value': 'all'}] + [
                {'label': state, 'value': state}
                for state in sorted(df['Driver State'].unique())
            ],
            value=['all'],
            multi=True,
            style={'width': '100%'},
            placeholder='Select states...'
        )
    ])

def create_filter_panel(df):
    return html.Div([
        
        
        html.Div([
            create_year_filter(df),
            create_month_filter(),
            create_state_filter(df)
        ], style={'padding': '10px'})
    ],
 )

def apply_filters(df, selected_year, selected_month, selected_states):
    filtered_df = df.copy()
    
    if selected_year != 'all':
        filtered_df = filtered_df[filtered_df['Year'] == selected_year]
    if selected_month != 'all':
        filtered_df = filtered_df[filtered_df['Month'] == int(selected_month)]
    if 'all' not in selected_states:
        filtered_df = filtered_df[filtered_df['Driver State'].isin(selected_states)]
        
    return filtered_df
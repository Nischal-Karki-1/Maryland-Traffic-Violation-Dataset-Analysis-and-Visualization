from dash import register_page, html, dcc, callback, Output, Input, no_update
import joblib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random


register_page(__name__, path='/price', name='price')


model_dict = joblib.load('fine_prediction_model.joblib')

def get_model_metrics():
    """Extract model metrics from the loaded model dictionary"""
    
    macro_metrics = model_dict['performance']['macro avg']
    weighted_metrics = model_dict['performance']['weighted avg']
    metrics = {
        'Precision': macro_metrics['precision'],
        'Recall': macro_metrics['recall'],
        'F1 Score': macro_metrics['f1-score'],
        'Support': macro_metrics['f1-score']/1000,
        'Accuracy': model_dict['performance']['accuracy'], 
        
    }
    return metrics



def clean_fine(value):

    if pd.isna(value) or value == 'MA':
        return 0
    cleaned = str(value).replace('$', '').replace('MA', '').replace(',', '').strip()
    return float(cleaned or 0)

def convert_yes_no_to_bool(value):
    
    if isinstance(value, str):
        return value.lower() == 'yes'
    return bool(value)

def load_and_clean_data(df):
    
    df['Date Of Stop'] = pd.to_datetime(df['Date Of Stop'], format='%m/%d/%Y')
    df['Fine'] = df['Fine'].apply(clean_fine)
    df['Contr.Acc Fine'] = df['Contr.Acc Fine'].apply(clean_fine)
    df['Total_Fine'] = df.apply(
        lambda row: row['Contr.Acc Fine'] if row['Contributed To Accident'] == True
        else row['Fine'], axis=1
    )
    return df

def predict_fine_category(input_data):
  
    required_fields = [
        'Description', 'Time Of Stop', 'Latitude', 'Longitude', 'Points',
        'Accident', 'Personal Injury', 'Property Damage', 'Fatal', 
        'Work Zone', 'Alcohol', 'HAZMAT', 'Commercial License', 
        'Commercial Vehicle', 'VehicleType', 'Violation Type', 
        'Make', 'Color', 'Driver State', 'DL State', 
        'Manufacture Year', 'SubAgency'
    ]
    
    missing_fields = [field for field in required_fields if field not in input_data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")
    
   
    for col in model_dict['boolean_columns']:
        input_data[col] = convert_yes_no_to_bool(input_data[col])

  
    input_df = pd.DataFrame([input_data])
    
  
    input_df['Time_Hour'] = pd.to_datetime(input_df['Time Of Stop']).dt.hour
    input_df['Time_Period'] = pd.cut(
        input_df['Time_Hour'],
        bins=[0, 6, 12, 18, 24],
        labels=['Night', 'Morning', 'Afternoon', 'Evening']
    )

   
    location_data = input_df[['Latitude', 'Longitude']].values
    input_df['Location_Cluster'] = model_dict['location_model'].predict(location_data)

    
    severity_columns = model_dict['boolean_columns'][:7]  
    for col in severity_columns:
        input_df[f'{col}_Flag'] = input_df[col].astype(int)

    input_df['Severity_Score'] = input_df[[f'{col}_Flag' for col in severity_columns]].sum(axis=1)

   
    input_df['Is_Commercial'] = (
        input_df['Commercial License'] |
        input_df['Commercial Vehicle']
    ).astype(int)

    input_df['Is_Local'] = (
        input_df['Driver State'] ==
        input_df['DL State']
    ).astype(int)

   
    for col, le in model_dict['label_encoders'].items():
        try:
            input_df[f'{col}_Encoded'] = le.transform(input_df[col].astype(str))
        except ValueError:
           
            input_df[f'{col}_Encoded'] = le.transform([le.classes_[0]])

 
    current_year = pd.Timestamp.now().year
    input_df['Vehicle_Age'] = current_year - pd.to_numeric(
        input_df['Manufacture Year'], 
        errors='coerce'
    ).fillna(current_year)

   
    description_features = model_dict['tfidf'].transform(input_df['Description'].fillna(''))
    description_df = pd.DataFrame(
        description_features.toarray(),
        columns=[f'desc_{i}' for i in range(description_features.shape[1])]
    )

    
    base_features = [
        'Time_Hour',
        'Location_Cluster',
        'Severity_Score',
        'Is_Commercial',
        'Is_Local',
        'Points',
        'Vehicle_Age',
        'Violation Type_Encoded',
        'VehicleType_Encoded',
        'SubAgency_Encoded',
        'Make_Encoded',
        'Color_Encoded'
    ] + [f'{col}_Flag' for col in severity_columns]

    X = pd.concat([
        input_df[base_features],
        description_df
    ], axis=1)

  
    X_scaled = model_dict['scaler'].transform(X.fillna(0))
    prediction = model_dict['model'].predict(X_scaled)
    probabilities = model_dict['model'].predict_proba(X_scaled)

  
    prob_dict = {
        class_name: prob
        for class_name, prob in zip(model_dict['classes'], probabilities[0])
    }

    prediction_details = {
        'predicted_category': prediction[0],
        'confidence': np.max(probabilities),
        'class_probabilities': prob_dict,
        'severity_risk': input_df['Severity_Score'].iloc[0] / len(severity_columns),
        'risk_factors': [
            col for col in severity_columns
            if input_df[f'{col}_Flag'].iloc[0] == 1
        ],
        'location_cluster': input_df['Location_Cluster'].iloc[0],
        'commercial_vehicle': bool(input_df['Is_Commercial'].iloc[0]),
        'points': input_data['Points'],
        'time_period': input_df['Time_Period'].iloc[0]
    }

    return prediction[0], prediction_details

# Read and process the dataset
df = pd.read_csv('Maryland_Traffic_Violation_2025.csv')
df = load_and_clean_data(df)





layout = html.Div([
    # Left Panel
    html.Div([
        html.Img(
            src='assets/Countylogo.png',
            alt='County Logo',
            style={
                'display': 'block',
                'margin': '0 auto',
                'width': '80%',
                'height': 'auto',
                'marginBottom': '90px'
            }
        ),
       html.Button(
    'Generate New Prediction',
    id='generate-prediction-btn',
    style={
        'backgroundColor': '#4CAF50',
        'color': 'white',
        'padding': '10px 20px',
        'border': 'none',
        'borderRadius': '4px',
        'cursor': 'pointer',
        'width': '70%',
        'fontSize':'14px',
        'margin': '0 auto',
        'display': 'block',
        'fontFamily': 'Monospace',
        'fontWeight': 'bold'
    }
)
    ], className='left-panel', style={
        'width': '300px',
        'height': '900px',
        'backgroundColor': 'white',
        'padding': '20px',
         'borderTop': '3px solid black',
    'borderBottom': '3px solid black',
    'borderLeft': '3px solid black',
    'border-top-left-radius': '10px',
    'border-bottom-left-radius': '10px',
    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)',
        'marginTop': '5%',
        'float': 'left'
    }),
    
    # Right Panel - Main Content Area
    html.Div([
        # Title Section
        html.Div([
            html.H1("Fine Category Analysis and Prediction Dashboard",
                style={
                    'textAlign': 'left',
                    'marginLeft': '20px',
                    'paddingTop': '10px',
                    'fontSize': '30px',
                    'fontWeight': 'bold'
                }
            )
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
        
        # Table Chart
         html.Div([
             html.Table([
                html.Thead([
                    html.Tr([
                        html.Th('Feature', style={
                            'width': '120px',
                            'textAlign': 'left',
                            'padding': '8px',
                            'backgroundColor': '#f5f5f5',
                            'position': 'sticky',
                            'top': '0',
                            'left': '0',
                            'zIndex': '2',
                            'borderBottom': '1px solid #ddd',
                            'borderRight': '1px solid #ddd'
                        }),
                        html.Th('Value', style={
                            'width': '60px',
                            'textAlign': 'left',
                            'padding': '8px',
                            'backgroundColor': '#f5f5f5',
                            'position': 'sticky',
                            'top': '0',
                            'zIndex': '1',
                            'borderBottom': '1px solid #ddd'
                        })
                    ])
                ]),
                html.Tbody(id='feature-table-body')
            ], style={
                'width': '300px',
                'borderCollapse': 'collapse',
                'border': '1px solid #ddd'
            })
            
        ], style={
            'width': '350px',
            'height': '370px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '95px',
            'left': '20px',
            'borderRadius':'4px',
            'overflowY': 'auto',
            'overflowX': 'hidden',
            'border': '1px solid #ddd',
            'padding': '10px',
        }),
        
        # Confidence Gauge 
        html.Div([
            dcc.Graph(
                id='confidence-gauge',
                style={'height': '120px'}
            )
            
        ], style={
            'width': '245px',
            'height': '150px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '95px',
            'left': '380px',
            'borderRadius':'4px'
        }),
        # Severity Gauge
                html.Div([
                    dcc.Graph(
                id='severity-risk-gauge',
                style={'height': '120px'}
             )
            
        ], style={
            'width': '245px',
            'height': '150px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '95px',
            'left': '635px',
            'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
              'borderRadius':'5px'
        }),
        
        # Class Possibilities Bar Chart
                html.Div([
            dcc.Graph(
                id='class-probabilities-chart',
                style={'height': '200px'}
            )
        ], style={
            'width': '500px',
            'height': '210px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '255px',
            'left': '380px',
            'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
              'borderRadius':'5px'
        }),
          # Map Chart
                html.Div([
            dcc.Graph(
                id='location-cluster-map',
                style={'height': '420px', 'width': '400px'}
            )
        ], style={
            'width': '420px',
            'height': '400px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '475px',
            'left': '20x',
            'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
              'borderRadius':'5px'
        }),
        
        # Metrics Bi Chart
                html.Div([
                     dcc.Graph(
                id='model-metrics-chart',
                style={'height': '400px', 'width': '400px'}
            )
            
        ], style={
            'width': '430px',
            'height': '400px',
            'backgroundColor': 'white',
            'position': 'absolute',
            'top': '475px',
            'left': '450px',
             'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
              'borderRadius':'5px'
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
    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)' ,
    'float':'left'
    })
    
], style={
    'width': '1200px',
    'height': '1080px',
    'backgroundColor': 'white',
    'margin': '0 auto'
})

@callback(
    [Output('feature-table-body', 'children'),
     Output('confidence-gauge', 'figure'),
     Output('severity-risk-gauge', 'figure'),
     Output('class-probabilities-chart', 'figure')],
    [Input('generate-prediction-btn', 'n_clicks')]
)
def update_prediction(n_clicks):
    if n_clicks is None:
        return no_update, no_update, no_update, no_update
    
    
    random_idx = random.randint(0, len(df) - 1)
    row = df.iloc[random_idx]
    
    input_data = {
        'Description': row['Description'],
        'Time Of Stop': row['Time Of Stop'],
        'Latitude': row['Latitude'],
        'Longitude': row['Longitude'],
        'Points': row['Points'],
        'Accident': row['Accident'],
        'Personal Injury': row['Personal Injury'],
        'Property Damage': row['Property Damage'],
        'Fatal': row['Fatal'],
        'Work Zone': row['Work Zone'],
        'Alcohol': row['Alcohol'],
        'HAZMAT': row['HAZMAT'],
        'Commercial License': row['Commercial License'],
        'Commercial Vehicle': row['Commercial Vehicle'],
        'VehicleType': row['VehicleType'],
        'Violation Type': row['Violation Type'],
        'Make': row['Make'],
        'Color': row['Color'],
        'Driver State': row['Driver State'],
        'DL State': row['DL State'],
        'Manufacture Year': row['Manufacture Year'],
        'SubAgency': row['SubAgency']
    }
    
    prediction, details = predict_fine_category(input_data)
    confidence = details['confidence'] * 100
    severity_risk = details['severity_risk'] * 100
    
   
    rows = []
    for feature, value in input_data.items():
        rows.append(html.Tr([
            html.Td(feature, style={'padding': '5px', 'backgroundColor': 'white', 'position': 'sticky', 'left': '0', 'fontFamily': 'Monospace', 'fontSize': '14px'}),
            html.Td(str(value), style={'padding': '5px', 'fontFamily': 'Monospace', 'fontSize': '14px'})
        ]))
    
    rows.extend([
        html.Tr([
            html.Td('Predicted Category', style={'padding': '5px', 'backgroundColor': '#e8f5e9', 'position': 'sticky', 'left': '0', 'fontWeight': 'bold', 'fontFamily': 'Monospace'}),
            html.Td(prediction, style={'padding': '5px', 'backgroundColor': '#e8f5e9', 'fontFamily': 'Monospace'})
        ]),
        html.Tr([
            html.Td('Actual Fine', style={'padding': '5px', 'backgroundColor': '#e8f5e9', 'position': 'sticky', 'left': '0', 'fontWeight': 'bold', 'fontFamily': 'Monospace'}),
            html.Td(f"${row['Total_Fine']:.2f}", style={'padding': '5px', 'backgroundColor': '#e8f5e9', 'fontFamily': 'Monospace'})
        ])
    ])
    
  
    gauge_figure = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=confidence,
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "#4CAF50"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 33], 'color': '#ffebee'},
                {'range': [33, 66], 'color': '#e8f5e9'},
                {'range': [66, 100], 'color': '#e3f2fd'}
            ],
        },
        number={
            'suffix': "%",
            'font': {'size': 28, 'family': 'Monospace', 'weight': 'bold'},
            'valueformat': ".1f"
        },
        domain={'y': [0.095, 1], 'x': [0.01, 1]}
    ))

    gauge_figure.update_layout(
        paper_bgcolor='white',
        margin=dict(l=20, r=30, t=20, b=0),
        height=140,
        annotations=[
            dict(
                text="Confidence",
                x=0.5,
                y=0.3,
                showarrow=False,
               
                yanchor='top'
            )
        ]
    )

    severity_figure = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=severity_risk,
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "#ff4444"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 33], 'color': '#e8f5e9'},
                {'range': [33, 66], 'color': '#fff3e0'},
                {'range': [66, 100], 'color': '#ffebee'}
            ],
        },
        number={
            'suffix': "%",
            'font': {'size': 28, 'family': 'Monospace', 'weight': 'bold'},
            'valueformat': ".1f"
        },
        domain={'y': [0.095, 1], 'x': [0.01, 1]}
    ))

    severity_figure.update_layout(
        paper_bgcolor='white',
        margin=dict(l=20, r=30, t=20, b=0),
        height=140,
        annotations=[
            dict(
                text="Severity Risk",
                x=0.5,
                y=0.3,
                showarrow=False,
                font=dict(size=18, family='Monospace'),
                yanchor='top'
            )
        ]
    )

   
    class_probs = details['class_probabilities']

    categories = []
    percentages = []
    for cat, prob in class_probs.items():
        categories.append(f"{float(cat):.1f}")
        percentages.append(prob * 100)  

    prob_figure = go.Figure(data=[
        go.Bar(
            x=categories,
            y=percentages,
            marker_color='#4CAF50',
          marker=dict(cornerradius=5)
        )
    ])

    prob_figure.update_layout(
        title={
            'text': 'Fine Category Confidence Levels',
            'y': 0.90,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
             'font': {'size': 14, 'family': 'Sans-Serif', 'weight':'bold', 'color':'black'}
        },
        margin=dict(l=20, r=20, t=40, b=0),
        yaxis_title="Confidence (%)",
        
        yaxis=dict(
             title_font=dict(size=10, weight='bold'),  
    tickfont=dict(size=8) 
         
        ),
        
        xaxis=dict(
            tickmode='array',
            ticktext=categories,
            tickvals=list(range(len(categories)))
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=200,
        showlegend=False,
        bargap=0.2
    )

   
    return rows, gauge_figure, severity_figure, prob_figure

CLUSTER_DATA = None

def load_cluster_data():
    global CLUSTER_DATA
    if CLUSTER_DATA is None:
        CLUSTER_DATA = pd.read_csv('Maryland_Traffic_Violation_Cluster.csv')
    return CLUSTER_DATA

def generate_base_figure():
    cluster_df = load_cluster_data()
    fig = go.Figure()
    
    
    cluster_colors = {
        0: {'color': '#FF4136', 'name': 'Cluster 0'},
        1: {'color': '#2ECC40', 'name': 'Cluster 1'},
        2: {'color': '#0074D9', 'name': 'Cluster 2'},
        3: {'color': '#FF851B', 'name': 'Cluster 3'},
        4: {'color': '#B10DC9', 'name': 'Cluster 4'},
    }
    
   
    for cluster in sorted(cluster_df['Location_Cluster'].unique()):
        cluster_points = cluster_df[cluster_df['Location_Cluster'] == cluster]
        
        fig.add_trace(go.Scattergeo(
            lon=cluster_points['Longitude'].values,
            lat=cluster_points['Latitude'].values,
            mode='markers',
            marker=dict(
                size=4,
                color=cluster_colors[cluster]['color'],
                opacity=0.6
            ),
            name=cluster_colors[cluster]['name'],
            hoverinfo='none',
            showlegend=True
        ))
    

    fig.add_trace(go.Scattergeo(
        lon=[],
        lat=[],
        mode='markers',
        marker=dict(
            size=8, 
            symbol='star',
            color='yellow',
            line=dict(
                width=2,
                color='black'
            ),
            opacity=1  
        ),
        name='Current Position',
        showlegend=True
    ))
    
    fig.update_layout(
        geo=dict(
            scope='usa',
            projection_scale=15,
            center=dict(lat=39.3, lon=-76.6),
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            showsubunits=True,
            subunitcolor='rgb(255, 255, 255)',
            showcoastlines=True,
            coastlinecolor='rgb(204, 204, 204)',
            fitbounds=False,
            visible=True,
            uirevision='base_map'
        ),
        margin=dict(l=10, r=10, t=0, b=20),
        height=380,
        width=380,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=0.2,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.8)',
            font=dict(size=8),
            itemsizing='constant'
        ),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig


BASE_FIGURE = generate_base_figure()

@callback(
    Output('location-cluster-map', 'figure'),
    [Input('generate-prediction-btn', 'n_clicks')]
)
def update_location_cluster_map(n_clicks):
    if n_clicks is None:
        return BASE_FIGURE
    
   
    fig = go.Figure(BASE_FIGURE)
    
   
    if n_clicks is not None:
        cluster_df = load_cluster_data() 
        random_idx = random.randint(0, len(cluster_df) - 1)
        row = cluster_df.iloc[random_idx]
        
        
        fig.data[-1].lon = [row['Longitude']]
        fig.data[-1].lat = [row['Latitude']]


    fig.update_layout(
        title={
            'text': 'Location Cluster Analysis',
            'y': 0.90,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 14, 'family': 'Sans-Serif', 'weight':'bold', 'color':'black'}
        }
    )
    
    return fig

@callback(
    Output('model-metrics-chart', 'figure'),
    Input('model-metrics-chart', 'id')
)
def update_model_metrics(_):
    """Update the model metrics chart with macro and weighted averages"""
    

    macro_metrics = model_dict['performance']['macro avg']
    weighted_metrics = model_dict['performance']['weighted avg']
    accuracy = model_dict['performance']['accuracy']
    
   
    metrics = ['Precision', 'Recall', 'F1-Score', 'Support']
    macro_values = [
        macro_metrics['precision'],
        macro_metrics['recall'],
        macro_metrics['f1-score'],
        macro_metrics['support']/100000  
    ]
    weighted_values = [
        weighted_metrics['precision'],
        weighted_metrics['recall'],
        weighted_metrics['f1-score'],
        weighted_metrics['support']/100000  
    ]

   
    metrics_figure = go.Figure()

   
    metrics_figure.add_trace(
        go.Bar(
            name='Macro Average',
            x=metrics,
            y=macro_values,
            marker_color='#4287F5',
            width=0.3,
            marker=dict(cornerradius=5)
        )
    )

  
    metrics_figure.add_trace(
        go.Bar(
            name='Weighted Average',
            x=metrics,
            y=weighted_values,
            marker_color='#ff4444',
            width=0.3,
            marker=dict(cornerradius=5)
        )
    )

    
    metrics_figure.add_trace(
        go.Bar(
            name='Accuracy',
            x=['Accuracy'],
            y=[accuracy],
            marker_color='#FFC107',
            width=0.3,
            marker=dict(cornerradius=5)
        )
    )

    # Update layout
    metrics_figure.update_layout(
        title={
            'text': 'Model Performance Metrics',
            'y': 0.90,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 14, 'family': 'Sans-Serif', 'weight':'bold', 'color':'black'}
        },
        margin=dict(l=20, r=20, t=100, b=20),
        yaxis=dict(
           title=dict(text='Score', font=dict(size=10, weight='bold')),
            range=[0, 1],
            tickformat='.0%',
        ),
        barmode='group',
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title=dict(font=dict(size=8, weight='bold')) 
        ),
        bargap=0.15,
        bargroupgap=0.1
    )
    
    return metrics_figure
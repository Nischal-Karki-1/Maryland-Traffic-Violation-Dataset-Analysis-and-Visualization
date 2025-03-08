# Montgomery County Traffic Violation Analysis & Visualization



## 📊 Overview

This project provides comprehensive analysis and visualization of Montgomery County's traffic violation dataset. Using advanced data mining techniques, machine learning, and interactive dashboards, the system uncovers patterns, trends, and insights that can inform policy and enforcement strategies for public safety and transportation management.

## 🚀 Features

- **Interactive Dashboards**: Five comprehensive dashboards with 40+ visualizations
  - Traffic Violation Overview
  - Demographics Analysis
  - Temporal Analysis
  - Vehicle Analysis
  - Fine Category Analysis & Prediction

- **Geospatial Analysis**: Heatmaps for violations, fines, and fatality hotspots

- **Predictive Modeling**: Machine learning model predicting fine categories with 99% accuracy

- **Advanced Visualizations**: Includes heatmaps, radar charts, gauge metrics, and various temporal and categorical charts

- **Demographic Insights**: Analysis of violation patterns across gender, race, and other demographic factors

## 💻 Tech Stack

- **Python 3.8**
- **Data Processing**: Pandas 1.5.3, NumPy 1.24.3
- **Machine Learning**: scikit-learn 1.2.2
- **Web Scraping**: BeautifulSoup4 4.12.2, requests 2.31.0
- **Geospatial Analysis**: geopy 2.3.0
- **Text Processing**: NLTK 3.8.1
- **Statistical Analysis**: SciPy 1.10.1
- **Visualization**: Dash 2.9.3, Plotly 5.13.1, Dash Bootstrap Components 1.4.1

## 📋 Data Sources

- Primary dataset from Montgomery County Public Data website
- Supplementary datasets created via web scraping:
  - Charge Hierarchy Description Dataset
  - Transportation Article Fine Dataset
  - SERO Codes Dataset

## 🔍 Analysis Highlights

- **Temporal Patterns**: Seasonal and time-of-day variations in traffic violations
- **Demographic Influences**: Court appearance rates and search patterns across demographic groups
- **Spatial Clustering**: Identification of high-risk violation zones
- **Predictive Insights**: Fine category prediction based on violation characteristics

## 🚗 Key Findings

- Winter showed highest traffic violations (27.01k)
- Most violations occurred in the morning on weekdays and at night on weekends
- Montgomery County center and border with Prince George's County had highest violation rates
- "Driver Failure to Obey Properly Placed Traffic Control Device Instructions" was the most common violation (39.4%)
- Black males had highest court appearance rate (11.4%) compared to 8% average
- Search conducted rates showed demographic disparities with 4.5% for Black individuals vs 3.2% overall average

## 🛠️ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/montgomery-traffic-violations.git
```

### 2. Navigate to Project Directory

```bash
cd montgomery-traffic-violations
```

### 3. Create and Activate Virtual Environment

For Linux/MacOS:
```bash
python -m venv venv
source venv/bin/activate
```

For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Dashboard Application

```bash
python app.py
```

### 6. Access the Dashboard

Open your browser and navigate to:
```
http://127.0.0.1:8050/
```

## 📊 Dashboard Preview

The application will be available at http://127.0.0.1:8050/

## 📷 Dashboard Showcase

<div align="center">
    <h3>🔍 Geographic Intelligence: Fine Distribution Heat Map</h3>
    <p><em>Interactive visualization of fine concentration across Montgomery County</em></p>
    <img width="600" alt="Traffic Violation Overview Dashboard with Heat Map of Fine Area" src="https://github.com/user-attachments/assets/cae7dea9-2db0-43f2-af43-fcfdbc7e48db">
</div>
<br>

<div align="center">
    <h3>🚦 Violation Hotspot Analysis: Geospatial Distribution</h3>
    <p><em>Critical insights into high-density violation areas for targeted enforcement</em></p>
    <img width="600" alt="Traffic Violation Overview Dashboard with Heat Map of Violation Area" src="https://github.com/user-attachments/assets/36bd3acf-b425-4fb9-a29c-9a8509a1ea3a">
</div>
<br>

<div align="center">
     <h3>📅 February 2024 Violation Snapshot: Filtered Overview Analysis</h3>
    <p><em>Targeted monthly dashboard showing comprehensive violation patterns during February 2024</em></p>
    <img width="600" alt="Traffic Violation Overview Dashboard with Filter of Year 2024 and Month February" src="https://github.com/user-attachments/assets/1a44e90b-12b5-4331-bf0b-29430c171bb5">
</div>
<br>

<div align="center">
    <h3>👥 Comprehensive Demographic Profile: Cross-Sectional Analysis</h3>
    <p><em>Multi-dimensional demographic insights across gender and racial categories</em></p>
    <img width="600" alt="Overall Demographics Analysis Dashboard for All Gender and Race" src="https://github.com/user-attachments/assets/44581c81-8fc0-41a4-9618-8c611d8a88dd">
</div>
<br>

<div align="center">
    <h3>⚖️ Population Segment Deep Dive: Black Male Violation Patterns</h3>
    <p><em>Focused demographic analysis revealing key enforcement disparities</em></p>
    <img width="600" alt="Demographics Analysis Dashboard for Black Male Information" src="https://github.com/user-attachments/assets/a6b5f62d-4a48-4d8f-9640-6abc077563b3">
</div>
<br>

<div align="center">
    <h3>⏰ Weekly Violation Rhythm: Comparative Weekday vs. Weekend Analysis</h3>
    <p><em>Temporal pattern recognition highlighting day-of-week enforcement variations</em></p>
    <img width="600" alt="Temporal Analysis Dashboard for Weekdays and Weekends" src="https://github.com/user-attachments/assets/64c1a5b8-7f7e-4f16-8a7d-46d47731585e">
</div>
<br>

<div align="center">
    <h3>💼 Workday Violation Intelligence: Monday-Friday Enforcement Patterns</h3>
    <p><em>Business day traffic enforcement insights for strategic planning</em></p>
    <img width="600" alt="Temporal Analysis Dashboard for Weekdays Only" src="https://github.com/user-attachments/assets/2268f716-a185-47d8-a6d2-c5e29d650f84">
</div>
<br>

<div align="center">
    <h3>🏖️ Weekend Traffic Behavior: Saturday-Sunday Violation Profile</h3>
    <p><em>Recreational day enforcement analysis revealing distinct weekend patterns</em></p>
    <img width="600" alt="Temporal Analysis Dashboard for Weekends Only" src="https://github.com/user-attachments/assets/7dadc559-3bd6-4668-b47a-e21de17bf9a2">
</div>
<br>

<div align="center">
    <h3>🚗 Vehicle Factor Investigation: Make, Model & Year Impact Analysis</h3>
    <p><em>Comprehensive vehicle characteristic correlations with violation types</em></p>
    <img width="600" alt="Vehicle Analysis Dashboard" src="https://github.com/user-attachments/assets/459347ce-fa28-473e-b2f6-071d9f3fa367">
</div>
<br>

<div align="center">
    <h3>💰 Predictive Fine Analytics: ML-Powered Category Forecasting</h3>
    <p><em>99% accurate machine learning model for violation fine prediction</em></p>
    <img width="600" alt="Fine Category Analysis and Prediction Dashboard" src="https://github.com/user-attachments/assets/9f007d4a-8786-4795-bf57-df4af6ae59b3">
</div>
<br>





## 📌 Requirements

- **Minimum Hardware**:
  - Memory: 8GB RAM
  - CPU: Intel Core i5 or equivalent
  - OS: Cross-platform (Windows/macOS/Linux)

## 🔮 Future Enhancements

- Optimization for full dataset (1.98M records)
- Cloud-based solutions for improved scalability
- Enhanced geospatial precision
- Dark theme for improved user experience
- Additional predictive models for accident probability

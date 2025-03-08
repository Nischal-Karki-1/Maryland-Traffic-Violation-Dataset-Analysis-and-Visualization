# Montgomery County Traffic Violation Analysis & Visualization

![Dashboard Preview](https://via.placeholder.com/800x400?text=Traffic+Violation+Dashboard)

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

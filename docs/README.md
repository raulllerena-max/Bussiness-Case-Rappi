# Rappi Competitive Intelligence System

A comprehensive Streamlit-based dashboard for analyzing competitive intelligence data in the food delivery market. This application provides strategic insights through geographic segmentation, metric prioritization, and trend analysis to help Rappi maintain competitive advantage.

## Features

### Core Dashboard
- **Executive Summary**: Focus on 3 core metrics (Estimated Delivery Time, Platform Service Fee, Final Price)
- **Competitive Positioning**: Real-time comparison with Uber Eats and DiDi Food
- **Target Recommendations**: Automated target setting based on competitor performance
- **Strategic Alerts**: Visual indicators for competitive gaps and opportunities

### Secondary Analysis
- **Trend Analysis**: 8-week historical data visualization
- **Metric Intelligence**: Dynamic analysis of various KPIs (CVR, Perfect Orders, etc.)
- **Strategic Segmentation**: Tertile-based recommendations (High/Medium/Low competitiveness)
- **Tactical Suggestions**: Specific actions based on metric type and performance gaps

### Geographic Intelligence
- **Zone Mapping**: Homologated geographic zones across competitors
- **Availability Classification**: Zones categorized by competitor presence
- **Prioritization Framework**: High/Medium/Low priority zones based on strategic value
- **Zone Type Classification**: Wealthy vs Non-Wealthy area segmentation

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone or download the project files
2. Install required dependencies:
   ```bash
   pip install streamlit pandas plotly numpy
   ```
3. Ensure data files are in the correct directories:
   - `base_de_datos/RAW_INPUT_METRICS.csv`
   - `competidores/COMPETITORS_INPUT_METRICS.csv`

## Usage

### Running the Application
```bash
streamlit run app.py
```

### Data Analysis Script
To generate the reliability matrix:
```bash
python analisis.py
```

### Dashboard Navigation
1. **Geographic Filters**: Select availability, zone type, and prioritization levels
2. **Zone Selection**: Choose specific geographic area for detailed analysis
3. **Core Metrics Tab**: View executive summary with key competitive indicators
4. **Secondary Analysis Tab**: Deep dive into specific metrics with trend analysis

## Project Structure

```
├── app.py                          # Main Streamlit application
├── analisis.py                     # Reliability matrix generation script
├── base_de_datos/                  # Rappi internal data
│   ├── RAW_INPUT_METRICS.csv
│   ├── RAW_ORDERS.csv
│   └── RAW_SUMMARY.csv
├── competidores/                   # Competitor data
│   ├── COMPETITORS_INPUT_METRICS.csv
│   ├── COMPETITORS_RAW_ORDERS.csv
│   └── SUMMARY.csv
├── docs/                           # Documentation
│   └── README.md
├── confiabilidad_todos_los_paises.csv  # Reliability analysis output
├── matriz_confiabilidad.csv        # Reliability matrix output
└── tempCodeRunnerFile.py          # Temporary file
```

## Data Requirements

### Input Data Format
- **COMPETITORS_INPUT_METRICS.csv**: Competitor metrics with columns for ZONE, METRIC, COMPETITOR, and time-series data (L0W, L1W, etc.)
- **RAW_INPUT_METRICS.csv**: Rappi internal metrics with similar structure

### Metric Homologation
The system automatically standardizes metrics across competitors:
- Delivery Time → "Tiempo Estimado de Entrega"
- Service Fee → "Service Fee de la Plataforma"
- Delivery Fee → "Precio Final (Delivery Fee)"
- Discounts/Promos → "Descuentos y Promociones"

## Key Concepts

### Availability Classification
- **All competitors with Rappi**: Zones where Rappi competes with both Uber Eats and DiDi Food
- **Rappi exclusive**: Zones served only by Rappi
- **All competitors but no Rappi**: Zones without Rappi presence

### Strategic Tertiles
- **Upper Tertile**: Leading or within 5% of competitor leader
- **Middle Tertile**: 5-15% gap from leader
- **Lower Tertile**: More than 15% gap from leader

### Target Setting
- **Fees/Prices**: Target = Best competitor value × 0.90 (-10%)
- **Delivery Time**: Target = Best competitor value (match exactly)

## Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualizations
- **numpy**: Numerical computations

## Output Files

- **matriz_confiabilidad.csv**: Reliability matrix showing trend consistency across competitors
- **confiabilidad_todos_los_paises.csv**: Country-wide reliability analysis

## Strategic Insights

The dashboard provides actionable intelligence for:
- **Pricing Strategy**: Dynamic fee adjustments based on competitor positioning
- **Operational Improvements**: Targeted actions for delivery time optimization
- **Market Expansion**: Identification of high-priority zones for growth
- **Competitive Monitoring**: Real-time alerts for competitive threats

## Notes

- Geographic zones are homologated to ensure consistent comparison
- Metrics are standardized across different data sources
- Trend analysis uses 1% tolerance for stability classification
- Reliability assessment considers consistency across all three major players
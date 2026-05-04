# 🌦️ Weather & Climate Data Analytics Dashboard

A complete **Big Data + Data Visualization project** that analyzes historical weather data using a Python ETL pipeline and presents insights through an interactive **Power BI dashboard**.

---

## 📌 Project Overview

This project builds an end-to-end data analytics pipeline:

- 🌐 Data Source: Open-Meteo Historical Weather API  
- ⚙️ ETL Pipeline: Python (Pandas, NumPy)  
- 📊 Visualization: Microsoft Power BI  
- 🗂️ Data Model: Star Schema  

The dashboard provides insights into:
- Global climate trends 🌍  
- Seasonal & hourly temperature patterns ⏳  
- City-wise weather comparisons 🏙️  
- Extreme weather events ⚡  

---

## 🚀 Key Features

- 🔄 Automated ETL pipeline for large-scale weather data  
- 📈 Interactive Power BI dashboard (3 pages)  
- 🌡️ Heatmaps, maps, KPI cards, and trend charts  
- 🎯 Derived metrics:
  - Heat Index
  - Wind Chill
  - Comfort Index
  - Extreme Event Detection  

---

## 📊 Dashboard Preview

### 🌍 Page 1 — Global Climate Overview
![Global Dashboard](screenshots/page1.png)

### 🔍 Page 2 — Weather Deep Dive
![Deep Dive](screenshots/page2.png)

### 🏙️ Page 3 — City Insights
![City Insights](screenshots/page3.png)

---

## 📂 Project Structure

weather-climate-data-analytics/
│
├── data/
│   └── processed/
│       ├── fact_weather.csv
│       ├── dim_city.csv
│       ├── dim_date.csv
│       ├── dim_weather_code.csv
│       ├── agg_daily.csv
│       ├── agg_monthly.csv
│       └── agg_extremes.csv
│
├── dashboards/
│   └── weather_climate_dashboard.pbix
│
├── reports/
│   ├── project_report.pdf
│   └── project_presentation.pptx
│
├── scripts/
│   └── etl_pipeline.py
│
├── screenshots/
│   ├── global_overview.png
│   ├── deep_dive.png
│   └── city_insights.png
│
├── README.md
├── requirements.txt
└── .gitignore

---

## ⚙️ Tools & Technologies

- Python (Pandas, NumPy)
- Open-Meteo API
- Power BI
- CSV Data Storage
- VS Code

---

## 📈 Key Insights

- 🌡️ Average global temperature: **14.44°C** :contentReference[oaicite:0]{index=0}  
- 📊 Total precipitation: **96.23K mm** :contentReference[oaicite:1]{index=1}  
- ⚡ Extreme events: **11K occurrences** :contentReference[oaicite:2]{index=2}  
- 📉 Clear seasonal and hourly temperature patterns observed  
- 🌍 Different climate zones show distinct behavior  

---

## 🧠 Learning Outcomes

- End-to-end Data Pipeline Development  
- Feature Engineering & Data Cleaning  
- Data Modeling (Star Schema)  
- Business Intelligence & Dashboard Design  

---

## 🔮 Future Improvements

- ☁️ Cloud deployment (Azure / AWS)  
- 📡 Real-time weather integration  
- 🤖 Machine learning for prediction  
- 🗄️ Database integration (PostgreSQL / Data Warehouse)  

---

## 📄 Project Report

📎 Full report available here:  
[Download Report](./report.pdf)

---

## 👨‍💻 Author

**Rahul Bisht**  
MSc Data & Business Analytics  
Jaypee Institute of Information Technology, Noida  

---

# ⚡ Global Energy Data Analytics Project

## 📌 Project Overview

This project presents a **complete data engineering and analytics solution** for integrating and analysing global energy-related datasets. It focuses on building a **scalable ETL pipeline** that collects, processes, and stores multi-source data to support data-driven insights.

The project is part of the MSc Data Analytics programme and demonstrates practical implementation of **data-intensive and scalable systems**.

The final output is a **clean, unified dataset** enabling analysis of relationships between:

* Electricity consumption
* Electricity production
* Renewable energy usage
* Transmission losses
* Electricity access
* Population
* GDP per capita

---

## 🎯 Objectives

* Design and implement an **automated data pipeline**
* Integrate **heterogeneous datasets** (JSON, XML, CSV, ZIP)
* Perform **data cleaning and standardisation**
* Apply **feature engineering for analytical insights**
* Store processed data in **cloud storage (AWS S3)** and **NoSQL database (MongoDB)**
* Enable downstream tasks such as **analysis, visualization, and machine learning**

---

## 🏗️ System Architecture

The system follows a structured **ETL (Extract → Transform → Load)** pipeline:

### 1. Extract

Data is collected from:

* World Bank APIs (JSON & XML)
* Our World in Data (CSV)
* World Bank ZIP datasets (renewable energy)

### 2. Transform

* Data cleaning and type conversion
* Handling missing values
* ISO country code standardisation (ISO2 → ISO3)
* Data reshaping (wide → long format)
* Dataset validation

### 3. Load

* Final dataset stored as:

  * Local CSV file
  * AWS S3 cloud storage
  * MongoDB Atlas collection

---

## 🔄 Pipeline Workflow

The pipeline is divided into structured tasks:

| Task    | Description                                        |
| ------- | -------------------------------------------------- |
| Task 1  | Electricity consumption data extraction            |
| Task 2  | Electricity access data extraction                 |
| Task 3  | Transmission losses (XML parsing + ISO conversion) |
| Task 4  | Renewable energy transformation (ZIP + melt)       |
| Task 5  | Electricity production aggregation                 |
| Task 6  | Population data extraction                         |
| Task 7  | GDP per capita extraction                          |
| Task 8  | Data cleaning and standardisation                  |
| Task 9  | Dataset integration (multi-source joins)           |
| Task 10 | Feature engineering and data export                |
| Task 11 | Data storage in MongoDB                            |

---

## 🧮 Feature Engineering

A key derived metric is:

[
\text{production_per_capita} = \frac{\text{production} \times 10^9}{\text{population}}
]

This enables fair comparison of energy production across countries.

---

## 🗂️ Final Dataset Schema

| Column                | Description                  |
| --------------------- | ---------------------------- |
| iso3                  | Country ISO3 code            |
| country_name          | Country name                 |
| year                  | Year                         |
| electricity           | Electricity consumption      |
| production            | Total electricity production |
| production_per_capita | Derived metric               |
| renewable             | Renewable energy percentage  |
| losses                | Transmission losses (%)      |
| access                | Electricity access (%)       |
| population            | Total population             |
| gdp_per_capita        | GDP per capita               |

---

## ☁️ Technologies Used

* **Python** – Core programming language
* **Pandas** – Data processing and transformation
* **Requests** – API integration
* **Boto3** – AWS S3 interaction
* **MongoDB Atlas** – NoSQL data storage
* **PyCountry** – ISO country code standardisation
* **XML / JSON / CSV parsing** – Multi-format data handling

---

## 🔐 Configuration

### AWS S3

```bash
AWS_ACCESS_KEY_ID=YOUR_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET
```

### MongoDB

```bash
mongodb+srv://<username>:<password>@cluster.mongodb.net/
```

---

## ▶️ How to Run

1. Install dependencies:

```bash
pip install pandas requests boto3 pymongo pycountry
```

2. Execute the pipeline:

```bash
python data_pipeline.py
```

---

## 📦 Output

* **Local File:**
  `final_dataset.csv`

* **AWS S3:**
  `s3://energy-data-backup/final/final_dataset.csv`

* **MongoDB Collection:**
  `electricity_db.final_energy_data`

---

## ⚠️ Important Notes

* The pipeline uses **inner joins** for core datasets to maintain data consistency
* Some records may be excluded due to missing values across sources
* Renewable dataset requires **ZIP extraction during execution**
* Transmission losses dataset requires **ISO2 to ISO3 conversion (critical step)**

---

## 📚 Academic Context

This project is developed as part of:

**MSc Data Analytics**
Module: *Data Intensive Scalable Systems*

It demonstrates:

* End-to-end data pipeline development
* Integration of large, heterogeneous datasets
* Cloud-based data engineering practices
* Real-world scalability concepts

---

## 👤 Author

**Tauqeer Hassan**
MSc Data Analytics

---

## ✅ Project Status

✔ Fully functional pipeline
✔ Automated data ingestion and processing
✔ Cloud and database integration
✔ Ready for analysis and modelling

---

# ⚡ Global Energy Data Analytics Pipeline

This project implements an end-to-end data engineering pipeline to integrate and analyse global energy datasets from multiple heterogeneous sources. It demonstrates the practical application of scalable data processing, transformation, and cloud-based storage to support data-driven insights in the energy domain.

## Project Submission – Execution Guide

---

## 🔗 Project Links

* **GitHub Repository:**
  [https://github.com/tauqeerqau/dissEnergyProject](https://github.com/tauqeerqau/dissEnergyProject)

* **Live Dashboard (Streamlit):**
  [https://dissenergyprojectanalysis.streamlit.app/](https://dissenergyprojectanalysis.streamlit.app/)

---

## ⚙️ Project Execution

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Run Core Notebook (Google Colab)

Open and run the main notebook in Google Colab:

```bash
DissProject.ipynb
```

This notebook contains the core implementation using PySpark and Hadoop for large-scale data processing and transformation.

---

### 3. Run Automated Pipeline (Local)

```bash
python data_pipeline.py
```

This executes the automated ETL pipeline for data ingestion, processing, integration, and storage.

---

### 3. Output Verification

After execution, the following outputs should be available:

* **Local Output**

  ```
  final_dataset.csv
  ```

* **AWS S3**

  ```
  energy-data-backup/final/final_dataset.csv
  ```

* **MongoDB Collection**

  ```
  electricity_db.final_energy_data
  ```

---

### 4. Data Analysis (Optional)

Run locally:

```bash
streamlit run app.py
```

Or access deployed dashboard:

[https://dissenergyprojectanalysis.streamlit.app/](https://dissenergyprojectanalysis.streamlit.app/)

---

### 5. Alternative Execution Environment

The pipeline can also be executed in **Google Colab** if required.

---

## 👤 Student

**Tauqeer Hassan**
MSc Data Analytics

---

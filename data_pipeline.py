# ==========================================
# ENERGY DATA PIPELINE (FINAL TRUE WORKING VERSION)
# ==========================================

import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET
import boto3
import pycountry
from pymongo import MongoClient
import logging
import zipfile
import io
from io import StringIO

logging.basicConfig(level=logging.INFO)

# ==========================================
# AWS CONFIG (UNCHANGED)
# ==========================================
os.environ["AWS_ACCESS_KEY_ID"] = "YOUR_KEY"
os.environ["AWS_SECRET_ACCESS_KEY"] = "YOUR_SECRET"

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="eu-north-1"
)

bucket = "energy-data-backup"

def upload(local, remote):
    try:
        s3.upload_file(local, bucket, remote)
        print("Uploaded:", remote)
    except Exception as e:
        print("Upload failed:", e)

# ==========================================
# ISO FUNCTION
# ==========================================
def iso(x):
    try:
        return pycountry.countries.lookup(x).alpha_3
    except:
        return None

# ==========================================
# ELECTRICITY
# ==========================================
print("\nLoading Electricity...")
url = "https://api.worldbank.org/v2/country/all/indicator/EG.USE.ELEC.KH.PC?format=json&per_page=20000"
df_elec = pd.DataFrame(requests.get(url).json()[1])
df_elec["country"] = df_elec["country"].apply(lambda x: x["value"])
df_elec = df_elec[["country","date","value"]]
df_elec.columns = ["country","year","electricity"]
df_elec["iso3"] = df_elec["country"].apply(iso)

country_map = df_elec[["iso3","country"]].drop_duplicates()
country_map.columns = ["iso3","country_name"]

# ==========================================
# ACCESS
# ==========================================
print("\nLoading Access...")
url = "https://api.worldbank.org/v2/country/all/indicator/EG.ELC.ACCS.ZS?format=json&per_page=20000"
df_access = pd.DataFrame(requests.get(url).json()[1])
df_access["country"] = df_access["country"].apply(lambda x: x["value"])
df_access = df_access[["country","date","value"]]
df_access.columns = ["country","year","access"]
df_access["iso3"] = df_access["country"].apply(iso)

# ==========================================
# LOSSES (🔥 FINAL FIX: ISO2 → ISO3)
# ==========================================
print("\nLoading Losses...")
url = "https://api.worldbank.org/v2/country/all/indicator/EG.ELC.LOSS.ZS?per_page=20000"
content = requests.get(url).content

with open("losses.xml","wb") as f:
    f.write(content)

tree = ET.parse("losses.xml")
root = tree.getroot()

records = []
ns = {"wb":"http://www.worldbank.org"}

for item in root.findall("wb:data", ns):
    c = item.find("wb:country", ns)
    d = item.find("wb:date", ns)
    v = item.find("wb:value", ns)

    if c is None or d is None:
        continue

    iso2 = c.attrib.get("id")  # ISO2

    # 🔥 CONVERT ISO2 → ISO3
    try:
        country_obj = pycountry.countries.get(alpha_2=iso2)
        iso_code = country_obj.alpha_3 if country_obj else None
    except:
        iso_code = None

    year_val = d.text

    if year_val and year_val.isdigit():
        records.append([
            iso_code,
            int(year_val),
            float(v.text) if v is not None and v.text else None
        ])

df_loss = pd.DataFrame(records, columns=["iso3","year","losses"])

print("Loss shape:", df_loss.shape)

# GROUP
df_loss = df_loss.groupby(["iso3","year"], as_index=False)["losses"].mean()

print("Loss after grouping:", df_loss.shape)

# ==========================================
# RENEWABLE
# ==========================================
print("\nLoading Renewable...")
url = "https://api.worldbank.org/v2/en/indicator/EG.ELC.RNEW.ZS?downloadformat=csv"
response = requests.get(url)
z = zipfile.ZipFile(io.BytesIO(response.content))
z.extractall("renewable_data")

csv_file = [f for f in os.listdir("renewable_data") if f.endswith(".csv") and "Metadata" not in f][0]
csv_path = os.path.join("renewable_data", csv_file)

df_raw = pd.read_csv(csv_path, skiprows=4)
year_cols = [c for c in df_raw.columns if c.isdigit()]

df_renew = df_raw.melt(
    id_vars=["Country Name","Country Code"],
    value_vars=year_cols,
    var_name="year",
    value_name="renewable"
)

df_renew = df_renew.rename(columns={
    "Country Name":"country",
    "Country Code":"iso3"
})

df_renew = df_renew[df_renew["iso3"].str.len() == 3]

# ==========================================
# PRODUCTION
# ==========================================
print("\nLoading Production...")
url = "https://ourworldindata.org/grapher/electricity-generation.csv"
response = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
df_prod = pd.read_csv(StringIO(response.text))

base = ["Entity","Code","Year"]
energy_cols = [c for c in df_prod.columns if c not in base]

df_prod[energy_cols] = df_prod[energy_cols].apply(pd.to_numeric, errors="coerce")
df_prod["production"] = df_prod[energy_cols].sum(axis=1)

df_prod = df_prod[["Entity","Code","Year","production"]]
df_prod.columns = ["country","iso3","year","production"]

# ==========================================
# POPULATION
# ==========================================
print("\nLoading Population...")
url = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000"
df_pop = pd.DataFrame(requests.get(url).json()[1])
df_pop["country"] = df_pop["country"].apply(lambda x: x["value"])
df_pop = df_pop[["country","date","value"]]
df_pop.columns = ["country","year","population"]
df_pop["iso3"] = df_pop["country"].apply(iso)

# ==========================================
# GDP (NEW ADDITION)
# ==========================================
print("\nLoading GDP...")

gdp_url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.CD?format=json&per_page=20000"

df_gdp = pd.DataFrame(requests.get(gdp_url).json()[1])

# Use ISO directly (IMPORTANT)
df_gdp["iso3"] = df_gdp["countryiso3code"]

# Keep required columns
df_gdp = df_gdp[["iso3", "date", "value"]]
df_gdp.columns = ["iso3", "year", "gdp_per_capita"]

# Remove aggregates (AFE, WLD etc.)
df_gdp = df_gdp[df_gdp["iso3"].str.len() == 3]

# Clean year
df_gdp["year"] = pd.to_numeric(df_gdp["year"], errors="coerce")
df_gdp = df_gdp.dropna(subset=["year", "gdp_per_capita"])
df_gdp["year"] = df_gdp["year"].astype(int)

print("GDP shape:", df_gdp.shape)

# ==========================================
# CLEAN
# ==========================================
def clean(df):
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    return df

df_elec = clean(df_elec)
df_access = clean(df_access)
df_pop = clean(df_pop)
df_prod = clean(df_prod)
df_renew = clean(df_renew)
df_gdp = clean(df_gdp)

df_elec = df_elec.dropna(subset=["iso3","electricity"])
df_access = df_access.dropna(subset=["iso3","access"])
df_pop = df_pop.dropna(subset=["iso3","population"])
df_prod = df_prod.dropna(subset=["iso3","production"])
df_renew = df_renew.dropna(subset=["iso3","renewable"])

# KEEP COLS
df_elec = df_elec[["iso3","year","electricity"]]
df_access = df_access[["iso3","year","access"]]
df_loss = df_loss[["iso3","year","losses"]]
df_pop = df_pop[["iso3","year","population"]]
df_prod = df_prod[["iso3","year","production"]]
df_renew = df_renew[["iso3","year","renewable"]]
df_gdp = df_gdp[["iso3","year","gdp_per_capita"]]

# ==========================================
# JOIN
# ==========================================
print("\nJoining CORE datasets...")

df = df_elec.merge(df_renew, on=["iso3","year"], how="inner") \
           .merge(df_access, on=["iso3","year"], how="inner") \
           .merge(df_prod, on=["iso3","year"], how="inner") \
           .merge(df_pop, on=["iso3","year"], how="inner") \
           .merge(df_gdp, on=["iso3","year"], how="left")

print("After core join:", df.shape)

df = df.merge(df_loss, on=["iso3","year"], how="left")

print("After adding losses:", df.shape)

df = df.merge(country_map, on="iso3", how="left")

# ==========================================
# FEATURE
# ==========================================
df["production_per_capita"] = (df["production"] * 1e9) / df["population"]

# ==========================================
# FINAL CHECK
# ==========================================
print("\nFINAL CHECK:")
print("Shape:", df.shape)
print("Countries:", df["iso3"].nunique())
print("Years:", df["year"].nunique())
print(df.isna().sum())

# ==========================================
# SAVE
# ==========================================
df.to_csv("final_dataset.csv", index=False)
upload("final_dataset.csv", "final/final_dataset.csv")

# ==========================================
# MONGO
# ==========================================
records = df.to_dict("records")

client = MongoClient("mongodb+srv://taqDissAdmin:T%40uq33r7861@electricitydb.puam6sy.mongodb.net/?appName=electricitydb")
db = client["electricity_db"]
collection = db["final_energy_data"]
collection.delete_many({})

if records:
    collection.insert_many(records)
    print("MongoDB Inserted")

print("\nPIPELINE COMPLETE")
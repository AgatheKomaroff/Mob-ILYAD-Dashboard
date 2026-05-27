import re
import pandas as pd
import io
import requests
import numpy as np
from pathlib import Path

API_POSTAL_CODES_URL = "https://tabular-api.data.gouv.fr/api/resources/dbe8a621-a9c4-4bc3-9cae-be1699c5ff25/data/csv/"
DATA_PATH = "data/01_input"

# Data loading functions

def load_french_postal_lookup() -> pd.DataFrame:
    """Load the French postal code lookup table from the API."""
    response = requests.get(API_POSTAL_CODES_URL)
    return pd.read_csv(
        io.StringIO(response.text.encode("latin").decode("utf-8")), sep=",",
        dtype={"code_postal": str, "code_commune_INSEE": str, "code_departement": str}
    )

def load_patient_location_data(file_path: str) -> pd.DataFrame:
    """Load the patient location data from the Excel file."""
    data_path = Path(DATA_PATH) / file_path
    if not data_path.exists():
        print(f"Warning: {data_path} not found. Loading sample data instead.")
        data_path = Path(DATA_PATH) / "carte_patients__sample.xlsx"
    return pd.read_excel(data_path)

def load_patient_redcap_data(path: str) -> pd.DataFrame:
    """Load the patient REDCap data from the CSV file."""
    data_path = Path(DATA_PATH) / path
    if not data_path.exists():
        print(f"Warning: {data_path} not found in {DATA_PATH}. Loading sample data instead.")
        data_path = Path(DATA_PATH) / "mobyliad_export__sample.csv"
    return pd.read_csv(data_path, encoding="latin", sep=";")

# Data assertion functions

def assert_required_columns(df: pd.DataFrame, required_columns: list[str]):
    """Assert that the required columns are present in the DataFrame."""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

# Data cleaning functions

def parse_french_postal_code(postal_code: str) -> str:
    found_postal_code = re.findall(r"(?:0*)?(\d{4,5})", postal_code)
    if not found_postal_code:
        return ""
    return found_postal_code[0]

def clean_patient_location_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the patient location data by parsing postal codes."""
    df["#étude"] = df["#étude"].astype(str)
    df["country"] = np.select(
        [
            df["Code Postal"].astype(str).str.contains("Suisse|CH", case=False)
        ],
        [
            "Swiss"
        ],
        default="France"
    )
    df["postal_code"] = (
        df["Code Postal"]
        .astype(str)
        .str.zfill(5)
        .apply(parse_french_postal_code)
        .astype(str)
        .str.zfill(5)
    )
    non_french_postal_codes = df.loc[df["country"] == "France", "postal_code"].str.len() != 5
    if non_french_postal_codes.any():
        print(f"Warning: Found {non_french_postal_codes.sum()} non-French postal codes. They will not be used.")
        df.loc[non_french_postal_codes, "postal_code"] = ""
    return df

def clean_french_postal_lookup(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the French postal code lookup table by ensuring postal codes are strings."""
    df["commune"] = df["nom_commune_complet"]
    df["code_postal"] = df["code_postal"].astype(str).str.zfill(5)
    df["department"] = df["nom_region"]
    return df

def clean_patient_redcap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the patient REDCap data by ensuring the '#étude' column is a string."""
    new_df = df[[
        "ID",
        "Conclusion du scanner (choice=Scanner négatif)",
        "Conclusion du scanner (choice=Scanner intermédiaire)",
        "Conclusion du scanner (choice=Scanner positif)",
        "Conclusion du scanner (choice=Découverte incidente)",
        "Nodule(s) détecté(s)",
        "Quel est votre âge ?",
        "Antécédents personnels de cancer",
        "Score EPICES",
        "Est-ce que le patient est sevré ? (Attention il faut que ça fasse + de 3 mois après la dernière cigarette sinon cocher 'toujours fumeur')"
    ]].copy()
    new_df["#étude"] = new_df["ID"].astype(str)
    new_df["scanner_conclusion"] = np.select(
        [
            new_df["Conclusion du scanner (choice=Scanner négatif)"] == "Checked",
            new_df["Conclusion du scanner (choice=Scanner intermédiaire)"] == "Checked",
            new_df["Conclusion du scanner (choice=Scanner positif)"] == "Checked",
        ],
        ["Négatif", "Intermédiaire", "Positif"],
        default="Négatif"
    )
    new_df["scanner_incidente"] = (new_df["Conclusion du scanner (choice=Découverte incidente)"] == "Checked")
    new_df["detected_nodules"] = new_df["Nodule(s) détecté(s)"]
    new_df["age"] = new_df["Quel est votre âge ?"]
    new_df["antecedent"] = new_df["Antécédents personnels de cancer"]
    new_df["EPICES"] = new_df["Score EPICES"].round(2)
    new_df["sevrage"] = new_df["Est-ce que le patient est sevré ? (Attention il faut que ça fasse + de 3 mois après la dernière cigarette sinon cocher 'toujours fumeur')"]
    return new_df

# Data merging function

def merge_patient_data_with_postal_lookup(patient_df: pd.DataFrame, postal_lookup_df: pd.DataFrame) -> pd.DataFrame:
    """Merge the patient location data with the French postal code lookup table."""
    merged_df = patient_df.merge(
        postal_lookup_df[["code_postal", "latitude", "longitude", "commune", "department"]].drop_duplicates(subset=["code_postal"]),
        left_on="postal_code",
        right_on="code_postal",
        how="left"
    )
    print(f"Merged patient data with postal lookup: {merged_df.shape[0]} records, {merged_df.shape[1]} columns.")
    print(f"Missing coordinates for {merged_df['latitude'].isna().sum()} records.")
    print(f"Missing coordinates patients: {merged_df[merged_df['latitude'].isna()]['#étude'].tolist()}")
    return merged_df

def merge_patient_data_with_redcap(patient_df: pd.DataFrame, redcap_df: pd.DataFrame) -> pd.DataFrame:
    """Merge the patient location data with the REDCap data."""
    merged_df = patient_df.merge(
        redcap_df[["#étude", "scanner_conclusion", "scanner_incidente", "detected_nodules", "age", "antecedent", "EPICES", "sevrage"]],
        on="#étude",
        how="left"
    )
    print(f"Merged patient data with REDCap data: {merged_df.shape[0]} records, {merged_df.shape[1]} columns.")
    merged_df["entity_count"] = 1
    merged_df["gender"] = merged_df["Genre"].str.strip().str.upper().map({"F": "Femme", "M": "Homme"})
    return merged_df

def collect_and_clean_data(patient_location_file: str, redcap_data_file: str) -> pd.DataFrame:
    print("Loading data...")
    postal_lookup_df = load_french_postal_lookup()
    patient_location_df = load_patient_location_data(patient_location_file)
    patient_redcap_df = load_patient_redcap_data(redcap_data_file)

    print("Cleaning data...")
    postal_lookup_df = clean_french_postal_lookup(postal_lookup_df)
    patient_location_df = clean_patient_location_data(patient_location_df)
    patient_redcap_df = clean_patient_redcap_data(patient_redcap_df)

    print("Merging data...")
    merged_location_df = merge_patient_data_with_postal_lookup(patient_location_df, postal_lookup_df)
    final_merged_df = merge_patient_data_with_redcap(merged_location_df, patient_redcap_df)

    print("Data collection and cleaning complete.")
    return final_merged_df

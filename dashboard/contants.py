
PATIENT_LOCATION_FILE = "carte_patients.xlsx"
REDCAP_DATA_FILE = "MobILYAD-MobilyadExport_DATA_LABELS_2026-04-28.csv"

name_features = {
    "gender": "Genre",
    "age": "Âge",
    "postal_code": "Code Postal",
    "commune": "Commune",
    "department": "Département",
    "scanner_conclusion": "Conclusion Scanner",
    "scanner_incidente": "Découverte incidente",
    "detected_nodules": "Détection nodules",
    "antecedent": "Antécédent",
    "EPICES": "Score EPICES",
    "sevrage": "Sevrage",    
}
type_features = {
    "gender": "text",
    "age": "number",
    "postal_code": "text",
    "commune": "text",
    "department": "text",
    "scanner_conclusion": "text",
    "scanner_incidente": "text",
    "detected_nodules": "text",
    "antecedent": "text",
    "EPICES": "number",
    "sevrage": "text",
}
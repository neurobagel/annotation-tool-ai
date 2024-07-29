from pathlib import Path
import json
import pandas as pd
from typing import List, Dict, Any

terms: Path = Path(__file__).parent / "CONCEPT.csv"
table: pd.DataFrame = pd.read_csv(
    terms, sep="\t", low_memory=False, keep_default_na=False, dtype=str
)

domain_id_entries: List[str] = table["domain_id"].unique()

conditions: pd.DataFrame = table.query(
    "domain_id == 'Measurement' and standard_concept == 'S' and concept_class_id == 'Staging / Scales'"  # noqa: E501
)

my_json: List[Dict[str, Any]] = [
    {
        "label": condition.concept_name,
        "identifier": "snomed:" + condition.concept_code,
    }
    for condition in conditions.itertuples()
]

with open("measurementTerms.json", "w") as f:
    json.dump(my_json, f, indent=2)

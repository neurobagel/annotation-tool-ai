from typing import Dict, List
from rdflib import Graph
import os


def extract_subclasses(
    ontology_path: str, specific_entities: List[str]
) -> None:

    # Load the ontology
    g: Graph = Graph()
    g.parse(ontology_path)

    # Build the SPARQL query
    entity_filters: str = " || ".join(
        [f"?superClass = <{entity}>" for entity in specific_entities]
    )
    query: str = f"""
    SELECT ?subClass ?subClassLabel ?superClass ?superClassLabel
    WHERE {{
        ?subClass rdfs:subClassOf ?superClass .
        OPTIONAL {{ ?subClass rdfs:label ?subClassLabel . }}
        OPTIONAL {{ ?superClass rdfs:label ?superClassLabel . }}
        FILTER ({entity_filters})
    }}
    """

    results = g.query(query)

    # Create a dictionary to store subclasses per superclass
    subclasses_dict: Dict[str, List[str]] = {}

    # Process the results
    for row in results:
        subClass, subClassLabel, superClass, superClassLabel = row
        subClassLabel = subClassLabel if subClassLabel else subClass
        superClassLabel = superClassLabel if superClassLabel else superClass
        superclass_name: str = str(superClassLabel).replace(" ", "_")

        if superclass_name not in subclasses_dict:
            subclasses_dict[superclass_name] = []

        subclasses_dict[superclass_name].append(
            f"{subClassLabel} ({subClass})"
        )

    # Write subclasses to separate files
    output_dir: str = "app/level_identification/src"
    os.makedirs(output_dir, exist_ok=True)

    for superClass, subclasses in subclasses_dict.items():
        filename: str = os.path.join(output_dir, f"{superClass}.txt")
        with open(filename, "w") as file:
            for subclass in subclasses:
                file.write(subclass + "\n")


ontology_path = "app/level_identification/src/doid.owl"
specific_entities = [
    "http://purl.obolibrary.org/obo/DOID_150",
    "http://purl.obolibrary.org/obo/DOID_863",
]

extract_subclasses(ontology_path, specific_entities)

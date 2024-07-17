import json
from typing import Any, Dict
from app.factories.annotation_factories.factory_interface import (
    AnnotationFactory,
)
from app.products.annotations import Annotations
from app.products.is_about_sex import IsAboutSex
from app.products.tsv_annotations import TSVAnnotations


class SexFactory(AnnotationFactory):
    def __init__(self, mapping_file: str = "/app/data/diagnosisTerms.json"):
        self.levels_mapping = self.load_levels_mapping(mapping_file)

    def create_annotation(
        self, parsed_output: Dict[str, Any]
    ) -> TSVAnnotations:
        termurl = parsed_output["TermURL"]
        description = "Sex variable"
        annotation_instance = IsAboutSex(Label="Sex", TermURL=termurl)

        levels = {
            key: self.levels_mapping.get(value.strip().lower(), {})
            for key, value in parsed_output.get("Levels", {}).items()
        }

        annotations = Annotations(IsAbout=annotation_instance, Levels=levels)
        return TSVAnnotations(
            Description=description,
            Levels={k: v["Label"] for k, v in levels.items() if "Label" in v},
            Annotations=annotations,
        )

    @staticmethod
    def load_levels_mapping(mapping_file: str) -> Dict[str, Dict[str, str]]:
        with open(mapping_file, "r") as file:
            mappings = json.load(file)
        return {
            entry["label"]
            .strip()
            .lower(): {"TermURL": entry["identifier"], "Label": entry["label"]}
            for entry in mappings
        }

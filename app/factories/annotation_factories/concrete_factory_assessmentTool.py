import json
from typing import Dict, Mapping
from app.factories.annotation_factories.factory_interface import (
    AnnotationFactory,
)
from app.products.annotations import Annotations
from app.products.is_about_assessmentTool import IsAboutAssessmentTool
from app.products.tsv_annotations import TSVAnnotations


class AssessmentToolFactory(AnnotationFactory):
    def __init__(self, mapping_file: str = "app/data/toolTerms.json"):
        self.assessmenttool_mapping = self.load_assessmenttool_mapping(
            mapping_file
        )

    def create_annotation(
        self, parsed_output: Dict[str, str]
    ) -> TSVAnnotations:
        annotation_instance = IsAboutAssessmentTool(
            TermURL=parsed_output["TermURL"]
        )
        description = "Description of Assessment Tool conducted"
        ispartof_key = parsed_output.get("AssessmentTool", "").strip().lower()
        ispartof = next(
            (
                item
                for item in self.assessmenttool_mapping.values()
                if item["Label"].strip().lower() == ispartof_key
            ),
            None,
        )
        annotations = Annotations(
            IsAbout=annotation_instance, IsPartOf=ispartof
        )
        return TSVAnnotations(Description=description, Annotations=annotations)

    @staticmethod
    def load_assessmenttool_mapping(
        mapping_file: str,
    ) -> Mapping[str, Dict[str, str]]:
        with open(mapping_file, "r") as file:
            mappings = json.load(file)
        return {
            term_url.strip().lower(): {
                "TermURL": f"cogatlas:{term_url.strip().lower()}",
                "Label": label.strip().lower(),
            }
            for term_url, label in mappings.items()
        }

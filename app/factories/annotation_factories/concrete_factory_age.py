from typing import Any, Dict
from app.factories.annotation_factories.factory_interface import (
    AnnotationFactory,
)
from app.products.annotations import Annotations
from app.products.is_about_age import IsAboutAge
from app.products.tsv_annotations import TSVAnnotations


class AgeFactory(AnnotationFactory):
    def create_annotation(
        self, parsed_output: Dict[str, Any]
    ) -> TSVAnnotations:
        annotation_instance = IsAboutAge(TermURL=parsed_output["TermURL"])
        description = "Age information"
        transformation_mapping = {
            "floatvalue": {"TermURL": "nb:FromFloat", "Label": "float value"},
            "integervalue": {
                "TermURL": "nb:FromInt",
                "Label": "integer value",
            },
            "europeandecimalvalue": {
                "TermURL": "nb:FromEuro",
                "Label": "European value decimals",
            },
            "boundedvalue": {
                "TermURL": "nb:FromBounded",
                "Label": "bounded value",
            },
            "iso8601": {
                "TermURL": "nb:FromISO8601",
                "Label": "period of time according to the ISO8601 standard",
            },
        }
        transformation_key = parsed_output.get("Format", "").strip().lower()
        transformation = transformation_mapping.get(transformation_key)
        annotations = Annotations(
            IsAbout=annotation_instance, Transformation=transformation
        )
        return TSVAnnotations(Description=description, Annotations=annotations)

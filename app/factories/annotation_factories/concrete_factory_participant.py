from typing import Any, Dict
from app.factories.annotation_factories.factory_interface import (
    AnnotationFactory,
)
from app.products.annotations import Annotations
from app.products.is_about_participant import IsAboutParticipant
from app.products.tsv_annotations import TSVAnnotations


class ParticipantFactory(AnnotationFactory):
    def create_annotation(
        self, parsed_output: Dict[str, Any]
    ) -> TSVAnnotations:
        annotation_instance = IsAboutParticipant(
            TermURL=parsed_output["TermURL"]
        )
        description = "A participant ID"
        annotations = Annotations(
            IsAbout=annotation_instance, Identifies="participant"
        )
        return TSVAnnotations(Description=description, Annotations=annotations)

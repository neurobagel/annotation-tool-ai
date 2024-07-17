from typing import Any, Dict
from app.factories.annotation_factories.factory_interface import (
    AnnotationFactory,
)
from app.products.annotations import Annotations
from app.products.is_about_session import IsAboutSession
from app.products.tsv_annotations import TSVAnnotations


class SessionFactory(AnnotationFactory):
    def create_annotation(
        self, parsed_output: Dict[str, Any]
    ) -> TSVAnnotations:
        annotation_instance = IsAboutSession(TermURL=parsed_output["TermURL"])
        description = "A session ID"
        annotations = Annotations(
            IsAbout=annotation_instance, Identifies="session"
        )
        return TSVAnnotations(Description=description, Annotations=annotations)

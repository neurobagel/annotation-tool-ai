# Abstract Factory Interface
from abc import ABC, abstractmethod
from typing import Any, Dict

from app.products.tsv_annotations import TSVAnnotations


class AnnotationFactory(ABC):
    @abstractmethod
    def create_annotation(
        self, parsed_output: Dict[str, Any]
    ) -> TSVAnnotations:
        pass

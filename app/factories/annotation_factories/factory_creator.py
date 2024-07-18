# Factory Creator
from typing import Optional
from app.factories.annotation_factories.concrete_factory_age import AgeFactory
from app.factories.annotation_factories.concrete_factory_assessmentTool import (  # noqa: E501
    AssessmentToolFactory,
)
from app.factories.annotation_factories.concrete_factory_diagnosis import (
    DiagnosisFactory,
)
from app.factories.annotation_factories.factory_interface import (
    AnnotationFactory,
)
from app.factories.annotation_factories.concrete_factory_participant import (
    ParticipantFactory,
)
from app.factories.annotation_factories.concrete_factory_session import (
    SessionFactory,
)
from app.factories.annotation_factories.concrete_factory_sex import SexFactory


class FactoryCreator:
    @staticmethod
    def get_factory(term_url: str) -> Optional[AnnotationFactory]:
        if term_url == "nb:ParticipantID":
            return ParticipantFactory()
        elif term_url == "nb:Age":
            return AgeFactory()
        elif term_url == "nb:Session":
            return SessionFactory()
        elif term_url == "nb:Sex":
            return SexFactory()
        elif term_url == "nb:Diagnosis":
            return DiagnosisFactory()
        elif term_url == "nb:Assessment":
            return AssessmentToolFactory()
        else:
            return None

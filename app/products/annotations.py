from typing import Dict, Optional, Union

from pydantic import BaseModel

from app.products.is_about_age import IsAboutAge
from app.products.is_about_assessmentTool import IsAboutAssessmentTool
from app.products.is_about_diagnosis import IsAboutGroup
from app.products.is_about_participant import IsAboutParticipant
from app.products.is_about_session import IsAboutSession
from app.products.is_about_sex import IsAboutSex


class Annotations(BaseModel):  # type: ignore
    IsAbout: Union[
        IsAboutParticipant,
        IsAboutSex,
        IsAboutAge,
        IsAboutSession,
        IsAboutGroup,
        IsAboutAssessmentTool,
    ]
    Identifies: Optional[str] = None
    Levels: Optional[Dict[str, Dict[str, str]]] = None
    Transformation: Optional[Dict[str, str]] = None
    IsPartOf: Optional[Dict[str, str]] = None

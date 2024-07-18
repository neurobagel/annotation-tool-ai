from pydantic import Field
from app.products.is_about_base import IsAboutBase


class IsAboutAssessmentTool(IsAboutBase):
    Label: str = Field(default="Assessment Tool")
    TermURL: str

from pydantic import Field
from app.products.is_about_base import IsAboutBase


class IsAboutGroup(IsAboutBase):
    Label: str = Field(default="Diagnosis variable")
    TermURL: str

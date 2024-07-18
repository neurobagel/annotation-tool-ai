from pydantic import Field
from app.products.is_about_base import IsAboutBase


class IsAboutSession(IsAboutBase):
    Label: str = Field(default="Run Identifier")
    TermURL: str

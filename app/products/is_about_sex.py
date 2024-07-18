from pydantic import Field
from app.products.is_about_base import IsAboutBase


class IsAboutSex(IsAboutBase):
    Label: str = Field(default="Sex variable")
    TermURL: str

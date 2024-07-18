from pydantic import Field
from app.products.is_about_base import IsAboutBase


class IsAboutAge(IsAboutBase):
    Label: str = Field(default="Age variable")
    TermURL: str

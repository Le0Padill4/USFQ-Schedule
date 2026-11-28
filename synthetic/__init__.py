"""Fixtures sinteticos reproducibles (NO son datos reales de la USFQ)."""

from .catalog import (
    SUPPORTED_CAREERS,
    CourseRec,
    CurriculumEntry,
    PrerequisiteGroup,
    SyntheticCatalog,
    eligible_courses,
)
from .generator import CatalogParams, generate_catalog, tiny_catalog

__all__ = [
    "SUPPORTED_CAREERS",
    "CatalogParams",
    "CourseRec",
    "CurriculumEntry",
    "PrerequisiteGroup",
    "SyntheticCatalog",
    "eligible_courses",
    "generate_catalog",
    "tiny_catalog",
]

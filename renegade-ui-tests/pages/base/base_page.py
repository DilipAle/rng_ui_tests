"""
pages/base/base_page.py — Renegade UI Tests
=============================================
Thin re-export of the shared BasePage.

All browser interaction methods (click, fill, goto, etc.) live in:
    shared/base_page.py

This file exists so page objects in this project can import locally:
    from pages.base.base_page import BasePage

Instead of importing from shared directly in every page object file.
The sys.path setup in conftest.py makes 'shared' importable.

To add a new shared method:
    Edit shared/base_page.py — it will be available in all 3 UI projects.
"""

from shared.base_page import BasePage

__all__ = ["BasePage"]

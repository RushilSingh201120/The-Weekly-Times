
"""Sphinx configuration for The Weekly Times documentation."""

import os
import sys
import django

# Add the project root to Python's import path.
sys.path.insert(0, os.path.abspath("../.."))

# Configure Django so Sphinx can import application modules.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "weekly_times_project.settings",
)


django.setup()

# Project information.
project = "The Weekly Times"
copyright = "2026, The Weekly Times Team"
author = "The Weekly Times Team"
release = "1.0"

# Sphinx extensions.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# General configuration.
templates_path = ["_templates"]
exclude_patterns = []
language = "en"

# HTML documentation theme.
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Include class and function documentation automatically.
autoclass_content = "both"
autodoc_member_order = "bysource"

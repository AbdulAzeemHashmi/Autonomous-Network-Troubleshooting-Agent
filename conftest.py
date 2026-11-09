"""
Root-level conftest.py
Ensures the project root directory is on sys.path before any test module
is imported. This is the fallback fix for the name clash between Python's
built-in 'code' module and this project's code/ package.
"""

import sys
import os

# Insert project root at position 0 so it takes priority over stdlib.
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


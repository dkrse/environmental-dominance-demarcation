"""Shared project paths. Import: from _paths import DATA, OUT, FIG"""
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
OUT  = os.path.join(ROOT, 'output')
FIG  = os.path.join(OUT, 'figures')
os.makedirs(FIG, exist_ok=True)

# apps/app_ct.py
# ============================================================
# Puente para el módulo de Tomografía Computarizada (CT)
# ============================================================
from dash import html
from .ct_modulos.interfaz import crear_layout_ct, registrar_callbacks_ct

def layout(pathname="/imaging/ct"):
    """
    Retorna el layout principal del módulo CT sincronizado con la URL.
    """
    return crear_layout_ct(pathname)

def register_callbacks(app):
    """
    Registra todos los callbacks del módulo CT.
    """
    registrar_callbacks_ct(app)
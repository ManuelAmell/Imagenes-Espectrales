"""Pruebas para funciones auxiliares de formato y metadatos en generar_notebooks.py.

Cubre:
- `lista(nombres)`: formateo de nombres en lenguaje natural ("A y B", "A, B y C").
- `dic_colores(materiales)` y `dic_nombres(materiales)`: generación de diccionarios Python en código generado.
"""
import pytest
from herramientas.generar_notebooks import lista, dic_colores, dic_nombres


class TestNotebookHelpers:
    """Pruebas de funciones auxiliares de generación de texto y diccionarios."""

    def test_lista_un_elemento(self):
        """Un solo elemento devuelve el nombre tal cual."""
        assert lista(["agua"]) == "agua"

    def test_lista_dos_elementos(self):
        """Dos elementos se unen con 'y'."""
        assert lista(["asfalto", "vegetación"]) == "asfalto y vegetación"

    def test_lista_tres_o_mas_elementos(self):
        """Tres o más elementos usan comas y terminan con ' y '."""
        assert lista(["asfalto", "techo de concreto", "vegetación"]) == "asfalto, techo de concreto y vegetación"
        assert lista(["a", "b", "c", "d"]) == "a, b, c y d"

    def test_dic_colores(self):
        """Genera la representación en string del diccionario de colores RGB."""
        materiales = [
            ("agua_salada", "agua salada", (0, 255, 255)),
            ("asfalto", "asfalto", (255, 0, 0)),
        ]
        res = dic_colores(materiales)
        assert res == '{"agua_salada":(0, 255, 255), "asfalto":(255, 0, 0)}'

    def test_dic_nombres(self):
        """Genera la representación en string del diccionario de nombres amigables."""
        materiales = [
            ("techo_concreto", "techo de concreto", (255, 255, 0)),
            ("vegetacion", "vegetación", (0, 255, 0)),
        ]
        res = dic_nombres(materiales)
        assert res == '{"techo_concreto":"techo de concreto", "vegetacion":"vegetación"}'

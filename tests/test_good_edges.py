import math
import tempfile
import pytest

from shadow.polyedr import Polyedr


def create_geom_file(content: str) -> str:
    """Создаёт временный .geom файл с заданным содержимым и возвращает его имя."""
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.geom', delete=False)
    f.write(content)
    f.close()
    return f.name


def test_empty_polyhedron():
    """Полиэдр без рёбер → характеристика = 0."""
    content = """1.0 0 0 0
0 0 0
"""
    filename = create_geom_file(content)
    poly = Polyedr(filename)
    assert poly.good_edges_projection_length() == 0.0


def test_single_edge_good_midpoint():
    """Одно ребро, середина которого — хорошая точка."""
    content = """1.0 0 0 0
2 1 1
0.1 0.6 0.0
1.1 0.6 0.0
3 2 1 2
"""
    filename = create_geom_file(content)
    poly = Polyedr(filename)
    # Длина проекции: dx=1.0, dy=0 → длина = 1.0
    assert poly.good_edges_projection_length() == 1.0


def test_single_edge_bad_midpoint():
    """Одно ребро, середина которого не является хорошей."""
    content = """1.0 0 0 0
2 1 1
-0.4 -0.4 0.0
0.4 0.4 0.0
3 2 1 2
"""
    filename = create_geom_file(content)
    poly = Polyedr(filename)
    assert poly.good_edges_projection_length() == 0.0



def test_cube_known_value():
    """Коробка (куб без одной грани) с вершинами ±0.75. Все середины рёбер 
    хорошие, но у 4 ребер проекция = 0 → характеристика = 1,5*8 = 12.
    """
    content = """1.0 0 0 0
8 6 24
-0.75 -0.75 0.75
-0.75 0.75 0.75
0.75 0.75 0.75
0.75 -0.75 0.75
-0.75 -0.75 -0.75
-0.75 0.75 -0.75
0.75 0.75 -0.75
0.75 -0.75 -0.75
4 1 2 3 4
4 5 6 2 1
4 4 3 7 8
4 5 1 4 8
4 8 7 6 5
"""
    filename = create_geom_file(content)
    poly = Polyedr(filename)
    assert poly.good_edges_projection_length() == 12.0


def test_cube_with_homothety_and_rotation():
    """Та же коробка, но с гомотетией и поворотами. Характеристика должна cтать 0."""
    content = """200.0 45.0 45.0 30.0
8 6 24
-0.75 -0.75 0.75
-0.75 0.75 0.75
0.75 0.75 0.75
0.75 -0.75 0.75
-0.75 -0.75 -0.75
-0.75 0.75 -0.75
0.75 0.75 -0.75
0.75 -0.75 -0.75
4 1 2 3 4
4 5 6 2 1
4 4 3 7 8
4 5 1 4 8
4 8 7 6 5
"""
    filename = create_geom_file(content)
    poly = Polyedr(filename)
    assert poly.good_edges_projection_length() == 0


def test_cube_with_good_edges():
    """Куб от -0.8 до 0.8 по всем осям. Середины рёбер, параллельных X и Y,
    являются хорошими. Длина проекции каждого такого ребра = 1.6.
    Всего 8 хороших рёбер, сумма = 12.8.
    """
    content = """1.0 0 0 0
8 6 24
-0.8 -0.8 -0.8
-0.8 -0.8 0.8
-0.8 0.8 -0.8
-0.8 0.8 0.8
0.8 -0.8 -0.8
0.8 -0.8 0.8
0.8 0.8 -0.8
0.8 0.8 0.8
4 1 2 4 3
4 1 2 6 5
4 2 4 8 6
4 3 4 8 7
4 1 3 7 5
4 5 6 8 7
"""
    filename = create_geom_file(content)
    poly = Polyedr(filename)
    result = poly.good_edges_projection_length()
    assert math.isclose(result, 12.8, rel_tol=1e-9)


def test_cube_with_good_edges():
    """Тот же куб, но с гомотетией и поворотами. Характеристика должна стать = 0.
    """
    content = """150.0 60.0 60.0 60.0
8 6 24
-0.8 -0.8 -0.8
-0.8 -0.8 0.8
-0.8 0.8 -0.8
-0.8 0.8 0.8
0.8 -0.8 -0.8
0.8 -0.8 0.8
0.8 0.8 -0.8
0.8 0.8 0.8
4 1 2 4 3
4 1 2 6 5
4 2 4 8 6
4 3 4 8 7
4 1 3 7 5
4 5 6 8 7
"""
    filename = create_geom_file(content)
    poly = Polyedr(filename)
    result = poly.good_edges_projection_length()
    assert math.isclose(result, 0, rel_tol=1e-9)


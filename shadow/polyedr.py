from math import pi, sqrt
from functools import reduce
from operator import add
from common.r3 import R3
from common.tk_drawer import TkDrawer


class Segment:
    """ Одномерный отрезок """
    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin

    def is_degenerate(self):
        return self.beg >= self.fin

    def intersect(self, other):
        if other.beg > self.beg:
            self.beg = other.beg
        if other.fin < self.fin:
            self.fin = other.fin
        return self

    def subtraction(self, other):
        return [Segment(
            self.beg, self.fin if self.fin < other.beg else other.beg),
            Segment(self.beg if self.beg > other.fin else other.fin, self.fin)]


class Edge:
    """ Ребро полиэдра """
    SBEG, SFIN = 0.0, 1.0

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin
        self.gaps = [Segment(Edge.SBEG, Edge.SFIN)]

    def shadow(self, facet):
        if facet.is_vertical():
            return
        shade = Segment(Edge.SBEG, Edge.SFIN)
        for u, v in zip(facet.vertexes, facet.v_normals()):
            shade.intersect(self.intersect_edge_with_normal(u, v))
            if shade.is_degenerate():
                return
        shade.intersect(
            self.intersect_edge_with_normal(
                facet.vertexes[0], facet.h_normal()))
        if shade.is_degenerate():
            return
        gaps = [s.subtraction(shade) for s in self.gaps]
        self.gaps = [
            s for s in reduce(add, gaps, []) if not s.is_degenerate()]

    def r3(self, t):
        return self.beg * (Edge.SFIN - t) + self.fin * t

    def intersect_edge_with_normal(self, a, n):
        f0, f1 = n.dot(self.beg - a), n.dot(self.fin - a)
        if f0 >= 0.0 and f1 >= 0.0:
            return Segment(Edge.SFIN, Edge.SBEG)
        if f0 < 0.0 and f1 < 0.0:
            return Segment(Edge.SBEG, Edge.SFIN)
        x = - f0 / (f1 - f0)
        return Segment(Edge.SBEG, x) if f0 < 0.0 else Segment(x, Edge.SFIN)


class Facet:
    """ Грань полиэдра """
    def __init__(self, vertexes):
        self.vertexes = vertexes

    def is_vertical(self):
        return self.h_normal().dot(Polyedr.V) == 0.0

    def h_normal(self):
        n = (
            self.vertexes[1] - self.vertexes[0]).cross(
            self.vertexes[2] - self.vertexes[0])
        return n * (-1.0) if n.dot(Polyedr.V) < 0.0 else n

    def v_normals(self):
        return [self._vert(x) for x in range(len(self.vertexes))]

    def _vert(self, k):
        n = (self.vertexes[k] - self.vertexes[k - 1]).cross(Polyedr.V)
        return n * \
            (-1.0) if n.dot(self.vertexes[k - 1] - self.center()) < 0.0 else n

    def center(self):
        return sum(self.vertexes, R3(0.0, 0.0, 0.0)) * \
            (1.0 / len(self.vertexes))


class Polyedr:
    """ Полиэдр """
    V = R3(0.0, 0.0, 1.0)

    def __init__(self, file):
        self.vertexes = []          # преобразованные вершины (для отрисовки)
        self.orig_vertexes = []     # исходные вершины (без преобразований)
        self.edges = []             # рёбра для отрисовки
        self.unique_edge_indices = set()   # множество уникальных пар индексов (i,j) с i<j
        self.facets = []

        with open(file) as f:
            for i, line in enumerate(f):
                if i == 0:
                    buf = line.split()
                    c = float(buf.pop(0))
                    alpha, beta, gamma = (float(x) * pi / 180.0 for x in buf)
                elif i == 1:
                    nv, nf, ne = (int(x) for x in line.split())
                elif i < nv + 2:
                    x, y, z = (float(x) for x in line.split())
                    # Сохраняем исходную вершину
                    self.orig_vertexes.append(R3(x, y, z))
                    # Преобразованная вершина (для отрисовки)
                    self.vertexes.append(R3(x, y, z).rz(alpha).ry(beta).rz(gamma) * c)
                else:
                    buf = line.split()
                    size = int(buf.pop(0))
                    indices = [int(n) - 1 for n in buf]
                    # Список преобразованных вершин грани
                    verts = [self.vertexes[i] for i in indices]
                    # Добавляем рёбра 
                    for n in range(size):
                        self.edges.append(Edge(verts[n-1], verts[n]))
                    # Запоминаем уникальные пары индексов исходных вершин
                    for n in range(size):
                        i = indices[n-1]
                        j = indices[n]
                        if i < j:
                            self.unique_edge_indices.add((i, j))
                        else:
                            self.unique_edge_indices.add((j, i))
                    # Грань для отрисовки
                    self.facets.append(Facet(verts))

    @staticmethod
    def is_good_point(p):
        """Проверяет, является ли точка p «хорошей» (в исходных координатах)."""
        return (abs(p.x) < 1.0 and abs(p.y) < 1.0 and abs(p.z) < 1.0 and
                (abs(p.x) > 0.5 or abs(p.y) > 0.5 or abs(p.z) > 0.5))

    def good_edges_projection_length(self):
        """Сумма длин проекций (на xy после преобразований) уникальных рёбер,
           середины которых в исходных координатах являются «хорошими» точками.
        """
        total = 0.0
        for i, j in self.unique_edge_indices:
            # Середина в исходных координатах
            mid_orig = (self.orig_vertexes[i] + self.orig_vertexes[j]) * 0.5
            if self.is_good_point(mid_orig):
                # Берём преобразованные координаты концов
                vi = self.vertexes[i]
                vj = self.vertexes[j]
                dx = vj.x - vi.x
                dy = vj.y - vi.y
                total += sqrt(dx*dx + dy*dy)
        return total

    def draw(self, tk):
        tk.clean()
        for e in self.edges:
            for f in self.facets:
                e.shadow(f)
            for s in e.gaps:
                tk.draw_line(e.r3(s.beg), e.r3(s.fin))

#!/usr/bin/env -S python3 -B

from time import time
from common.tk_drawer import TkDrawer
from shadow.polyedr import Polyedr

tk = TkDrawer()
try:
    for name in ["cube_intersect", "ccc", "cube", "box", "king", "cow"]:
        print("=============================================================")
        print(f"Начало работы с полиэдром '{name}'")
        poly = Polyedr(f"data/{name}.geom")
        good_len = poly.good_edges_projection_length()
        print(f"Сумма длин проекций рёбер с «хорошей» серединой: {good_len}")
        start_time = time()
        poly.draw(tk)
        delta_time = time() - start_time
        print(f"Изображение полиэдра '{name}' заняло {delta_time} сек.")
        input("Hit 'Return' to continue -> ")
except(EOFError, KeyboardInterrupt):
    print("\nStop")
    tk.close()


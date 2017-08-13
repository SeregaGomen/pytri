#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
from tri_view import TTriView
from tri_tri import TTri


def main():
    file_name = 'test/test0.rf'
    tri = TTri()

    tri.set_file_name(file_name)
    tri.set_angle_optimize(False)
    tri.set_length_optimize(True)
    tri.set_step(250)
#    tri.set_step(600)
    tri.set_eps(1.0e-6)
    tri.set_angle(15)
    tri.set_ratio(1.5)

    if tri.start() is False:
        return

    app = TTriView(Tk(), file_name, tri.x, tri.fe, tri.be, show_vertex=True, show_fe=True, show_be=True)
    app.mainloop()


if __name__ == "__main__":
    main()

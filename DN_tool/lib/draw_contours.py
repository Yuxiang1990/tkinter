import tkinter as tk
import os
import tkinter.messagebox
from PIL import ImageTk, Image
from DN_tool.lib.nii2plot_v1 import nii_draw
from DN_tool.lib.nrrd2plot_v1 import nrrd_draw
import numpy as np


class draw_contours:
    def __init__(self):
        self.shape = 500
        self.canvas_max = 2000
        self.nii_cmd = "python -m DN_tool.nii2plot_v1 -niimask %s -nii %s -o %s"
        self.nrrd_cmd = "python -m DN_tool.nrrd2plot_v1 -nrrd %s -nii %s -o %s"

        self.draw_contour_win = tk.Toplevel()
        self.draw_contour_win.geometry("800x800")
        self.draw_contour_win.title("Draw contous")
        nii_label = tk.Label(self.draw_contour_win,  font=('Times', 18, 'bold'), text="Nii img path:")
        nii_label.place(x=20, y=20, anchor='nw')
        mask_label = tk.Label(self.draw_contour_win, font=('Times', 18, 'bold'), text="Nii/Nrrd mask path:")
        mask_label.place(x=20, y=60, anchor='nw')
        out_label = tk.Label(self.draw_contour_win, font=('Times', 18, 'bold'), text="output path:")
        out_label.place(x=20, y=100, anchor='nw')

        self.niistr = tk.StringVar()
        self.maskstr = tk.StringVar()
        self.outpath = tk.StringVar()
        tk_path = tk.Entry(self.draw_contour_win, textvariable=self.niistr, width=80)
        tk_path.place(x=300, y=30, anchor='nw')
        tk_path = tk.Entry(self.draw_contour_win, textvariable=self.maskstr, width=80)
        tk_path.place(x=300, y=70, anchor='nw')
        tk_path = tk.Entry(self.draw_contour_win, textvariable=self.outpath, width=80)
        tk_path.place(x=300, y=110, anchor='nw')

        tk_btm = tk.Button(self.draw_contour_win, text="生成边缘勾勒", bg='green', fg='red',
                           font=('Helvetica', 20), command=self.draw)
        tk_btm.place(x=400, y=200, anchor='center')
        self.canvas = tk.Canvas(self.draw_contour_win, relief='raised', bg='black', height=800, width=1000)
        # self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.config(scrollregion=(0, 0, self.canvas_max, self.canvas_max))
        self.canvas.place(x=10, y=240, anchor='nw')
        self.image_list = []
        self.index = 0
        # scrollbar
        self.vbar = tk.Scrollbar(self.draw_contour_win, orient=tk.VERTICAL, bg='#87CEFA')
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.canvas.yview)
        self.hbar = tk.Scrollbar(self.draw_contour_win, orient=tk.HORIZONTAL, bg='#87CEFA')
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hbar.config(command=self.canvas.xview)
        self.canvas.config(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)

    def draw(self):
        if not os.path.exists(self.niistr.get()):
            tkinter.messagebox.showerror(title='Error', message='Exception happen, Pls check nii path.')
        if not os.path.exists(self.maskstr.get()):
            tkinter.messagebox.showerror(title='Error', message='Exception happen, Pls check mask path.')
        if not os.path.exists(self.outpath.get()):
            tkinter.messagebox.showwarning(title='warning', message='warning, Pls check out path.')
            os.makedirs(self.outpath.get())

        niistr = self.niistr.get()
        maskstr = self.maskstr.get()
        outpath = self.outpath.get()
        if maskstr.endswith(".nrrd"):
            png = nrrd_draw(niistr, maskstr, outpath)
        elif maskstr.endswith(".nii"):
            png = nii_draw(niistr, maskstr, outpath)
        r = Image.fromarray(png[..., 0]).convert("L")
        g = Image.fromarray(png[..., 1]).convert("L")
        b = Image.fromarray(png[..., 2]).convert("L")
        self.image_list.append(ImageTk.PhotoImage(Image.merge("RGB", (r, g, b)).resize((self.shape, self.shape))))
        # calc canvas_locx and canvas_locy
        a, v = np.divmod(self.index, self.canvas_max // self.shape)
        y = a * self.shape
        x = v * self.shape
        self.canvas.create_image(x, y, anchor='nw', image=self.image_list[self.index])
        self.index += 1



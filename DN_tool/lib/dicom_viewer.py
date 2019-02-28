import tkinter as tk
import os
import tkinter.messagebox
from DN_tool.Dcm_Series import Series
from numpy import clip, uint8
from PIL import Image, ImageTk


class dicom_viewer():
    def __init__(self):
        self.min_hu = tk.IntVar()
        self.min_hu.set(-1000)
        self.max_hu = tk.IntVar()
        self.max_hu.set(400)
        self.dicompath = tk.StringVar()
        self.dicominfo = tk.StringVar()
        self.coordzyx = tk.StringVar()
        self.dicompath.set("input dicom path")
        self.dcm_viewer_win = tk.Toplevel()
        self.dcm_viewer_win.geometry("800x800")
        self.dcm_viewer_win.title("Dicom viewer")
        self.z = 0
        tk_label = tk.Label(self.dcm_viewer_win, text="Dicom 路径:")
        tk_label.place(x=50, y=20, anchor='center')

        tk_label = tk.Label(self.dcm_viewer_win, textvariable=self.dicominfo)
        tk_label.place(x=50, y=70)

        tk_path = tk.Entry(self.dcm_viewer_win, textvariable=self.dicompath, width=80)
        tk_path.place(x=400, y=20, anchor='center')

        tk_btm = tk.Button(self.dcm_viewer_win, text="确定", command=self.getarr)
        tk_btm.place(x=400, y=50, anchor='center')

        self.canvas = tk.Canvas(self.dcm_viewer_win, height=512, width=512)
        self.canvas.place(x=390, y=390, anchor='center')
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.bind("<Button 1>", self.callback)

    def norm(self, png):
        _min_hu = self.min_hu.get()
        _max_hu = self.max_hu.get()
        png = clip(png, _min_hu, _max_hu)
        png = (png - png.min()) / (png.max() - png.min())
        return (png * 255).astype(uint8)

    def getarr(self):
        if not os.path.exists(self.dicompath.get()):
            tkinter.messagebox.showerror(title='Error', message='Exception happen, Pls check path.')
        else:
            ds = Series([self.dicompath.get()])
            self.dicom_arr = ds.Dcm_series_arr
            self.dicominfo.set("dicominfo (space={} sizezyx={})".format(ds.Dcm_series_spacing, ds.Dcm_series_size))
            tk_scale = tk.Scale(self.dcm_viewer_win, label='Adjust Z', from_=0, to=self.dicom_arr.shape[0] - 1, orient=tk.VERTICAL,
                                length=400, showvalue=1, tickinterval=2, resolution=1, command=self.draw)
            tk_scale.place(x=700, y=50)
            tk.Label(self.dcm_viewer_win, text="min_hu:").place(y=660, x=160)
            tk.Label(self.dcm_viewer_win, text="max_hu:").place(y=660, x=400)
            tk.Entry(self.dcm_viewer_win, textvariable=self.min_hu, width=8).place(y=660, x=220)
            tk.Entry(self.dcm_viewer_win, textvariable=self.max_hu, width=8).place(y=660, x=460)
            tk.Label(self.dcm_viewer_win, textvariable=self.coordzyx, bg='black', fg='white').place(y=140, x=500)

    def draw(self, z):
        try:
            self.z = int(z)
            png = self.dicom_arr[int(z)]
            png = self.norm(png)
            # png = cv2.resize(png, (500, 500))
            # cv2.imwrite("tmp.png", png)
        except:
            tkinter.messagebox.showerror(title='Error', message='path not exist, pls check!')
        # image_file = tk.PhotoImage(file='tmp.png')
        self.image_file = ImageTk.PhotoImage(Image.fromarray(png))
        self.canvas.create_image(0, 0, anchor='nw', image=self.image_file)

    def callback(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasx(event.y)
        self.coordzyx.set("z:{} y:{} x:{}".format(self.z, int(y), int(x)))
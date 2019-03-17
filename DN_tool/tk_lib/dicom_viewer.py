import os
import tkinter as tk
import tkinter.messagebox
import cv2
from PIL import Image, ImageTk
from numpy import clip, unique, load, uint8
import numpy as np
import re
from DN_tool.lib.Dcm_Series import Series

rgb_list = {0: (70,130,180),
            1: (152,251,152),
            2: (255,255,0),
            3: (255,0,0),
            4: (211,211,211)}

rgb_description = {0: "4:RUL", 1: "5:RML", 2: "6:RLL", 3: "7:LUL", 4: "8:LLL"}


class dicom_viewer():
    def __init__(self):
        self.min_hu = tk.IntVar()
        self.min_hu.set(-1000)
        self.max_hu = tk.IntVar()
        self.max_hu.set(400)
        self.dicompath = tk.StringVar()
        self.maskpath = tk.StringVar()

        self.dicominfo = tk.StringVar()
        self.coordzyx = tk.StringVar()
        self.coordzyx1 = tk.StringVar()

        self.dicompath.set("input dicom path")
        self.dcm_viewer_win = tk.Toplevel()
        self.dcm_viewer_win.geometry("1500x800")
        self.dcm_viewer_win.title("Dicom viewer")
        self.z = 0
        tk_label = tk.Label(self.dcm_viewer_win, text="Dicom & npz 路径:")
        tk_label.place(x=70, y=20, anchor='center')

        tk_label = tk.Label(self.dcm_viewer_win, text="mask 路径:")
        tk_label.place(x=800, y=20, anchor='center')

        tk_label = tk.Label(self.dcm_viewer_win, textvariable=self.dicominfo)
        tk_label.place(x=70, y=70)

        tk_path = tk.Entry(self.dcm_viewer_win, textvariable=self.dicompath, width=80)
        tk_path.place(x=430, y=20, anchor='center')

        tk_path = tk.Entry(self.dcm_viewer_win, textvariable=self.maskpath, width=80)
        tk_path.place(x=840, y=20, anchor='w')

        tk_btm = tk.Button(self.dcm_viewer_win, text="确定", command=self.getarr)
        tk_btm.place(x=400, y=50, anchor='center')
        # lobe description
        self.rul = tk.Label(self.dcm_viewer_win, text="4:RUL", bg="#4682B4", font="24")
        self.rul.place(x=50, y=200)
        self.rml = tk.Label(self.dcm_viewer_win, text="5:RML", bg="#98FB98", font="24")
        self.rml.place(x=50, y=220)
        self.rll = tk.Label(self.dcm_viewer_win, text="6:RLL", bg="#FFFF00", font="24")
        self.rll.place(x=50, y=240)
        self.lul = tk.Label(self.dcm_viewer_win, text="7:LUL", bg="#FF0000", font="24")
        self.lul.place(x=50, y=260)
        self.lll = tk.Label(self.dcm_viewer_win, text="8:LLL", bg="#D3D3D3", font="24")
        self.lll.place(x=50, y=280)

        self.canvas = tk.Canvas(self.dcm_viewer_win, height=512, width=512)
        self.canvas.place(x=140, y=140, anchor='nw')
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.bind("<Button 1>", self.callback)

        self.canvas1 = tk.Canvas(self.dcm_viewer_win, height=512, width=512)
        self.canvas1.place(x=140 + 512, y=140, anchor='nw')
        self.canvas1.config(scrollregion=self.canvas1.bbox("all"))
        self.canvas1.bind("<Button 1>", self.callback1)

        self.warning_cnt = 0

    def norm(self, png):
        _min_hu = self.min_hu.get()
        _max_hu = self.max_hu.get()
        png = clip(png, _min_hu, _max_hu)
        png = (png - png.min()) / (png.max() - png.min())
        return (png * 255).astype(uint8)

    def getarr(self):
        if not (os.path.exists(self.dicompath.get()) or os.path.exists(self.maskpath.get())):
            tkinter.messagebox.showerror(title='Error', message='Exception happen, Pls check path.')
        else:
            # img|raw|voxel|img_norm
            npzfiles = self.dicompath.get()
            try:
                if npzfiles.endswith(".npz"):
                    with load(npzfiles) as f:
                        string = " ".join(f.files)
                        self.dicom_arr = f[re.findall("(voxel|raw|img_norm)", string)[0]]
                        self.dicominfo.set("dicominfo (sizezyx={})".format(self.dicom_arr.shape))
                else:
                    ds = Series([self.dicompath.get()])
                    self.dicom_arr = ds.Dcm_series_arr
                    self.dicominfo.set("dicominfo (space={} sizezyx={})".format(ds.Dcm_series_spacing, ds.Dcm_series_size))
            except:
                tkinter.messagebox.showerror(title='Error', message='npzfiles parse failed.')
            try:
                maskfiles = self.maskpath.get()
                with load(maskfiles) as f:
                    string = " ".join(f.files)
                    if 'seg' in f.files:
                        self.mask_arr = f['seg']
                    else:
                        self.mask_arr = f[re.findall("(\w*mask|voxel)", string)[0]]
                if len(unique(self.mask_arr)) == 2:
                    self.mask_arr = self.mask_arr.astype(uint8) * 255
                else:
                    self.mask_arr = np.repeat(self.mask_arr[..., np.newaxis].astype(uint8), axis=-1, repeats=3)
                    # lobe mask, nodule mask
                    labels = np.unique(self.mask_arr).tolist()
                    labels.remove(0)
                    print(labels)
                    for label in labels:
                        remain = (label + 1) % 5
                        self.mask_arr[self.mask_arr[..., 0] == label] = np.array(rgb_list[remain])

            except Exception as e:
                tkinter.messagebox.showerror(title='Error', message='maskfiles parse failed. %s' % e)

            try:
                shape = self.dicom_arr.shape
            except:
                shape = self.mask_arr.shape
            tk_scale = tk.Scale(self.dcm_viewer_win, label='Adjust Z', from_=0, to=shape[0] - 1, orient=tk.VERTICAL,
                                length=400, showvalue=1, tickinterval=2, resolution=1, command=self.draw)
            tk_scale.place(x=1100, y=100)
            tk.Label(self.dcm_viewer_win, text="min_hu:").place(y=660, x=160)
            tk.Label(self.dcm_viewer_win, text="max_hu:").place(y=660, x=400)
            tk.Entry(self.dcm_viewer_win, textvariable=self.min_hu, width=8).place(y=660, x=220)
            tk.Entry(self.dcm_viewer_win, textvariable=self.max_hu, width=8).place(y=660, x=460)
            tk.Label(self.dcm_viewer_win, textvariable=self.coordzyx, bg='black', fg='white').place(y=140, x=500)
            tk.Label(self.dcm_viewer_win, textvariable=self.coordzyx1, bg='black', fg='white').place(y=140, x=500 + 512)


    def draw(self, z):
        try:
            self.z = int(z)
            png = self.dicom_arr[int(z)]
            png = self.norm(png)
        except Exception as e:
            if not self.warning_cnt:
                self.warning_cnt += 1
                tkinter.messagebox.showerror(title='Error', message="draw failed, %s" % e)
        try:
            mask = self.mask_arr[int(z)]
        except Exception as e:
            if not self.warning_cnt:
                self.warning_cnt += 1
                tkinter.messagebox.showerror(title='Error', message="draw failed, %s" % e)
        # image_file = tk.PhotoImage(file='tmp.png')
        try:
            self.image_file = ImageTk.PhotoImage(Image.fromarray(png))
            self.canvas.create_image(0, 0, anchor='nw', image=self.image_file)
        except:
            print("draw image failed")
        try:
            self.mask_file = ImageTk.PhotoImage(Image.fromarray(mask))
            self.canvas1.create_image(0, 0, anchor='nw', image=self.mask_file)
        except:
            print("draw mask failed")

    def callback(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasx(event.y)
        self.coordzyx.set("z:{} y:{} x:{}".format(self.z, int(y), int(x)))

    def callback1(self, event):
        x = self.canvas1.canvasx(event.x)
        y = self.canvas1.canvasx(event.y)
        self.coordzyx1.set("z:{} y:{} x:{}".format(self.z, int(y), int(x)))
import os
import tkinter as tk
import tkinter.messagebox
from DN_tool.tagger import FlaskServer
import pandas as pd
import numpy as np
import urllib
import json
from datetime import datetime


class check_nodule():
    def __init__(self):
        self.WIDTH = 40
        self.columns = ['seriesuid', 'coordZ', 'coordY', 'coordX', 'diameter_mm', 'probability', 'is_nodule']
        self.check_nodule_win = tk.Toplevel()
        self.check_nodule_win.geometry("800x800")
        self.check_nodule_win.title("Draw controus")
        npz_dir = tk.Label(self.check_nodule_win, font=('Times', 15, 'bold'), fg='blue',
                             text="NPZ Dir:")
        npz_dir.place(x=20, y=20, anchor='nw')
        csv_file = tk.Label(self.check_nodule_win, font=('Times', 15, 'bold'), fg='blue',
                              text="CSV File `seriesuid,coordZ,coordY,coordX, diameter_mm,probability,is_nodule`:")
        csv_file.place(x=20, y=60, anchor='nw')
        out_label = tk.Label(self.check_nodule_win, font=('Times', 15, 'bold'), fg='blue', text="new csvfile outpath:")
        out_label.place(x=20, y=100, anchor='nw')

        port = tk.Label(self.check_nodule_win, font=('Times', 15, 'bold'), fg='blue', text="server port:")
        port.place(x=20, y=140, anchor='nw')

        self.npzstr = tk.StringVar()
        self.csvstr = tk.StringVar()
        self.outpath = tk.StringVar()
        self.port = tk.IntVar()
        tk_path = tk.Entry(self.check_nodule_win, textvariable=self.npzstr, width=80)
        tk_path.place(x=20, y=40, anchor='nw')
        tk_path = tk.Entry(self.check_nodule_win, textvariable=self.csvstr, width=80)
        tk_path.place(x=20, y=80, anchor='nw')
        tk_path = tk.Entry(self.check_nodule_win, textvariable=self.outpath, width=80)
        tk_path.place(x=20, y=120, anchor='nw')
        tk_path = tk.Entry(self.check_nodule_win, textvariable=self.port, width=10)
        tk_path.place(x=180, y=145, anchor='nw')

        tk_btm0 = tk.Button(self.check_nodule_win, text="疑似结节人工确认", bg='green', fg='red',
                           font=('Helvetica', 15), command=self.check)
        tk_btm0.place(x=200, y=200, anchor='center')

        tk_btm1 = tk.Button(self.check_nodule_win, text="立刻保存结果", bg='green', fg='red',
                           font=('Helvetica', 15), command=self.save)
        tk_btm1.place(x=500, y=200, anchor='center')

        tk_btm2 = tk.Button(self.check_nodule_win, text="stop", bg='green', fg='red',
                            font=('Helvetica', 15), command=self.stop)
        tk_btm2.place(x=700, y=200, anchor='center')
        # create server
        self.server = FlaskServer()


    def check(self):
        if not os.path.exists(self.npzstr.get()):
            tkinter.messagebox.showerror(title='Error', message='Exception happen, Pls check npz path.')
            return 0
        if not os.path.exists(self.csvstr.get()):
            tkinter.messagebox.showerror(title='Error', message='Exception happen, Pls check csv path.')
            return 0
        if not os.path.exists(self.outpath.get()):
            tkinter.messagebox.showerror(title='Error', message='Exception happen, Pls check out path.')
            return 0
        if (int(self.port.get()) < 5005) | (int(self.port.get()) > 6000):
            tkinter.messagebox.showerror(title='Error', message='suggest port  5005 < id < 6000')
            return 0
        df = pd.read_csv(self.csvstr.get())
        if len(set(df.columns) & set(self.columns)) != len(self.columns):
            tkinter.messagebox.showerror(title='Error', message='Exception happen, Pls check csvfile columns.')
            return 0
        check_names = sorted(df['seriesuid'].unique())
        for i in check_names:
            uid = os.path.basename(i)
            try:
                data, roi = self.uid_to_info(uid, df)
            except:
                continue
            self.server.serve(field=uid, data=data, roi=roi)
        self.server.run(port=int(self.port.get()))
        tkinter.messagebox.showinfo(title='Info', message="please run `http://localhost:{port}`")

    def uid_to_info(self, uid, df):
        ret = []
        path = os.path.join(self.npzstr.get(), uid + ".npz")
        print(path)
        data = np.load(path)['raw']
        data = np.clip(data, -1000, 400)
        data = (((data - data.min()) / (data.max() - data.min())) * 255).astype(np.uint8)
        cand_df = df[df['seriesuid'] == uid]
        for _, row in cand_df.iterrows():
            x, y, z, is_nodule, p = row.loc[['coordX', 'coordY', 'coordZ', 'is_nodule', 'probability']]
            # x,y,z, = row.loc[['coordX','coordY','coordZ']]
            # is_nodule = "yes"
            # p = 0.1
            if np.isnan(is_nodule):
                tag = "pass"
            elif (is_nodule == 0) | (is_nodule == "no"):
                tag = "no"
            elif (is_nodule == 1) | (is_nodule == "yes"):
                tag = "yes"

            ret.append({'p':p,'r':self.WIDTH,'x':x,'y':y,'z':z,'tag':tag})
        return data, ret

    def save(self):
        try:
            port = int(self.port.get())
            out = self.outpath.get()
            now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            with urllib.request.urlopen('http://localhost:{}/rois/'.format(port)) as j:
                lst = json.loads(j.read().decode('utf-8'))['rois']
                df = pd.DataFrame(lst, columns=('seriesuid', 'coordX', 'coordY', 'coordZ', 'probability', 'tag'))
            df.to_csv(os.path.join(out, now + ".csv"),index=None)
            tkinter.messagebox.showinfo(title='Info', message='save success')

        except:
            tkinter.messagebox.showerror(title='Error', message='save error, pls check')

    def stop(self):
        self.server.reset()

import tkinter as tk
from DN_tool.tk_lib.dicom_viewer import dicom_viewer
from DN_tool.tk_lib.draw_contours import draw_contours
from DN_tool.tk_lib.check_nodule import check_nodule


window = tk.Tk()
window.title("Dn tools v1.0.0 (design by yuxiang)")
window.geometry("600x400")


memubar = tk.Menu(window)
filemenu = tk.Menu(memubar, tearoff=0)
memubar.add_cascade(label='Tools', menu=filemenu)
filemenu.add_command(label='dicom_viewer', command=dicom_viewer)
filemenu.add_command(label='draw_contours', command=draw_contours)
filemenu.add_command(label='check_nodule', command=check_nodule)


window.config(menu=memubar)
# welcome image
welcome = "Welcome to DN Tools"
tk.Label(window, text=welcome, fg='blue', font=('Italics', 30, 'bold')).place(x=300, y=50, anchor='center')

func1 = "1.tool->dicom_viewer, used for view dicom;"
tk.Label(window, text=func1, font=('Italics', 16)).place(y=150, x=10)
func2 = "2.tool->draw_contours, used for view draw contours for nii;"
tk.Label(window, text=func2, font=('Italics', 16)).place(y=200, x=10)
func3 = "3.tool->check_nodule, used for view check_nodule;"
tk.Label(window, text=func3, font=('Italics', 16)).place(y=250, x=10)

window.mainloop()
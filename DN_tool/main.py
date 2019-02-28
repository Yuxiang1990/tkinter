import tkinter as tk
from DN_tool.lib.dicom_viewer import dicom_viewer
from DN_tool.lib.draw_contours import draw_contours


window = tk.Tk()
window.title("Dn tools v1.0.0 (design by yuxiang)")
window.geometry("600x400")


memubar = tk.Menu(window)
filemenu = tk.Menu(memubar, tearoff=0)
memubar.add_cascade(label='Tools', menu=filemenu)
filemenu.add_command(label='dicom_viewer', command=dicom_viewer)
filemenu.add_command(label='draw_contours', command=draw_contours)

window.config(menu=memubar)
# welcome image
welcome = "Welcome to DN Tools"
tk.Label(window, text=welcome, fg='blue', font=('Italics', 30, 'bold')).place(x=300, y=50, anchor='center')

func1 = "1.tool->dicom_viewer, used for view dicom;"
tk.Label(window, text=func1, font=('Italics', 16)).place(y=150, x=10)

window.mainloop()
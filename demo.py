#from tkinter.ttk import *
from tkinter import *
from tkinter import ttk

def calc(event):
    a = float(t1.get())
    b = float(t2.get())
    dic = {0:a+b,1:a-b,2:a*b,3:a/b}
    c = dic[comb.current()]
    lbl.config(text=str(c))

root = Tk()
root.title('四则运算')
root.geometry('320x240')

t1 = Entry(root)
t1.place(relx=0.1,rely=0.1,relwidth=0.2,relheight=0.1)

t2 = Entry(root)
t2.place(relx=0.5,rely=0.1,relwidth=0.2,relheight=0.1)

comb = ttk.Combobox(root, values=['加','减','乘','除',])
comb.place(relx=0.1,rely=0.5,relwidth=0.2)
comb.bind('<<ComboboxSelected>>', calc)

lbl=Label(root, text='结果')
lbl.place(relx=0.5,rely=0.7,relwidth=0.2,relheight=0.3)

root.mainloop()

#/etc/python

from Tkinter import *

def remove_label():
    if len(buttons) > 0:
        toRemove = buttons.pop()
        toRemove.destroy();

def add_label():
    new_label = Label(root, text=data1.get(), fg="green")
    buttons.append(new_label)
    new_label.pack()
    clear_field()

    
def clear_field():
    data1.set("");
    new_label.get()

root = Tk()
root.title("SDIRC")
root.geometry("1000x400+200+200")
root.configure(background="black")

data1 = StringVar()
data1.set("default")
buttons = []
button = Button(root, text="red", bg="red", activebackground="blue" )
button.configure(command=remove_label)
button.pack()

button2 = Button(root, text="blue", bg="green", command=add_label)
button2.pack()

entry = Entry(root, bg="white", textvariable=data1)
entry.pack()


root.mainloop()

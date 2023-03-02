# Import the required libraries
import tkinter as tk
from tkinter import font

main_window = tk.Tk()
screen_width = main_window.winfo_screenwidth()
screen_height = main_window.winfo_screenheight()
main_window.geometry(f'{screen_width}x{screen_height}')
main_window.resizable(False, False)
main_window.wm_attributes('-fullscreen', 'True')

main_font = font.Font(family='TH Niramit AS', size='22', weight='bold')
test_font = font.Font(family='TH Niramit AS', size='200', weight='bold')

home_frame = tk.Frame(main_window)
test_frame = tk.Frame(main_window)

def show_home_frame():
   home_frame.pack(fill='both', expand=1)
   test_frame.pack_forget()

def show_test_frame():
   test_frame.pack(fill='both', expand=1)
   home_frame.pack_forget()
# ======== home frame ======================================================================
config_frame = tk.Frame(master=home_frame,width=500,height=500,bg='#FFFFFF')
config_frame.place(relx=0.5, rely=0.5,anchor=tk.CENTER)

select_exp_label = tk.Label(master=config_frame,text="เลือกการทดลอง",font=main_font)
select_exp_label.grid(row=0,column=0,sticky=tk.W)

btn2 = tk.Button(master=config_frame, text="เริ่มการทดลอง", font=main_font, command=show_test_frame)
btn2.grid(row=3,column=0)


#======== test frame ===============================================================
btn1 = tk.Button(test_frame, text="Switch to Greet", font=main_font, command=show_home_frame)
btn1.pack(pady=20)
show_home_frame()

main_window.mainloop()
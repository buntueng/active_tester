# Import the required libraries
import tkinter as tk
from tkinter import font
import customtkinter
from pathlib import Path
import os
import yaml
from yaml.loader import SafeLoader
import logging

current_path = Path(__file__).resolve().parents[0]
experiments_path = Path(current_path,'experiments')
results_path = Path(current_path,'results')
yml_config_path = Path(current_path, 'config.yml')
logging_file_path = Path(current_path, 'log_app.log')
#===================== setup logging module =========================================================================
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

fileHandler = logging.FileHandler(filename=logging_file_path)
fileHandler.setFormatter(logging_format)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging_format)
logger.addHandler(consoleHandler)
# =========================== sub program ==========================================================================
def read_yml(file_path):
    yml_params = None
    if file_path.is_file():
        with open(file_path,'r') as yml_file:
            yml_params = yaml.load(yml_file, Loader=SafeLoader)
    else:
        logging.warning("file path is not here")
    return yml_params

main_window = tk.Tk()
screen_width = main_window.winfo_screenwidth()
screen_height = main_window.winfo_screenheight()
main_window.geometry(f'{screen_width}x{screen_height}')
main_window.resizable(False, False)
main_window.wm_attributes('-fullscreen', 'True')

main_thai_font = customtkinter.CTkFont(family='TH Niramit AS', size=30)
main_eng_font = customtkinter.CTkFont(family='TH Niramit AS', size=20)
test_font = font.Font(family='TH Niramit AS', size='200', weight='bold')

home_frame = tk.Frame(main_window)
test_frame = tk.Frame(main_window)
# ===========================================================================================
def show_home_frame():
   home_frame.pack(fill='both', expand=1)
   test_frame.pack_forget()

def show_test_frame():
   test_frame.pack(fill='both', expand=1)
   home_frame.pack_forget()

def start_button_pressed():
   pass
# ======== home frame ======================================================================
config_params = read_yml(yml_config_path)
logging.debug(config_params)
exp_selectable = os.listdir(experiments_path)
if len(exp_selectable) > 0:
   select_exp_var = customtkinter.StringVar(value=exp_selectable[0])
else:
   select_exp_var = customtkinter.StringVar()

config_frame = customtkinter.CTkFrame(home_frame,width=200,height=200,corner_radius=10,fg_color='#FFFFFF')
config_frame.place(relx=0.5, rely=0.5,anchor=tk.CENTER)

select_exp_label = customtkinter.CTkLabel(config_frame,text="เลือกการทดสอบ",font=main_thai_font,fg_color="#FFFFFF")
select_exp_option = customtkinter.CTkOptionMenu(master=config_frame, values=[], variable=select_exp_var,font=main_eng_font)

if len(exp_selectable) > 0:
   select_exp_option.configure(values=exp_selectable)

start_button = customtkinter.CTkButton(master=config_frame, text="เริ่มการทดสอบ",width=300,height=50, font=main_thai_font, command=start_button_pressed)

select_exp_label.grid(row=0,column=0,sticky=tk.W,padx=(50,10),pady=(50,0))
select_exp_option.grid(row=0,column=1,sticky=tk.W,padx=(0,50),pady=(50,0))
start_button.grid(row=1,column=0,columnspan=2,pady=(20,50))


#======== test frame ===============================================================
btn1 = tk.Button(test_frame, text="Switch to Greet", font=main_eng_font, command=show_home_frame)
btn1.pack(pady=20)
show_home_frame()

#============== add events =======================================================
main_window.bind('<Escape>', lambda e: main_window.destroy())


main_window.mainloop()
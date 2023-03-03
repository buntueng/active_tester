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
test_font = font.Font(family='TH Niramit AS', size='120', weight='bold')

home_frame = tk.Frame(main_window)
test_frame = tk.Frame(main_window)

message_label = tk.StringVar()
# ===========================================================================================
main_state = 0
terminate_loop = False
test_param = None
test_result = []

def change_background():
   test_frame.config(background='red')

def show_home_frame():
   home_frame.pack(fill='both', expand=1)
   # home_frame.config(background='#FFFFFF')
   test_frame.pack_forget()

def show_test_frame():
   test_frame.pack(fill='both', expand=1)
   test_frame.config(background='#FFFFFF')
   home_frame.pack_forget()

def start_button_pressed():
   global main_state
   global terminate_loop
   global test_param

   

   test_param_path = Path(current_path,"experiments")
   test_param_path = Path(test_param_path,select_exp_option.get())
   param_file_obj = open(test_param_path,"r",encoding="utf-8")
   test_param = param_file_obj.readlines()
   show_test_frame()
   main_state = 0
   terminate_loop = False
   run_state()


def run_state():
   global main_state
   global terminate_loop
   global test_param
   global test_result
   global config_params
   if main_state == 0:
      message_label.set("การทดสอบจะเริ่มใน \n 5 วินาที")
      main_state = 1
   elif main_state == 1:
      message_label.set("การทดสอบจะเริ่มใน \n 4 วินาที")
      main_state = 2
   elif main_state == 2:
      message_label.set("การทดสอบจะเริ่มใน \n 3 วินาที")
      main_state = 3
   elif main_state == 3:
      message_label.set("การทดสอบจะเริ่มใน \n 2 วินาที")
      main_state = 4
   elif main_state == 4:
      message_label.set("การทดสอบจะเริ่มใน \n 1 วินาที")
      main_state = 5
   elif main_state == 5:
      main_state = 6
      terminate_loop = True
      current_color,current_text = test_param[0].strip().split(",")
      test_frame.config(background=current_color)
      test_label.config(background=current_color)
      message_label.set(current_text)

   if not terminate_loop:
      main_window.after(1000,run_state)
   else:
      logging.debug("Exit test")

   
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
test_label = tk.Label(master=test_frame,textvariable = message_label,font=test_font,background='#FFFFFF')
test_label.place(relx=0.5, rely=0.5,anchor=tk.CENTER)
show_home_frame()

#============== add events =======================================================
main_window.bind('<Escape>', lambda e: main_window.destroy())


main_window.mainloop()
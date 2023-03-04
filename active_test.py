# Import the required libraries
import tkinter as tk
from tkinter import font
import customtkinter
from pathlib import Path
import os
import yaml
from yaml.loader import SafeLoader
import logging
import time
import sys
import serial
import glob

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

def list_serial_ports():
   if sys.platform.startswith('win'):
      ports = ['COM%s' % (i + 1) for i in range(2,20)]
   elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
      # this excludes your current terminal "/dev/tty"
      ports = glob.glob('/dev/tty[A-Za-z]*')
   elif sys.platform.startswith('darwin'):
      ports = glob.glob('/dev/tty.*')
   else:
      raise EnvironmentError('Unsupported platform')
   result = []
   for port in ports:
      try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
      except (OSError, serial.SerialException):
            pass
   return result

main_window = tk.Tk()
screen_width = main_window.winfo_screenwidth()
screen_height = main_window.winfo_screenheight()
main_window.geometry(f'{screen_width}x{screen_height}')
main_window.resizable(False, False)
main_window.wm_attributes('-fullscreen', 'True')

main_thai_font = customtkinter.CTkFont(family='TH Niramit AS', size=30)
main_eng_font = customtkinter.CTkFont(family='TH Niramit AS', size=20)
timer_font = customtkinter.CTkFont(family='TH Niramit AS', size=40)
test_font = font.Font(family='TH Niramit AS', size='120', weight='bold')

home_frame = tk.Frame(main_window)
test_frame = tk.Frame(main_window)

message_label = tk.StringVar()
timer_display = tk.StringVar()
select_comport_var = tk.StringVar()
# ===========================================================================================
main_state = 0
state_timer = None
start_time = None
timeout_ms = 10000        # set timeout = 10 second
test_param = None
test_result = []

serial_port = None

def current_millis():
    return round(time.time() * 1000)

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

def show_result_frame():
   pass

def start_button_pressed():
   global main_state
   global test_param

   if select_comport_option.get() != "" and select_exp_option.get() != "":
      test_param_path = Path(current_path,"experiments")
      test_param_path = Path(test_param_path,select_exp_option.get())
      param_file_obj = open(test_param_path,"r",encoding="utf-8")
      test_param = param_file_obj.readlines()
      main_state = 0
      show_test_frame()
      run_state()
   else:
      if select_exp_option.get() == "" and select_comport_option.get() == "":
         info_message = "โปรดเช็คไฟล์ทดสอบและคอมพอร์ต"
      elif select_exp_option.get() == "" and select_comport_option.get() != "":
         info_message = "โปรดเช็คไฟล์ทดสอบ"
      elif select_exp_option.get() != "" and select_comport_option.get() == "":
         info_message = "โปรดเช็คคอมพอร์ต"
      tk.messagebox.showinfo(title="ไม่สามารถทดสอบได้",message=info_message)


def run_state():
   global main_state
   global test_param
   global test_result
   global config_params
   global state_timer
   global start_time
   global timeout_ms
   global timer_display
   global serial_port
   if main_state == 0:
      serial_port = serial.Serial(port=select_comport_option.get(),baudrate=9600,bytesize=8,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,timeout=1)
      main_window.after(1000,run_state)
      message_label.set("การทดสอบจะเริ่มใน \n 5 วินาที")
      main_state = 1

   elif main_state == 1:
      main_window.after(1000,run_state)
      message_label.set("การทดสอบจะเริ่มใน \n 4 วินาที")
      main_state = 2

   elif main_state == 2:
      main_window.after(1000,run_state)
      message_label.set("การทดสอบจะเริ่มใน \n 3 วินาที")
      main_state = 3
      
   elif main_state == 3:
      main_window.after(1000,run_state)
      message_label.set("การทดสอบจะเริ่มใน \n 2 วินาที")
      main_state = 4
      
   elif main_state == 4:
      message_label.set("การทดสอบจะเริ่มใน \n 1 วินาที")
      main_state = 5
      main_window.after(1000,run_state)
   elif main_state == 5:
      main_window.after(10,run_state)
      state_timer = 0
      main_state = 6
      
   elif main_state == 6:
      main_window.after(10,run_state)
      if len(test_param) > 0:
         current_color,current_text = test_param[0].strip().split(",")
         test_frame.config(background=current_color)
         test_label.config(background=current_color)
         timer_label.config(background=current_color)
         message_label.set(current_text)
         test_param.pop(0)
         start_time = current_millis()
         serial_port.flushInput()
         serial_port.flushOutput()
         main_state = 7
      else:
         main_state = 8
      
   elif main_state == 7:
      timer_display.set(str(current_millis()-start_time))
      if (current_millis()-start_time) >= timeout_ms:
         # record timeout
         main_state = 6
      if serial.inWaiting():
         pass
      #  process data
      main_window.after(10,run_state)
   elif main_state == 8:
      pass
   
# ======== home frame ======================================================================
config_params = read_yml(yml_config_path)
# logging.debug(config_params)
exp_selectable = os.listdir(experiments_path)
if len(exp_selectable) > 0:
   select_exp_var = customtkinter.StringVar(value=exp_selectable[0])
else:
   select_exp_var = customtkinter.StringVar()

config_frame = customtkinter.CTkFrame(home_frame,width=200,height=200,corner_radius=10,fg_color='#FFFFFF')
config_frame.place(relx=0.5, rely=0.5,anchor=tk.CENTER)

select_exp_label = customtkinter.CTkLabel(config_frame,text="เลือกการทดสอบ",font=main_thai_font,fg_color="#FFFFFF")
select_comport_label = customtkinter.CTkLabel(config_frame,text="เลือกคอมพอร์ต",font=main_thai_font,fg_color="#FFFFFF")
select_exp_option = customtkinter.CTkOptionMenu(master=config_frame, values=[], variable=select_exp_var,font=main_eng_font)
select_comport_option = customtkinter.CTkOptionMenu(master=config_frame, values=[], variable=select_comport_var,font=main_eng_font)

if len(exp_selectable) > 0:
   select_exp_option.configure(values=exp_selectable)

start_button = customtkinter.CTkButton(master=config_frame, text="เริ่มการทดสอบ",width=300,height=50, font=main_thai_font, command=start_button_pressed)

select_exp_label.grid(row=0,column=0,sticky=tk.W,padx=(50,10),pady=(50,0))
select_exp_option.grid(row=0,column=1,sticky=tk.W,padx=(0,50),pady=(50,0))
select_comport_label.grid(row=1,column=0,padx=(50,10),pady=20,sticky=tk.W)
select_comport_option.grid(row=1,column=1,sticky=tk.W,padx=(0,50),pady=20)
start_button.grid(row=2,column=0,columnspan=2,pady=(0,50))

#======== test frame ===============================================================
test_label = tk.Label(master=test_frame,textvariable = message_label,font=test_font,background='#FFFFFF')
timer_label = tk.Label(master=test_frame,textvariable = timer_display,font=timer_font,background='#FFFFFF')
test_label.place(relx=0.5, rely=0.5,anchor=tk.CENTER)
timer_label.place(relx=0.97, rely=0.97,anchor=tk.SE)
show_home_frame()

#============== add events =======================================================
main_window.bind('<Escape>', lambda e: main_window.destroy())

# =========== initial widgets =================
list_available_port = list_serial_ports()
if len(list_available_port)<=0:
   list_available_port = ['']
select_comport_option['values'] = list_available_port

main_window.mainloop()
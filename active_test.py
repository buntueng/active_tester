# Import the required libraries
import tkinter as tk
from tkinter import font,ttk
import customtkinter
from pathlib import Path
import os
import logging
import time
import sys
import serial
import glob
from tkinter import filedialog
from tkinter.filedialog import asksaveasfile
import csv

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
# def read_yml(file_path):
#     yml_params = None
#     if file_path.is_file():
#         with open(file_path,'r') as yml_file:
#             yml_params = yaml.load(yml_file, Loader=SafeLoader)
#     else:
#         logging.warning("file path is not here")
#     return yml_params

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
timer_font = customtkinter.CTkFont(family='TH Niramit AS', size=80)
test_font = font.Font(family='TH Niramit AS', size='120', weight='bold')

home_frame = tk.Frame(main_window)
test_frame = tk.Frame(main_window)
result_frame = tk.Frame(main_window)

message_label = tk.StringVar()
timer_display = tk.StringVar()
select_comport_var = tk.StringVar()
# ===========================================================================================
main_state = 0
state_timer = None
start_time = None
timeout_ms = 1000        # set timeout = 10 second
test_param = None
test_result = []
current_color = ""
current_text = ""

serial_port = None

def current_millis():
    return round(time.time() * 1000)

def change_background():
   test_frame.config(background='red')

def show_home_frame():
   home_frame.pack(fill='both', expand=1)
   home_frame.config(background='#FFFFFF')
   test_frame.pack_forget()
   result_frame.pack_forget()

def show_test_frame():
   test_frame.pack(fill='both', expand=1)
   test_frame.config(background='#FFFFFF')
   home_frame.pack_forget()
   result_frame.pack_forget()

def show_result_frame():
   result_frame.pack(fill='both', expand=1)
   result_frame.config(background='#FFFFFF')
   home_frame.pack_forget()
   test_frame.pack_forget()

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

def save_result_button_pressed():
   # file_path = filedialog.asksaveasfilename( filetypes=[("txt file", ".txt")], defaultextension=".txt")
   file_path = filedialog.asksaveasfilename( filetypes=[("csv file", ".csv")], defaultextension=".csv")
   if file_path:
      ## ============== write to text file ================
      # file_obj=open(file_path,'a+')
      # header_result = "ลำดับที่ \t เวลาที่ใช้ (ms) \t ผลการทดสอบ \t หมายเหตุ \n"
      # file_obj.write(header_result)
      # for row_id in result_treeview.get_children():
      #    temp_result = result_treeview.item(row_id)['values']
      #    record_result = str(temp_result[0]) + "\t" + str(temp_result[1]) + "\t" + str(temp_result[2]) + "\t" + str(temp_result[3]) + "\n"
      #    file_obj.write(record_result)
      # file_obj.close()
      with open(file_path, "a+", newline='') as obj_file:
        csvwriter = csv.writer(obj_file, delimiter=',')
        csv_title = ["ลำดับที่","เวลาที่ใช้ (ms)","ผลการทดสอบ","หมายเหตุ"]
        csvwriter.writerow(csv_title)
        for row_id in result_treeview.get_children():
            row = result_treeview.item(row_id)['values']
            csvwriter.writerow(row)

def retest_button_pressed():
   for i in result_treeview.get_children():
      result_treeview.delete(i)
   if serial_port.is_open:
      serial_port.close()
   test_label.configure(background="#FFFFFF")
   timer_label.configure(background="#FFFFFF")
   show_home_frame()

def run_state():
   global main_state
   global test_param
   global test_result
   global state_timer
   global start_time
   global timeout_ms
   global timer_display
   global serial_port
   global current_color
   global current_text
   if main_state == 0:
      serial_port = serial.Serial(port=select_comport_option.get(),baudrate=9600,bytesize=8,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,timeout=0.1)
      message_label.set("การทดสอบจะเริ่มใน \n 5 วินาที")
      main_state = 1
      main_window.after(1000,run_state)
   elif main_state == 1:
      message_label.set("การทดสอบจะเริ่มใน \n 4 วินาที")
      main_state = 2
      main_window.after(1000,run_state)
   elif main_state == 2:
      message_label.set("การทดสอบจะเริ่มใน \n 3 วินาที")
      main_state = 3
      main_window.after(1000,run_state)
   elif main_state == 3:
      message_label.set("การทดสอบจะเริ่มใน \n 2 วินาที")
      main_state = 4
      main_window.after(1000,run_state)
   elif main_state == 4:
      message_label.set("การทดสอบจะเริ่มใน \n 1 วินาที")
      main_state = 5
      main_window.after(1000,run_state)
   elif main_state == 5:
      state_timer = 0
      main_state = 6
      test_result = []
      main_window.after(10,run_state)
      
   elif main_state == 6:
      if len(test_param) > 0:
         # logging.debug(len(test_param[0]))
         if len(test_param[0]) > 3:
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
            test_param.pop(0)
      else:
         main_state = 8
      main_window.after(10,run_state)
      
   elif main_state == 7:
      timer_display.set(str(current_millis()-start_time))
      loop_time = 10
      if (current_millis()-start_time) >= timeout_ms:
         test_result.append([timeout_ms,"F","O"])
         main_state = 6
         loop_time = 1000
      if serial_port.inWaiting():
         current_input_data = serial_port.read(1)
         # logging.debug(current_input_data)
         if current_input_data == b'R' and current_color == "red":
            test_result.append([current_millis()-start_time,"T","N"])
         elif current_input_data == b'G' and current_color == "green":
            test_result.append([current_millis()-start_time,"T","N"])
         elif current_input_data == b'B' and current_color == "blue":
            test_result.append([current_millis()-start_time,"T","N"])
         else:
            test_result.append([current_millis()-start_time,"F","N"])
         main_state = 6
         loop_time = 1000
      main_window.after(loop_time,run_state)
   elif main_state == 8:
      show_result_frame()
      for index,each_result in enumerate(test_result):
         show_value = [str(index+1),each_result[0],'','']
         if each_result[1] == 'T':
            show_value[2] = "ถูก"
         else:
            show_value[2] = "ผิด"
         if each_result[2] == 'O':
            show_value[3] = "ไม่กดในเวลาที่กำหนด"
         show_value_tuple = tuple(show_value)
         result_treeview.insert('', 'end',values=show_value_tuple)
   
# ======== home frame ======================================================================
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

#====================== result frame ===============================================
main_result_frame = customtkinter.CTkFrame(master=result_frame,width=500,height=700,corner_radius=10,fg_color='#00FFFF')
main_result_frame.place(relx=0.5, rely=0.5,anchor=tk.CENTER)
title_result_label = tk.Label(master=main_result_frame,text="สรุปผลการทดสอบ",font=main_thai_font,background='#00FFFF')
save_result_button = customtkinter.CTkButton(master=main_result_frame, text="บันทึกผลการทดสอบ",width=300,height=50, font=main_thai_font, command=save_result_button_pressed)
retest_button = customtkinter.CTkButton(master=main_result_frame, text="กลับไปทดสอบอีกครั้ง",width=300,height=50, font=main_thai_font, command=retest_button_pressed)
exit_button = customtkinter.CTkButton(master=main_result_frame, text="ปิดโปรแกรม",width=300,height=50, font=main_thai_font, command=lambda: main_window.destroy())

style = ttk.Style(main_result_frame)
# set ttk theme to "clam" which support the fieldbackground option
style.theme_use("clam")
style.configure("Treeview.Heading", background="#FFFFFF",font=main_thai_font)
style.configure("Treeview", background="#FFFFFF",font=main_thai_font,rowheight=33)

result_treeview = ttk.Treeview(master=main_result_frame)
result_treeview['columns']=('Order_number','Reflect_time', 'TestResult', 'Comments')
result_treeview.column('#0', width=0, stretch=tk.NO)
result_treeview.column('Order_number', anchor=tk.CENTER, width=80)
result_treeview.column('Reflect_time', anchor=tk.CENTER, width=280)
result_treeview.column('TestResult', anchor=tk.CENTER, width=280)
result_treeview.column('Comments', anchor=tk.CENTER, width=280)

result_treeview.heading('#0', text='', anchor=tk.CENTER)
result_treeview.heading('Order_number', text='ลำดับ', anchor=tk.CENTER)
result_treeview.heading('Reflect_time', text='เวลาที่ใช้ในการกด (ms)', anchor=tk.CENTER)
result_treeview.heading('TestResult', text='ผลการทดสอบ (ถูกหรือผิด)', anchor=tk.CENTER)
result_treeview.heading('Comments', text='หมายเหตุ', anchor=tk.CENTER)

vertical_scrollbar = ttk.Scrollbar(master=main_result_frame, orient ="vertical", command = result_treeview.yview)
vertical_scrollbar.grid(row=1,column=3,sticky=tk.NS,padx=(0,50),pady=10)

title_result_label.grid(row=0,column=0,sticky=tk.W,padx=50,pady=(50,0))
result_treeview.grid(row=1,column=0,columnspan=2,sticky=tk.W,padx=(50,0),pady=10)
save_result_button.grid(row=2,column=1,sticky=tk.E,pady=(30,0))
retest_button.grid(row=3,column=1,sticky=tk.E,pady=20)
exit_button.grid(row=4,column=1,sticky=tk.E,pady=(0,50))

show_home_frame()
#============== add events =======================================================
main_window.bind('<Escape>', lambda e: main_window.destroy())

# =========== initial widgets =================
list_available_port = list_serial_ports()
# logging.debug(list_available_port)
if len(list_available_port)<=0:
   list_available_port = ['']
else:
   select_comport_option.configure(values= list_available_port)
   select_comport_option.set(list_available_port[0])

main_window.mainloop()
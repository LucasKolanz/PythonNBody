'''
This python file makes the main gui

TODO (overall):
	-(DONE)add cython to interate method
	-n body support
	-electromagnetic force support (or maybe just relativity effects)

TODO (this file):
	-(DONE)user input initial conditions should have no sun in the graph, only dots
	-(DONE)legend doesn't support updating graph in one run
	-(DONE)need to write out and reset data variables inbetween run button presses
	-show how much space your current saved data is taking up
	-give options to delete saved data by data file and (maybe) all at once
	-allow speed up and slow down of animation via scroll bar
	-change size of animation points as you zoom out/in  
	-(in prog)loading progress bar
	-(seems done but idk)check if data exists before makeing new data
'''

import tkinter as tk
from tkinter import ttk
import threading
# import signal
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
import os
import data as d
import numpy as np
import h5py
import time

class gui:

	# col_length = 
	# row_length = 

	"""docstring for gui"""
	def __init__(self):
		super(gui, self).__init__()

		#variables for graph
		self.data = []
		self.nombre = ''
		self.total_iter = -1
		self.radii = []

		#initialize threads used
		self.loading_thread = ''
		self.prog_bar_thread = ''
		self.loading_bool = False
		self.graph_thread = ''

		#initialize lists to hold widgets
		self.make_data_menu_items = []
		self.get_data_menu_items = []
		self.input_variable_items = []
		self.input_variable_names = []
		self.existing_data_items = []

		#initialize data storage variables
		self.input_variable_x_variables = []
		self.input_variable_o_variables = []

		###Begin main window making###
		if not os.path.isdir('data_dump'):
			os.mkdir('data_dump')

		self.window = tk.Tk()
		self.window.resizable(True, True)

		# self.w_width  = self.window.winfo_screenwidth()
		# self.w_height = self.window.winfo_screenheight()
		# self.window.geometry(f'{self.w_width}x{self.w_height}')

		#set up frames
		
		self.frm_graph = tk.Frame(master=self.window, bg="green", \
			relief=tk.FLAT, borderwidth=5)
		self.frm_graph.grid(row=0,column=1,columnspan=1,rowspan=1, \
			padx=0,pady=0,sticky='NSEW')
		self.make_graph_frame()

		self.frm_input = tk.Frame(master=self.window)
		self.frm_input.grid(row=0,column=0,columnspan=1,rowspan=1, \
			padx=0,pady=0,sticky='NSEW')
		self.make_input_frame()
		# print(self.fg_width+self.fi_width)
		wid = self.fg_width+self.fi_width
		self.frm_display_message = tk.Frame(master=self.window, \
			bg='red', relief=tk.RIDGE, borderwidth=5,height=50)

		self.frm_display_message.grid(row=1,column=0,columnspan=4, \
			rowspan=1,padx=0,pady=0,sticky='NSEW')
		self.make_message_frame()

		self.window.columnconfigure(1, weight=1)
		# self.window.columnconfigure(0, weight=1)
		self.window.rowconfigure(0, weight=1)
		self.window.rowconfigure(1, weight=1)
		
		self.frm_display_message.rowconfigure(0, weight=1)
		self.frm_display_message.rowconfigure(1, weight=1)
		self.frm_display_message.columnconfigure(1, weight=1)

		for i in range(4):
			self.frm_p_input.columnconfigure(i, weight=1)
		for i in range(4):
			self.frm_variable_input.columnconfigure(i, weight=1)
		for i in range(4):
			self.existing_data_frame.columnconfigure(i, weight=1)

		for i in range(4):
			self.frm_p_input.rowconfigure(i, weight=1)
		for i in range(4):
			self.frm_variable_input.rowconfigure(i, weight=1)
		for i in range(4):
			self.existing_data_frame.rowconfigure(i, weight=1)

		# self.frm_p_input.rowconfigure(0, weight=1)
		# self.frm_variable_input.rowconfigure(0, weight=1)
		# self.existing_data_frame.rowconfigure(0, weight=1)

		# self.frm_input.rowconfigure(0, weight=1)
		# self.frm_input.columnconfigure(0, weight=1)

		# self.frm_graph.rowconfigure(0, weight=1)
		# self.frm_graph.rowconfigure(1, weight=1)
		# self.frm_graph.columnconfigure(0, weight=1)
		# self.frm_graph.columnconfigure(1, weight=1)



		# self.frm_add_body = tk.Frame(master=self.window, height=self.height*0.05, \
		# 	bg='green', relief=tk.RIDGE, borderwidth=5)
		# self.frm_add_body.grid(row=1,column=1,columnspan=4,rowspan=4,padx=10,pady=10)



		
		


		

		# self.lbl_tot



		

	def make_message_frame(self):
		#set up message frame
		master_ = self.frm_display_message
		#make display message stuff
		self.lbl_message_display = tk.Label(master=master_, text='Messages: ')
		# self.lbl_message_display.pack(side=tk.LEFT,fill=tk.Y)
		self.lbl_message_display.grid(row=0,column=0,padx=5,pady=5, sticky='NS')

		self.lbl_message = tk.StringVar()
		self.lbl_message.set('')
		# self.lbl_message.set('fa;sdfj;adasdjfaskjdfh;aksdjf;laksdjf;alksdjf;alksdjf;alksdjf;alksdjf;alksdjf;aslkdjf;alkdjf;alksdjf;alksdjf;askldfj;alksdjf;alskdfj;adkjfkasjfas;dkfa;sldkfja;sdkjfa;sdkljfa;sldkfja;sldkfja;lsdkfj;aslkdfja;sldkfja;lskdfja;kdlfj;asdkljfdkjkfsj;alskdjf;alksjdf;aksjd;faksdjf;alksdjf;alkdsjf;asdkjf;akdsfj;aslkdfja;sldkfja;lsdkjfkfa;dkfa;dkfa;dkj')
		self.lbl_message_display_message = tk.Label(master=master_, \
			textvariable=self.lbl_message)
		self.lbl_message_display_message.grid(row=0,column=1,columnspan=1,padx=5, \
			pady=5, sticky='NSEW')
		# self.lbl_message_display_message.pack(fill=tk.Y)
		

	def make_graph_frame(self):
		#set up graph's frame
		master_ = self.frm_graph
		scale = 1.35
		dpi_ = 80
		self.fig = plt.Figure()
		# self.fig = plt.Figure(figsize=(7*scale,5*scale),dpi=dpi_)
		self.graph_canvas = FigureCanvasTkAgg(self.fig, master=master_)
		self.graph_canvas.get_tk_widget().pack(fill=tk.BOTH)

		# self.get_data_text = tk.StringVar()
		# self.get_data_text.set('Get Saved Data')
		# self.btn_get_data = tk.Button(master=master_, textvariable=self.get_data_text)
		# self.btn_get_data.bind("<Button-1>", self.handle_get_data_click)
		# self.btn_get_data.pack(padx=10, pady=10)

		
		self.fg_width = self.frm_graph.winfo_width()
		self.fg_height = self.frm_graph.winfo_height()

	def make_input_frame(self):
		self.frm_p_input = tk.Frame(master=self.frm_input, \
			bg="yellow", relief=tk.RIDGE, borderwidth=5)
		self.frm_p_input.grid(row=0,column=0,columnspan=1,rowspan=1,padx=0, \
			pady=0,sticky='NSEW')
		
		self.frm_variable_input = tk.Frame(master=self.frm_input, \
			bg='green', relief=tk.RIDGE, borderwidth=5)
		self.frm_variable_input.grid(row=1,column=0,columnspan=1,rowspan=1, \
			padx=0,pady=0,sticky='NSEW')

		self.existing_data_frame = tk.Frame(master=self.frm_input, \
			bg='orange', relief=tk.RIDGE, borderwidth=5)
		self.existing_data_frame.grid(row=2,column=0,columnspan=1,rowspan=1, \
			padx=0,pady=0,sticky='NSEW')

		self.frm_run_sim = tk.Frame(master=self.frm_input, \
			bg='blue', relief=tk.RIDGE, borderwidth=5)
		self.frm_run_sim.grid(row=3,column=0,columnspan=1,rowspan=1, \
			padx=0,pady=0,sticky='NSEW')

		self.make_p_input_frame()
		self.make_var_input_frame()
		self.make_get_existing_data_frame()
		self.make_run_sim_frame()

		self.fi_width = self.frm_input.winfo_width()
		self.fi_height = self.frm_input.winfo_height()

	def make_run_sim_frame(self):
		master_ = self.frm_run_sim
		self.btn_run = tk.Button(master=master_, text='Run Sim')
		self.btn_run.bind("<Button-1>", self.handle_run_click)
		self.btn_run.grid(row=0,column=0,columnspan=1,rowspan=1, \
			padx=0,pady=0,sticky='NSEW')
		self.window.bind("<Return>", self.handle_run_click)

		self.status_text = tk.StringVar()
		self.status_text.set('Status: Idle')
		self.lbl_status = tk.Label(master=master_,textvariable=self.status_text)
		self.lbl_status.grid(row=0,column=2,columnspan=1,rowspan=1, \
			padx=0,pady=0,sticky='NSEW')
		
		# self.prog_bar = ttk.Progressbar(master=master_, orient=tk.HORIZONTAL, length = 100, \
		# 	mode='determinate')

		self.btn_exit = tk.Button(master=master_, text='Exit Sim')
		self.btn_exit.bind("<Button-1>", self.handle_exit_click)
		self.btn_exit.grid(row=0,column=3,columnspan=1,rowspan=1, \
			padx=0,pady=0,sticky='NSEW')


	def make_p_input_frame(self):
		#set up input frame 
		master_ = self.frm_p_input

		#make widgets to get new data
		self.approx = ["Central Force","Many-body"]
		self.lbl_approx_input = tk.Label(master=master_, text="Approximation: ")
		self.lbl_approx_input.grid(row=0,column=0,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.make_data_menu_items.append(self.lbl_approx_input)
		self.approx_option = tk.StringVar(master=master_)
		self.approx_option.set(self.approx[0])
		self.ent_approx_input = tk.OptionMenu(master_,self.approx_option,*self.approx)
		self.ent_approx_input.grid(row=0,column=1,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.make_data_menu_items.append(self.ent_approx_input)

		self.forces = ["Gravity","Electromagnetic","Both"]
		self.lbl_force_input = tk.Label(master=master_, text="Force: ")
		self.lbl_force_input.grid(row=0,column=2,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.make_data_menu_items.append(self.lbl_force_input)
		self.force_option = tk.StringVar(master=master_)
		self.force_option.set(self.forces[0])
		self.ent_force_input = tk.OptionMenu(master_,self.force_option,*self.forces)
		self.ent_force_input.grid(row=0,column=3,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.make_data_menu_items.append(self.ent_force_input)

		self.lbl_num_body_input = tk.Label(master=master_, text='Bodies: ')
		self.lbl_num_body_input.grid(row=1,column=0,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.make_data_menu_items.append(self.lbl_num_body_input)
		self.num_bodies = tk.Entry(master=master_)
		self.num_bodies.grid(row=1,column=1,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.make_data_menu_items.append(self.num_bodies)

		self.lbl_dt_input = tk.Label(master=master_, text='dt (days): ')
		self.lbl_dt_input.grid(row=2,column=0,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.make_data_menu_items.append(self.lbl_dt_input)
		self.dt = tk.Entry(master=master_)
		self.dt.grid(row=2,column=1,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.make_data_menu_items.append(self.dt)

		self.lbl_tot_time_input = tk.Label(master=master_, text='Total Time (days): ')
		self.lbl_tot_time_input.grid(row=3,column=0,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.make_data_menu_items.append(self.lbl_tot_time_input)
		self.tot_time = tk.Entry(master=master_)
		self.tot_time.grid(row=3,column=1,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")

		self.relativity_bool = tk.IntVar()
		self.relativity_checkbx = tk.Checkbutton(master=master_,text='',variable=self.relativity_bool, \
			command=self.relativity_checkbx_ck)
		self.relativity_checkbx.grid(row=1,column=2,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		self.relativity_text = tk.Label(master=master_,text="Relativity")
		self.relativity_text.grid(row=1,column=3,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")

		self.planet_bool = tk.IntVar()
		self.planet_checkbx = tk.Checkbutton(master=master_,text='',variable=self.planet_bool, \
			command=self.planet_checkbx_ck)
		self.planet_checkbx.grid(row=2,column=2,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		self.planet_text = tk.Label(master=master_,text="Use Planet IC")
		self.planet_text.grid(row=2,column=3,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		
	def make_var_input_frame(self):
		master_ = self.frm_variable_input
		#If user wants to input initial conditions of every body
		self.lbl_xi = tk.Label(master=master_, text='Xi (au): ')
		self.lbl_xi.grid(row=0,column=0,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.input_variable_items.append(self.lbl_xi)
		self.xi = tk.Entry(master=master_)
		self.xi.grid(row=0,column=1,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.input_variable_items.append(self.xi)

		self.lbl_yi = tk.Label(master=master_, text='Yi (au): ')
		self.lbl_yi.grid(row=1,column=0,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.input_variable_items.append(self.lbl_yi)
		self.yi = tk.Entry(master=master_)
		self.yi.grid(row=1,column=1,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.input_variable_items.append(self.yi)

		self.lbl_zi = tk.Label(master=master_, text='Zi (au): ')
		self.lbl_zi.grid(row=2,column=0,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.input_variable_items.append(self.lbl_zi)
		self.zi = tk.Entry(master=master_)
		self.zi.grid(row=2,column=1,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.input_variable_items.append(self.zi)

		self.lbl_vxi = tk.Label(master=master_, text='Vxi (au/day): ')
		self.lbl_vxi.grid(row=0,column=2,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.input_variable_items.append(self.lbl_vxi)
		self.vxi = tk.Entry(master=master_)
		self.vxi.grid(row=0,column=3,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.input_variable_items.append(self.vxi)

		self.lbl_vyi = tk.Label(master=master_, text='Vyi: (au/day)')
		self.lbl_vyi.grid(row=1,column=2,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.input_variable_items.append(self.lbl_vyi)
		self.vyi = tk.Entry(master=master_)
		self.vyi.grid(row=1,column=3,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.input_variable_items.append(self.vyi)

		self.lbl_vzi = tk.Label(master=master_, text='Vzi: (au/day)')
		self.lbl_vzi.grid(row=2,column=2,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.input_variable_items.append(self.lbl_vzi)
		self.vzi = tk.Entry(master=master_)
		self.vzi.grid(row=2,column=3,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.input_variable_items.append(self.vzi)

		self.lbl_body_mass = tk.Label(master=master_, text='Body Mass (Msol): ')
		self.lbl_body_mass.grid(row=3,column=0,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.input_variable_items.append(self.lbl_body_mass)
		self.body_mass = tk.Entry(master=master_)
		self.body_mass.grid(row=3,column=1,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.input_variable_items.append(self.body_mass)

		self.lbl_body_name = tk.Label(master=master_, text='Body Label (op): ')
		self.lbl_body_name.grid(row=3,column=2,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.input_variable_items.append(self.lbl_body_name)
		self.body_name = tk.Entry(master=master_)
		self.body_name.grid(row=3,column=3,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.input_variable_items.append(self.body_name)

		self.lbl_body_radius = tk.Label(master=master_, text='Body radius (au) (op): ')
		self.lbl_body_radius.grid(row=4,column=0,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.input_variable_items.append(self.lbl_body_radius)
		self.body_radius = tk.Entry(master=master_)
		self.body_radius.grid(row=4,column=1,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.input_variable_items.append(self.body_radius)

		#make add data button (in different frame)
		self.btn_add_body = tk.Button(master=master_, text='Add Body')
		self.btn_add_body.bind("<Button-1>", self.handle_add_body_click)
		self.btn_add_body.grid(row=4,column=2,columnspan=2,rowspan=1,padx=1,pady=7, \
			sticky='NSEW')

		

	def make_get_existing_data_frame(self):
		master_ = self.existing_data_frame
		#make widgets to get existing data
		self.exist_data_bool = tk.IntVar()
		self.existing_data_checkbx = tk.Checkbutton(master=master_,text='Use existing data', \
			variable=self.exist_data_bool, command=self.existing_data_checkbx_ck)
		self.existing_data_checkbx.grid(row=0,column=0,columnspan=4,rowspan=1, \
			padx=1,pady=7,sticky='E')


		self.lbl_get_data_prompt = tk.Label(master=master_, text='Please select an existing data set')
		self.lbl_get_data_prompt.grid(row=1,column=0,columnspan=4,rowspan=1, \
			padx=1,pady=7,sticky='NSEW')
		# self.get_data_menu_items.append(self.lbl_get_data_prompt)

		self.existing_data = self.get_existing_data()
		self.data_option = tk.StringVar(master=master_)
		if len(self.existing_data) == 0:
			self.existing_data.append('No Previously Saved Data')

		self.data_option.set(self.existing_data[0])

		self.ent_data_input = tk.OptionMenu(master_,self.data_option,*self.existing_data)
		self.ent_data_input.grid(row=2,column=0,columnspan=4,rowspan=1, \
			padx=1,pady=7,sticky='NSEW')

		self.able(master_,'disable',["Checkbutton"])
		# self.get_data_menu_items.append(self.ent_data_input)

	def existing_data_checkbx_ck(self):
		mo = 'disabled'
		mo_o = 'normal'
		if not self.exist_data_bool.get():
			mo_o = 'disabled'
			mo = 'normal'

		self.able(self.frm_p_input,mo)
		self.able(self.frm_variable_input,mo)

		self.able(self.existing_data_frame,mo_o,["Checkbutton"])

	def relativity_checkbx_ck(self):
		return 

	def planet_checkbx_ck(self):
		mo = 'disabled'
		if not self.planet_bool.get():
			mo = 'normal'
		self.able(self.frm_variable_input,mo)
		self.able(self.existing_data_frame,mo)

	def get_existing_data(self):
		return_me = []
		for dat in os.listdir('./data_dump/'):
			try:
				f = h5py.File('./data_dump/{}'.format(dat))
				return_me.append('Approx={}, Force={}, Bodies={}, dt={}, Total Time={}'.format \
					(f.attrs['approximation'],f.attrs['force'],f.attrs['bodies'], \
						f.attrs['dt'],f.attrs['total_time']) \
				)
			except:
				os.system('rm ./data_dump/{}'.format(dat))
		return return_me

	def get_data_num(self,bodies,force,approx,delta_t,total_t):
		for dat in os.listdir('./data_dump/'):
			f = h5py.File('./data_dump/{}'.format(dat))
			if f.attrs['approximation'] == approx and f.attrs['force'] == force:
				if f.attrs['bodies'] == int(bodies) and f.attrs['dt'] == float(delta_t) and f.attrs['total_time'] == float(total_t):
					return dat.strip('data_').strip('.hdf5')	
		return -1		
		

	def get_data(self,data_num,max_frames, dim=3, option=0):

		data_name = 'data_' + str(data_num) + '.hdf5'
		try:
			f = h5py.File('data_dump/{}'.format(data_name), 'r')
		except:
			return [-1,-1,-1,-1]
		# os.system('h5dump -H data_dump/data_{}.hdf5'.format(data_num))
		total_iter = f.attrs['iterations']
		bodies = f.attrs['bodies']
		radii = f.attrs['radii']
		names = []
		if option == 0:
			names = f.attrs['names']

		if max_frames < total_iter:
			skip = int(np.ceil(total_iter/max_frames))
			frames = max_frames
		else:
			skip = 1
			frames = total_iter

		return_me = np.empty((bodies,dim, frames))#[[],[],[]]
		# f = h5py.File(data_name, 'r')
		# print(f['position_data'][:10,:,:])
		ind = 0
		for j in range(0,total_iter,skip):
			return_me[:, :, ind] = f['position_data'][j,:,:]
			ind += 1

		while ind < frames:
			return_me[:, :, ind] = f['position_data'][j,:,:]
			ind += 1
		return return_me, names, total_iter, radii

	def get_bodies(self):
		f = h5py.File(d.data_name, 'r')
		return f.attrs['bodies']

	def radii_to_markersize(self,radii):
		return radii*62775.3611135

	def update_lines(self, num, dataLines, lines):
		for line, data in zip(lines, dataLines):
			# NOTE: there is no .set_data() for 3 dim data...
			line.set_data(data[0:2, :num])
			line.set_3d_properties(data[2, :num])
		return lines

	def run_prog_bar(self,const):
		t0 = time.time()
		self.prog_bar.pack(padx=10,pady=10)
		self.prog_bar.start()
		self.loading_bool = True
		# self.loading_bool = True
		while self.prog_bar['value'] < 100:
			# bar_len = 100-np.floor(const/(time.time()-t0))
			# print('IN run_prog_bar: {}'.format(self.loading_bool))
			bar_len = np.floor(time.time()-t0) * 10
			if not self.loading_bool:
				bar_len = 100
			elif bar_len > 99:
				bar_len = 99
			# if bar_len > 99:
			# 	bar_len == 99
			self.prog_bar['value'] = bar_len
			# print(self.prog_bar['value'])
			# bar['value'] = bar_len
			self.window.update_idletasks()
			time.sleep(0.1)
		self.prog_bar.stop()
		self.prog_bar.pack_forget()

	# def start_progress(self,bar,bodies,iterations):
	# 	# self.prog_bar.start()
	# 	bar['value'] = 0
	# 	constant = ((bodies*iterations)/10000)**2
	# 	self.run_prog_bar(bar,constant)

	def make_graph(self,argumentsv):
		approx = ['central','many-body']
		forces = ['grav']#,'em']
		# Attaching 3D axis to the figure
		requested_num_planets = np.nan
		requested_approx = -1
		requested_force = -1
		for i in argumentsv:
			if 'num_planets=' in i:
				try:
					requested_num_planets = int(i.strip('num_planets='))
				except:
					print("error: in setting num_planets. Could not cast to int")
					return -1
			elif 'approx=' in i:
				try:
					requested_approx = i.strip('approx=') 
				except:
					print("error: in setting approx.")
					return -1
			elif 'force=' in i:
				try:
					requested_force = i.strip('force=') 
				except:
					print("error: in setting force.")
					return -1
			elif 'dt=' in i:
				try:
					requested_dt = i.strip('dt=')
				except:
					print("error: in setting dt")
			elif 'total_time=' in i:
				try:
					requested_tt = i.strip('total_time=')
				except:
					print("error: in setting total time")


		if np.isnan(requested_num_planets):
			requested_num_planets = 2
		if requested_force == -1:
			requested_force = 'grav'
		if requested_approx == -1:
			requested_approx = 'central'

		if isinstance(requested_num_planets, int):
			if requested_num_planets < 0 or requested_num_planets > 9:
				print('Requested number of planets not supported. Please set a value from 1 to {}.'.format(d.max_solar_system_bodies))
				return -1
		elif isinstance(requested_num_planets, list):
			if requested_approx == 'central' or requested_approx == 'many-body':
				if len(requested_num_planets) > d.max_solar_system_bodies:
					print("Requested number of bodies ({}) not supported. Please enter a number from 1 to {} or a list of indices to include with maximum length of {}".format(requested_num_planets,d.max_solar_system_bodies,d.max_solar_system_bodies))
					return -1

		if requested_approx not in approx:
			print('Requested approx "{}" is not supported. Supported approx are:'.foramt(requested_approx))
			print(approx)
			return -1

		if requested_force not in forces:
			print('Requested force "{}" is not supported. Supported forces are:'.format(requested_force))
			print(forces)
			return -1

		#def get_data_num(bodies,force,approx,delta_t,total_t):
		if self.loading_thread != '':
			while self.loading_thread.is_alive():
				time.sleep(0.1)
			self.update_menu(self.get_existing_data(),self.ent_data_input,self.data_option)
		# else:

		dat_num = self.get_data_num(requested_num_planets,requested_force,requested_approx,requested_dt,requested_tt)
		# data,nombre,total_iter,radii = get_data(requested_force,requested_approx,requested_num_planets,max_frames=50000,dim=3)
		# print(dat_num)
		data,nombre,total_iter,radii = self.get_data(data_num=dat_num,max_frames=50000,dim=3)
		# data = get_data(total_iter,50000,bodies,3)
		# self.data = data_
		# self.nombre = nombre_
		# self.total_iter = total_iter_
		# self.radii = radii_
		# signal.signal(signal.SIGUSR1, self.recieve_signal)
		# print('in make_graph: {}'.format(data.shape))
		# print(data[:,:,:10])
		# print(data.sum())
		try:
			self.ax.clear()
			# self.fig.legend([])
			self.ax.get_legend().remove()
			# self.fig.legend().remove()
		except:
			self.ax = p3.Axes3D(self.fig)
		# data = get_data()
		# Creating "iterations" line objects.
		# NOTE: Can't pass empty arrays into 3d version of plot()
		lines = []#np.zeros((len(data)),dtype=Line3D)
		marker_sizes = np.full((requested_num_planets),10)

		# marker_sizes = radii_to_markersize(radii)
		# marker_sizes[0] = 40
		# marker_sizes[1:5] *= 10/marker_sizes[3]

		colors = ['y','#ffa07a','#fff56a','b','r','#ff4500','#7a7733','#acf0f9','#109ae1']
		if self.planet_data_or_not_text.get() == 'Input Body Variables':
			marker_sizes[0] = 40
			lines.append(self.ax.plot(data[0][0, 0:1], data[0][1, 0:1], data[0][2, 0:1],lw = 3,marker='*',markersize=marker_sizes[0],color=colors[0],markevery=[-1])[0])
			lines.extend([self.ax.plot(dat[0, 0:1], dat[1, 0:1], dat[2, 0:1],lw = 0.9, marker='.',markersize=marker_sizes[i+1],color=colors[i+1],markevery=[-1])[0] for i,dat in enumerate(data[1:])])
		else:
			lines.extend([self.ax.plot(dat[0, 0:1], dat[1, 0:1], dat[2, 0:1],lw = 0.9, marker='.',markersize=marker_sizes[i],color=colors[i],markevery=[-1])[0] for i,dat in enumerate(data)])
		# Setting the axes properties
		lim = 3
		self.ax.set_xlim3d([-lim, lim])
		self.ax.set_xlabel('X')

		self.ax.set_ylim3d([-lim, lim])
		self.ax.set_ylabel('Y')

		self.ax.set_zlim3d([-lim, lim])
		self.ax.set_zlabel('Z')

		# ax.set_title('3D Test')
		self.ax.legend(nombre)


		# Creating the Animation object

		self.line_ani = animation.FuncAnimation(self.fig, self.update_lines, total_iter, fargs=(data, lines),
											blit=False, interval=1)

		# try: 
		# 	graph_canvas.get_tk_widget().pack_forget()
		# except: 
		# 	pass
		self.loading_bool = False

		self.fig.canvas.draw()
		# graph_canvas = FigureCanvasTkAgg(fig, master=frm_graph)
		self.graph_canvas.get_tk_widget().pack(side = tk.LEFT)
		# time.sleep(5)
		self.status_text.set('Status: Idle')

		# results = [data,nombre,total_iter,radii]


	def handle_get_data_click(self,event):
		self.reset_message()
		if self.get_data_text.get() == 'Make New Data':
			self.get_data_text.set('Get Saved Data')
			# if get_data_menu_bool:
			self.unpack_widgets(self.get_data_menu_items)
				# get_data_menu_bool = False
			# if not make_data_menu_bool:
			self.grid_widgets(self.make_data_menu_items)
			if self.planet_data_or_not_text.get() == 'Use Solar System Variables':
				self.grid_widgets(self.input_variable_items)
			self.btn_add_body.pack()
				# make_data_menu_bool = True
		else:
			self.get_data_text.set('Make New Data')

			# if make_data_menu_bool:
			self.ungrid_widgets(self.make_data_menu_items)
			self.ungrid_widgets(self.input_variable_items)
			self.btn_add_body.pack_forget()
				# make_data_menu_bool = False
			# if not get_data_menu_bool:	
			self.pack_widgets(self.get_data_menu_items)
				# get_data_menu_bool = True
		self.window.update_idletasks()

	def handle_exit_click(self,event):
		# if not self.data_wrote:
		# 	self.sim.write_datas()
		self.window.destroy()

	def handle_run_click(self,event):
		self.reset_message()
		# lbl_status_value.delete("1.0",tk.END)
		# window.update()
		
		self.status_text.set('Status: Processing')
		# self.prog_bar.pack(padx=10,pady=10)
		# self.prog_bar.start()
		
		self.window.update_idletasks()
		# self.traitement()
		# time.sleep(1)

		self.input_variable_x_variables = np.array(self.input_variable_x_variables)
		self.input_variable_o_variables = np.array(self.input_variable_o_variables)

		if self.get_data_text.get() == 'Get Saved Data':
			use_dt = float(self.dt.get())
			use_tt = float(self.tot_time.get())
			approx = self.approx_option.get()
			if self.approx_option.get() == 'Central Force':
				app = True
			else:
				app = False
			if approx == "Central Force":
				approx = 'central'
			elif approx == 'Many-body':
				approx = 'many-body'
			force = self.force_option.get()
			if force == 'Gravity':
				force = 'grav'
			elif force == 'Electromagnetic':
				force = 'em'
			self.data_wrote = False
			if self.planet_data_or_not_text.get() != 'Input Body Variables':
				# approx = approx_option.get()
				# force = force_option.get()
				bodies = len(self.input_variable_x_variables)
				arguments = dict()
				arguments['total_time_'] = use_tt
				arguments['central_force_'] = app
				arguments['init_dt_'] = use_dt
				arguments['names_'] = self.input_variable_names
				arguments['force_'] = force
				arguments['initial_cond_'] = self.input_variable_x_variables
				arguments['other_data_'] = self.input_variable_o_variables
				arguments['bodies_'] = bodies
				arguments['mode_'] = 'custom'

				self.prog_bar_thread = threading.Thread(group=None,target=self.run_prog_bar, \
					name=None,args=(10,), daemon=True)
				self.prog_bar_thread.start()
				self.loading_thread = threading.Thread(group=None,target=d.numerics, \
					name=None,args=(arguments,), daemon=True)
				# self.run_prog_bar(10)
				self.loading_thread.start()
				# self.sim = d.numerics(arguments)
				# self.sim.make_data(0)
			else:
				bodies = int(self.num_bodies.get())
				arguments = dict()
				arguments['total_time_'] = use_tt
				arguments['central_force_'] = app
				arguments['init_dt_'] = use_dt
				arguments['names_'] = []
				arguments['force_'] = force
				arguments['initial_cond_'] = self.input_variable_x_variables
				arguments['other_data_'] = self.input_variable_o_variables
				arguments['bodies_'] = bodies
				arguments['mode_'] = 'planetary'
				self.prog_bar_thread = threading.Thread(group=None,target=self.run_prog_bar, \
					name=None,args=(10,), daemon=True)
				self.prog_bar_thread.start()
				# print('PROG START')
				self.loading_thread = threading.Thread(group=None,target=d.numerics, \
					name=None,args=(arguments,), daemon=True)
				# self.run_prog_bar(10)
				self.loading_thread.start()
				
		else:
			opts = self.data_option.get().split(',')
			approx = opts[0].split('=')[1]
			force = opts[1].split('=')[1]
			bodies = int(opts[2].split('=')[1])
			use_dt = float(opts[3].split('=')[1])
			use_tt = float(opts[4].split('=')[1])
			if approx == "Central Force":
				approx = 'central'
			elif approx == 'Many-body':
				approx = 'many-body'
			force = self.force_option.get()
			if force == 'Gravity':
				force = 'grav'
			elif force == 'Electromagnetic':
				force = 'em'

			# d.make_data(bodies=bodies,force=force,approx=approx,dt=use_dt,total_time=use_tt, \
			# 	data=input_variable_x_variables, other_data=input_variable_o_variables)
		
		inputs = ['approx={}'.format(approx),'force={}'.format(force), \
			'num_planets={}'.format(bodies),'dt={}'.format(use_dt), \
			'total_time={}'.format(use_tt)]

		self.make_graph(inputs)


	def handle_add_body_click(self,event):
		error_msg = ''
		try:
			init_x = float(self.xi.get())
		except:
			error_msg += 'Error: Please enter an initial x position for this body\n'
		try:	
			init_y = float(self.yi.get())
		except:
			error_msg += 'Error: Please enter an initial y position for this body\n'
		try:
			init_z = float(self.zi.get())
		except:
			error_msg += 'Error: Please enter an initial z position for this body\n'
		try:
			init_vx = float(self.vxi.get())
		except:
			error_msg += 'Error: Please enter an initial x velocity for this body\n'
		try:
			init_vy = float(self.vyi.get())
		except:
			error_msg += 'Error: Please enter an initial y velocity for this body\n'
		try:
			init_vz = float(self.vzi.get())
		except:
			error_msg += 'Error: Please enter an initial z velocity for this body\n'
		try:
			init_body_mass = float(self.body_mass.get()) 
		except:
			error_msg += 'Error: Please enter a mass for this body\n'
		try:
			init_body_name = string(self.body_name.get())
		except:
			init_body_name = ''
		try:
			init_body_radius = float(self.body_radius.get())
		except:
			init_body_radius = -1.0


		if error_msg == '':
			if init_body_name != '':
				self.input_variable_names.append(init_body_name)
			self.xi.delete(0, 'end')
			self.yi.delete(0, 'end')
			self.zi.delete(0, 'end')
			self.vxi.delete(0, 'end')
			self.vyi.delete(0, 'end')
			self.vzi.delete(0, 'end')
			self.body_mass.delete(0, 'end')
			self.body_radius.delete(0, 'end')
			self.body_name.delete(0, 'end')

			self.input_variable_x_variables.append([[init_x,init_y,init_z],[init_vx,init_vy,init_vz]])
			self.input_variable_o_variables.append([init_body_mass,init_body_radius])
		else:
			error_msg = error_msg[:-1]
			self.lbl_message.set(error_msg)
			self.lbl_message_display_message.pack(fill="none", expand=True)

	def handle_body_variable_click(self,event):
		self.reset_message()
		if self.planet_data_or_not_text.get() == 'Input Body Variables':
			self.grid_widgets(self.input_variable_items)
			self.planet_data_or_not_text.set('Use Solar System Variables')
			self.btn_add_body.pack(padx=10,pady=10)
		else:
			self.ungrid_widgets(self.input_variable_items)
			self.planet_data_or_not_text.set('Input Body Variables')
			self.btn_add_body.pack_forget()

	def grid_widgets(self,widget_list,max_col_len=6):
		curr_row_len = 0
		curr_column_len = 0
		for ind,val in enumerate(widget_list):
			if curr_column_len >= max_col_len:
				curr_column_len = 0
				curr_row_len += 1

			if ind % 2 == 0:
				left_pad = 10
				right_pad = 0
				side = 'E'
			else:
				left_pad = 0
				right_pad = 10
				side = 'W'

			if ind == len(widget_list)-1:
				val.grid(row=curr_row_len,column=curr_column_len,sticky=side, \
					padx=(left_pad,right_pad),pady=3,columnspan=2)
			else:
				val.grid(row=curr_row_len,column=curr_column_len,sticky=side, \
					padx=(left_pad,right_pad),pady=3)

			curr_column_len += 1

	def ungrid_widgets(self,widget_list):
		for ind,val in enumerate(widget_list):
			val.grid_forget()

	def pack_widgets(self,widget_list):
		for ind,val in enumerate(widget_list): 
			val.pack(fill="none", expand=True)

	def unpack_widgets(self,widget_list):
		for ind,val in enumerate(widget_list): 
			val.pack_forget()

	def reset_message(self):
		self.lbl_message_display_message.pack_forget()

	def update_menu(self,new_menu,update_me,update_option):
		menu = update_me["menu"]
		menu.delete(0, "end")
		for string in new_menu:
			menu.add_command(label=string, 
							 command=lambda value=string: update_option.set(value))
		if len(new_menu) > 0:
			update_option.set(new_menu[0])

	#mode = 'normal' -> enable children
	#mode = 'disable' -> disable children
	def able(self,frame,mode='normal',exceptions=[""]):
		for child in frame.winfo_children():
			wtype = child.winfo_class()
			if wtype not in exceptions:
				child.configure(state=mode)
			elif wtype == 'Frame':
				self.able(child,mode=mode)


def main():
	GUI = gui()
	GUI.window.mainloop()


if __name__ == '__main__':
	main()
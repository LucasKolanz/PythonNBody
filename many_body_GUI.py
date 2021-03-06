'''
By Lucas Kolanz

This python file makes the main gui for the n-body solver.
It also checks input and runs all other necessary programs

TODO (overall):
	-(DONE)add cython to interate method
	-(DONE)n body support
	-electromagnetic force support (or maybe just relativity effects)

TODO (this file):
	-(DONE)user input initial conditions should have no sun in the graph, only dots
	-(DONE)legend doesn't support updating graph in one run
	-(DONE)need to write out and reset data variables inbetween run button presses
	-(DONE)redesign GUI [make it easier to see all options and make GUI expanding]
	-(DONE)show how much space your current saved data is taking up
	-(DONE)give options to delete saved data by data file and (maybe) all at once
	-add gui to control different preset initial conditions
	-allow speed up and slow down of animation via scroll bar
	-change size of animation points as you zoom out/in  
	-(in prog)loading progress bar
	-(This happens sometimes???)check if data exists before makeing new data
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


#given a string in the form of a python (or numpy) 1D list
#	this function returns this as a list
def list_from_string(obj):
	if isinstance(obj,list):
		return obj

	separators = ['+',':',', ',',',' ']
	separated_obj = []



	if obj[0] == '[' and obj [-1] == ']':
		obj = obj.strip(']')
		obj = obj.strip('[')
		for i in separators:
			if isinstance(obj,list):
				for j in obj:
					if len(j.split(i)) > 1:
						separated_obj.extend(j.split(i))
			elif isinstance(obj,str):
				if len(obj.split(i)) > 1:
					separated_obj.extend(obj.split(i))
					obj = separated_obj

		
		return [int(i) for i in obj]
	else:
		try:
			return list(range(int(obj)))
		except:
			print("ERROR in list_from_string(): arg obj={}, type(obj)={}".format(obj,type(obj)))


	# if obj[0] == '[' and obj [-1] == ']':
	# 	if ',' not in obj and ':' not in obj:
	# 		return [int(i) for i in obj[1:-1].split(' ')]
	# 	already_got = False
	# 	return_me = []
	# 	for i,o in enumerate(obj):
	# 		if o == ':':
	# 			return_me.extend(list(range(int(obj[i-1]),int(obj[i+1])+1)))
	# 			if int(obj[i+2] == ']'):
	# 				already_got = True
	# 		elif o == ',' or (not already_got and o == ']'):
	# 			return_me.append(int(obj[i-1]))

	# 	if len(return_me) == 0:
	# 		return -1
	# 	else:
	# 		return return_me
	# try:
	# 	return list(range(int(obj)))
	# except:
	# 	print("ERROR in list_from_string(): arg obj={}, type(obj)={}".format(obj,type(obj)))


#given the data_num of a certain dataset and max amount of frames
#	allowed in the simultion, this function returns the data,
#	the names of the bodiues, the number of iterations in the sim,
# 	and the radii of the bodies
def get_data(data_num,max_frames, dim=3, option=0):
	data_name = 'data_' + str(data_num) + '.hdf5'
	try:
		f = h5py.File('data_dump/usr_data/{}'.format(data_name), 'r')
	except:
		return [-1,-1,-1,-1]
	# os.system('h5dump -H data_dump/data_{}.hdf5'.format(data_num))
	total_iter = f.attrs['iterations']
	bodies = f.attrs['bodies']
	# print(bodies)
	# bodies_list = list_from_string() 
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

	return_me = np.empty((len(bodies),dim, frames))#[[],[],[]]
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


#method returns the total size or specific file size
#	of user made data
#option == 0 -> return total size
#option == 1 -> return list of data and sizes
def get_size(start_path = '.',option=0):
	if option == 0:
		return_me = 0
	elif option == 1:
		return_me = []
	else:
		print('Error: option {} not recognized'.format(option))
		return
	for dirpath, dirnames, filenames in os.walk(start_path):
		# print(dirpath)
		# print(dirnames)
		# print(filenames)
		for f in filenames:
			fp = os.path.join(dirpath, f)
			# skip if it is symbolic link
			if not os.path.islink(fp):
				if option == 0:
					return_me += os.path.getsize(fp)
				elif option == 1:
					return_me.append([f,os.path.getsize(fp)])
	return return_me


#given the attributes of a dataset, this function returns the
#	appropriate data tag number
def get_data_num(bodies,force,approx,delta_t,total_t):
	for dat in os.listdir('./data_dump/usr_data/'):
		f = h5py.File('./data_dump/usr_data/{}'.format(dat))
		if f.attrs['approximation'] == approx and f.attrs['force'] == force:
			if np.array_equal(list(f.attrs['bodies']), np.array(bodies)) and f.attrs['dt'] == float(delta_t) and f.attrs['total_time'] == float(total_t):
				return dat.split('_')[-1].split('.')[0]	
	return -1

#given a string containing the attributes of a dataset, this function returns the
#	appropriate data tag number
def get_data_num_single_str(data):
	# print(data)
	for att in data.split(','):
		if 'Approx=' in att:
			approx = att.strip('Approx=')
		elif 'Force=' in att:
			force = att.strip('Force=')
		elif 'Bodies=' in att:
			bodies = att.strip('Bodies=')
		elif 'dt=' in att:
			dt = float(att.strip('dt='))
		elif 'TotalTime=' in att:
			tot_time = float(att.strip('TotalTime='))
	for dat in os.listdir('./data_dump/usr_data/'):
		f = h5py.File('./data_dump/usr_data/{}'.format(dat))
		# print(f.attrs['bodies'], list_from_string(bodies),bodies,type(bodies))
		if f.attrs['approximation'] == approx and f.attrs['force'] == force:
			if np.array_equal(f.attrs['bodies'],list_from_string(bodies)) and f.attrs['dt'] == float(dt) and f.attrs['total_time'] == float(tot_time):
				return dat.split('_')[-1].split('.')[0]	
	return -1	

#returns a list of the user saved data attributes
def get_existing_data():
	return_me = []
	for dat in os.listdir('./data_dump/usr_data/'):
		if os.path.isfile('./data_dump/usr_data/'+dat):
			try:
				f = h5py.File('./data_dump/usr_data/{}'.format(dat))
				return_me.append('Approx={}, Force={}, Bodies={}, dt={}, Total Time={}'.format \
					(f.attrs['approximation'],f.attrs['force'],f.attrs['bodies'], \
						f.attrs['dt'],f.attrs['total_time']) \
				)
			except:
				os.system('rm ./data_dump/usr_data/{}'.format(dat))
	return return_me

class gui:
	"""gui class contains all methods and variables needed for all GUIs.
		GUIs include the main GUI, delete data GUI, and select premade 
		initial conditions (not yet implimented)."""
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

		self.frm_delete_list = -1

		###Begin main window making###
		if not os.path.isdir('data_dump'):
			os.mkdir('data_dump')

		self.window = tk.Tk()
		self.window.title('N-Body Simulation')
		self.window.resizable(True, True)

		# self.w_width  = self.window.winfo_screenwidth()
		# self.w_height = self.window.winfo_screenheight()
		# self.window.geometry(f'{self.w_width}x{self.w_height}')

		#set up frames
		
		self.frm_graph = tk.Frame(master=self.window, bg="green", \
			relief=tk.FLAT, borderwidth=5)
		self.frm_graph.grid(row=0,column=1,columnspan=1,rowspan=1, \
			padx=0,pady=0,sticky='NSEW')
		self.frm_graph.rowconfigure(0, weight=1)
		self.frm_graph.columnconfigure(0, weight=1)
		self.make_graph_frame()

		self.frm_input = tk.Frame(master=self.window)
		self.frm_input.grid(row=0,column=0,columnspan=1,rowspan=1, \
			padx=0,pady=0,sticky='NSEW')
		# self.frm_input.columnconfigure(0,weight=1)
		self.frm_input.rowconfigure(0,weight=1)
		self.frm_input.rowconfigure(1,weight=1)
		self.frm_input.rowconfigure(2,weight=1)
		self.frm_input.rowconfigure(3,weight=1)
		self.make_input_frame()

		wid = self.fg_width+self.fi_width
		self.frm_display_message = tk.Frame(master=self.window, \
			bg='red', relief=tk.RIDGE, borderwidth=5,height=50)

		self.frm_display_message.grid(row=1,column=0,columnspan=4, \
			rowspan=1,padx=0,pady=0,sticky='NSEW')
		self.make_message_frame()

		self.window.columnconfigure(1, weight=1)
		self.window.rowconfigure(0, weight=1)
		self.window.rowconfigure(1, weight=1)
		
		self.frm_display_message.rowconfigure(0, weight=1)
		self.frm_display_message.rowconfigure(1, weight=1)
		self.frm_display_message.columnconfigure(1, weight=1)

		for i in range(4):
			self.frm_p_input.columnconfigure(i, weight=1)
			self.frm_p_input.rowconfigure(i, weight=1)
		for i in range(4):
			self.frm_variable_input.columnconfigure(i, weight=1)
			self.frm_variable_input.rowconfigure(i, weight=1)
		for i in range(4):
			self.existing_data_frame.columnconfigure(i, weight=1)
			self.existing_data_frame.rowconfigure(i, weight=1)

	
	#Controls the Label in the main GUI that displays how much 
	#	user data is currently being stored
	def set_data_amount(self):
		string1 = 'Storing '
		string2 = ' of saved data'

		directory = os.getcwd() + '/data_dump/'
		# data = sum(os.path.getsize(f) for f in os.listdir(directory) if os.path.isfile(f))
		data = float(get_size(start_path=directory))
		count = 0
		while data > 1000:
			data = data / 1000
			count += 1

		size = 'B'
		if count == 1:
			size = 'KB'
		elif count == 2:
			size = 'MB'
		elif count == 3:
			size = 'GB'
		elif count == 4:
			size = 'TB'
			


		self.used_data_text.set(string1 + '{:.2f}'.format(data) + size + string2) 

	#makes the message frame
	def make_message_frame(self):
		#set up message frame
		master_ = self.frm_display_message
		#make display message stuff
		self.lbl_message_display = tk.Label(master=master_, text='Messages: ')
		self.lbl_message_display.grid(row=0,column=0,padx=5,pady=5, sticky='NS')

		self.lbl_message = tk.StringVar()
		self.lbl_message.set('')
		self.lbl_message_display_message = tk.Label(master=master_, \
			textvariable=self.lbl_message)
		self.lbl_message_display_message.grid(row=0,column=1,columnspan=1,padx=5, \
			pady=5, sticky='NSEW')
		
	#makes the frame the graph will be displayed in
	def make_graph_frame(self):
		#set up graph's frame
		master_ = self.frm_graph
		scale = 1.35
		dpi_ = 80
		self.fig = plt.Figure()
		# self.fig = plt.Figure(figsize=(7*scale,5*scale),dpi=dpi_)
		self.graph_canvas = FigureCanvasTkAgg(self.fig, master=master_)
		self.graph_canvas.get_tk_widget().grid(row=0,column=0,sticky='NSEW')
		
		self.fg_width = self.frm_graph.winfo_width()
		self.fg_height = self.frm_graph.winfo_height()

	#makes the frames the user will interact with
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

		#make all individual user interaction frames
		self.make_p_input_frame()
		self.make_var_input_frame()
		self.make_get_existing_data_frame()
		self.make_run_sim_frame()

		self.fi_width = self.frm_input.winfo_width()
		self.fi_height = self.frm_input.winfo_height()

	#makes the frame with the run button
	def make_run_sim_frame(self):
		master_ = self.frm_run_sim
		self.btn_run = tk.Button(master=master_, text='Run Sim')
		self.btn_run.bind("<Button-1>", self.handle_run_click)
		self.btn_run.grid(row=1,column=1,padx=15,pady=15)
	
		self.window.bind("<Return>", self.handle_run_click)

		self.status_text = tk.StringVar()
		self.status_text.set('Status: Idle')
		self.lbl_status = tk.Label(master=master_,textvariable=self.status_text)
		self.lbl_status.grid(row=1,column=2,padx=15,pady=15)
	
		self.btn_exit = tk.Button(master=master_, text='Exit Sim')
		self.btn_exit.bind("<Button-1>", self.handle_exit_click)
		self.btn_exit.grid(row=1,column=3,padx=15,pady=15)

		master_.grid_rowconfigure(0, weight=1)
		master_.grid_rowconfigure(2, weight=1)
		master_.grid_columnconfigure(0, weight=1)
		master_.grid_columnconfigure(4, weight=1)

	#makes the easy user input frame
	def make_p_input_frame(self):
		#set up input frame 
		master_ = self.frm_p_input

		#make widgets to get new data
		self.approx = ["Central Force","Many-body"]
		self.lbl_approx_input = tk.Label(master=master_, text="Approximation: ")
		self.lbl_approx_input.grid(row=0,column=0,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.make_data_menu_items.append(self.lbl_approx_input)
		self.approx_option = tk.StringVar(master=master_)
		self.approx_option.set(self.approx[1])
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
		self.relativity_checkbx = tk.Checkbutton(master=master_,text='Relativity',variable=self.relativity_bool, \
			command=self.relativity_checkbx_ck)
		self.relativity_checkbx.grid(row=1,column=2,columnspan=2,rowspan=1,padx=1,pady=7)

		self.planet_bool = tk.IntVar()
		self.planet_checkbx = tk.Checkbutton(master=master_,text='Use Planet IC',variable=self.planet_bool, \
			command=self.planet_checkbx_ck)
		self.planet_checkbx.grid(row=2,column=2,columnspan=2,rowspan=1,padx=1,pady=7)
		
	#makes the frame that accepts individual body variables as user input
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

		self.lbl_vyi = tk.Label(master=master_, text='Vyi (au/day):')
		self.lbl_vyi.grid(row=1,column=2,columnspan=1,rowspan=1,padx=1,pady=7,sticky="E")
		# self.input_variable_items.append(self.lbl_vyi)
		self.vyi = tk.Entry(master=master_)
		self.vyi.grid(row=1,column=3,columnspan=1,rowspan=1,padx=1,pady=7,sticky="W")
		# self.input_variable_items.append(self.vyi)

		self.lbl_vzi = tk.Label(master=master_, text='Vzi (au/day):')
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

		
	#makes the frame where the user can select their already
	#	made data
	def make_get_existing_data_frame(self):
		master_ = self.existing_data_frame
		#make widgets to get existing data
		self.exist_data_bool = tk.IntVar()
		self.existing_data_checkbx = tk.Checkbutton(master=master_,text='Use existing data', \
			variable=self.exist_data_bool, command=self.existing_data_checkbx_ck)
		self.existing_data_checkbx.grid(row=1,column=2,columnspan=2,rowspan=1, \
			padx=1,pady=7,sticky='E')

		self.used_data_text = tk.StringVar()
		self.set_data_amount()
		self.lbl_used_data = tk.Label(master=master_, textvariable=self.used_data_text)
		self.lbl_used_data.grid(row=1,column=1,columnspan=2,rowspan=1, \
			padx=1,pady=7,sticky='W')

		self.btn_delete_data = tk.Button(master=master_,text='Delete Saved Data')
		self.btn_delete_data.bind("<Button-1>", self.handle_delete_data_click)
		self.btn_delete_data.grid(row=2,column=1,columnspan=2,rowspan=1,padx=1,pady=7, \
			sticky='W')

		self.lbl_get_data_prompt = tk.Label(master=master_, text='Please select an existing data set')
		self.lbl_get_data_prompt.grid(row=3,column=1,columnspan=4,rowspan=1, \
			padx=1,pady=7,sticky='NSEW')
		# self.get_data_menu_items.append(self.lbl_get_data_prompt)

		self.existing_data = get_existing_data()
		self.data_option = tk.StringVar(master=master_)
		if len(self.existing_data) == 0:
			self.existing_data.append('No Previously Saved Data')

		self.data_option.set(self.existing_data[0])

		self.ent_data_input = tk.OptionMenu(master_,self.data_option,*self.existing_data)
		self.ent_data_input.grid(row=4,column=1,columnspan=4,rowspan=1, \
			padx=1,pady=7,sticky='NSEW')

		master_.rowconfigure(0,weight=1)
		master_.rowconfigure(5,weight=1)
		master_.columnconfigure(0,weight=1)
		master_.columnconfigure(5,weight=1)

		dictionary = dict()
		dictionary['Label'] = 1
		dictionary['Button'] = 1
		self.able(master_,'disable',["Checkbutton"],dictionary)
		# self.get_data_menu_items.append(self.ent_data_input)

	#makes the delete data GUI
	def make_delete_list_frame(self):

		if self.frm_delete_list != -1:
			self.frm_delete_list.destroy()

		self.frm_delete_list = tk.Frame(master=self.delete_data_window,relief=tk.RIDGE,borderwidth=5,height=20)

		master_ = self.frm_delete_list

		canvas = tk.Canvas(master=master_)
		scrollbar_v = ttk.Scrollbar(master_, orient="vertical", command=canvas.yview)
		scrollbar_h = ttk.Scrollbar(master_, orient="horizontal", command=canvas.xview)
	
		scrollable_frame = tk.Frame(canvas)

		scrollable_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(
				scrollregion=canvas.bbox("all")
			)
		)

		canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

		canvas.configure(yscrollcommand=scrollbar_v.set)
		canvas.configure(xscrollcommand=scrollbar_h.set)

		self.check_buttons = []
		self.check_buttons_ints = []
		self.data_labels = []
		j = 0
		i = 0
		self.data_sizes = []#get_size(os.getcwd()+'/data_dump/',option = 1)
		for i,data in enumerate(get_existing_data()):
			data = data.replace(', ',',')
			data = data.replace('Total Time','TotalTime')

			
			dat_num = get_data_num_single_str(data)
			self.data_sizes.append(os.path.getsize(os.getcwd()+'/data_dump/usr_data/data_{}.hdf5'.format(dat_num)))
			self.check_buttons_ints.append(tk.IntVar())
			self.check_buttons.append(tk.Checkbutton(master=scrollable_frame,text=data, \
				variable=self.check_buttons_ints[-1]))
			self.check_buttons[-1].grid(row=i,column=1,columnspan=2,sticky='W')
	
			self.data_labels.append(tk.Label())

		if i == 0:
			j = 1
		else:
			j = i + 1

		master_.grid(row=3,column=1,columnspan=2,rowspan=1,sticky='NSEW')
		scrollbar_v.grid(row=1,column=3,rowspan=2,sticky='NSE')
		scrollbar_h.grid(row=j,column=1,columnspan=2,sticky='WSE')
		canvas.grid(row=1,column=1,columnspan=1,rowspan=2,sticky='NSEW')
		master_.rowconfigure(1,weight=1)
		master_.columnconfigure(1,weight=1)

	#TODO
	#If user selects the "relativity" checkbox
	def relativity_checkbx_ck(self):
		return

	#what happens if the user checks the "Use existing data" checkbox
	#	function ables and disables applicable GUI widgets
	def existing_data_checkbx_ck(self):
		dictionary = dict()
		dictionary['Label'] = 1
		mo = 'disabled'
		mo_o = 'normal'
		if not self.exist_data_bool.get():
			mo_o = 'disabled'
			mo = 'normal'

		self.able(self.frm_p_input,mo)
		self.able(self.frm_variable_input,mo)

		dictionary = dict()
		dictionary['Label'] = 1
		dictionary['Button'] = 1
		self.able(self.existing_data_frame,mo_o,["Checkbutton"],dictionary)

	#If user wants to use planet initial conditions.
	#	function ables and disables applicable GUI widgets
	def planet_checkbx_ck(self):
		mo = 'disabled'
		if not self.planet_bool.get():
			mo = 'normal'

		dictionary = dict()
		dictionary['Label'] = 1
		dictionary['Button'] = 1
		self.able(self.frm_variable_input,mo)
		self.able(self.existing_data_frame,mo,[''],dictionary)

	

		
		




	#this method returns the bodies attribute
	# def get_bodies(self):
	# 	f = h5py.File(d.data_name, 'r')
	# 	return f.attrs['bodies']

	#given body radii this function returns the proportional graph
	#	markersizes
	def radii_to_markersize(self,radii):
		return radii*62775.3611135

	#updates the lines of the sim for the animations
	def update_lines(self, num, dataLines, lines):
		for line, data in zip(lines, dataLines):
			# NOTE: there is no .set_data() for 3 dim data...
			line.set_data(data[0:2, :num])
			line.set_3d_properties(data[2, :num])
		return lines

	#TODO
	#runs the progress bar during loading
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

	#given all args as a single string this function makes the data
	#	and displays the animation on the graph
	def make_graph(self,argumentsv):
		approx = ['central','many-body']
		forces = ['grav']#,'em']
		# Attaching 3D axis to the figure
		requested_bodies = ''
		requested_approx = -1
		requested_force = -1
		for i in argumentsv:
			if 'num_planets=' in i:
				try:
					requested_bodies = i.strip('num_planets=')
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


		if len(requested_bodies) == 0:
			requested_bodies = [0,1]
		if requested_force == -1:
			requested_force = 'grav'
		if requested_approx == -1:
			requested_approx = 'central'

		if isinstance(requested_bodies, int):
			if requested_bodies < 0 or requested_bodies > 10:
				print('Requested number of planets not supported. Please set a value from 1 to {}.'.format(d.max_solar_system_bodies))
				return -1
		elif isinstance(requested_bodies, list):
			if requested_approx == 'central' or requested_approx == 'many-body':
				if len(requested_bodies) > d.max_solar_system_bodies:
					print("Requested number of bodies ({}) not supported. Please enter a number from 1 to {} or a list of indices to include with maximum length of {}".format(requested_bodies,d.max_solar_system_bodies,d.max_solar_system_bodies))
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
			self.set_data_amount()
			self.update_menu(get_existing_data(),self.ent_data_input,self.data_option)
		# else:

		dat_num = get_data_num(list_from_string(requested_bodies),requested_force,requested_approx,requested_dt,requested_tt)
		# data,nombre,total_iter,radii = get_data(requested_force,requested_approx,requested_bodies,max_frames=50000,dim=3)
		data,nombre,total_iter,radii = get_data(data_num=dat_num,max_frames=50000,dim=3)

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
		marker_sizes = np.full((len(requested_bodies)),10)

		# marker_sizes = radii_to_markersize(radii)
		# marker_sizes[0] = 40
		# marker_sizes[1:5] *= 10/marker_sizes[3]

		colors = ['y','#ffa07a','#fff56a','b','r','#ff4500','#7a7733','#acf0f9','#109ae1','#808080']
		if self.planet_bool.get() == 1:
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

		self.graph_canvas.get_tk_widget().grid(row=0,column=0,sticky='NSEW')
		# self.graph_canvas.columnconfigure(0,weight=1)
		# self.graph_canvas.rowconfigure(0,weight=1)
		# time.sleep(5)
		self.status_text.set('Status: Idle')

		# results = [data,nombre,total_iter,radii]

	#what happens if the user clicks
	# def handle_get_data_click(self,event):
	# 	self.reset_message()
	# 	if self.get_data_text.get() == 'Make New Data':
	# 		self.get_data_text.set('Get Saved Data')
	# 		# if get_data_menu_bool:
	# 		self.unpack_widgets(self.get_data_menu_items)
	# 			# get_data_menu_bool = False
	# 		# if not make_data_menu_bool:
	# 		self.grid_widgets(self.make_data_menu_items)
	# 		if self.planet_data_or_not_text.get() == 'Use Solar System Variables':
	# 			self.grid_widgets(self.input_variable_items)
	# 		self.btn_add_body.pack()
	# 			# make_data_menu_bool = True
	# 	else:
	# 		self.get_data_text.set('Make New Data')

	# 		# if make_data_menu_bool:
	# 		self.ungrid_widgets(self.make_data_menu_items)
	# 		self.ungrid_widgets(self.input_variable_items)
	# 		self.btn_add_body.pack_forget()
	# 			# make_data_menu_bool = False
	# 		# if not get_data_menu_bool:	
	# 		self.pack_widgets(self.get_data_menu_items)
	# 			# get_data_menu_bool = True
	#	 	self.window.update_idletasks()


	#deletes any extraneous data still in ftp folder and destroys 
	#	main GUI window
	def handle_exit_click(self,event):
		if len(os.listdir('./data_dump/ftp/')) > 0:
			os.system('rm ./data_dump/ftp/*')
		self.window.destroy()

	#What happens when the user clicks the "Run Sim" button
	def handle_run_click(self,event):
		# self.reset_message()
		# lbl_status_value.delete("1.0",tk.END)
		# window.update()
		error_msg = ''
		
		self.status_text.set('Status: Processing')
		# self.prog_bar.pack(padx=10,pady=10)
		# self.prog_bar.start()
		
		self.window.update_idletasks()
		# self.traitement()
		# time.sleep(1)

		self.input_variable_x_variables = np.array(self.input_variable_x_variables)
		self.input_variable_o_variables = np.array(self.input_variable_o_variables)

		if self.exist_data_bool.get() == 0:
			arguments = dict()
			try:
				use_dt = float(self.dt.get())
				arguments['init_dt_'] = use_dt
			except ValueError:
				error_msg += 'Error: Please enter a value for dt\n'
			try:
				use_tt = float(self.tot_time.get())
				arguments['total_time_'] = use_tt
			except ValueError:
				error_msg += 'Error: Please enter a value for total time\n'
			


			approx = self.approx_option.get()
			if approx == 'Central Force':
				app = True
				approx = 'central'
			else:
				app = False
				approx = 'many-body'
			arguments['central_force_'] = app
			
			force = self.force_option.get()
			if force == 'Gravity':
				force = 'grav'
			elif force == 'Electromagnetic':
				force = 'em'
			arguments['force_'] = force
			# self.data_wrote = False


			
			if (len(self.input_variable_x_variables) == 0 or len(self.input_variable_o_variables) == 0) and self.planet_bool.get() == 0:
				error_msg += 'Error: Please enter initial conditions manualy or select "Use Planet IC" (planet initial conditions)\n'
			else:
				arguments['initial_cond_'] = self.input_variable_x_variables
				arguments['other_data_'] = self.input_variable_o_variables
				# bodies = len(self.input_variable_x_variables)
				
				bodies = list_from_string(self.num_bodies.get())
				arguments['bodies_'] = bodies

			if self.planet_bool.get() == 0:
				arguments['names_'] = self.input_variable_names
				arguments['mode_'] = 'custom'
				if len(self.num_bodies.get()) == 0:
					error_msg += 'Warning: Please enter a value for bodies in Python list format, or enter initial conditions manually.'

			else:	
				if self.num_bodies.get() == '':
					error_msg += 'Error: Please enter a number of bodies from 2-9\n'
				else:
					bodies = list_from_string(self.num_bodies.get())
				arguments['names_'] = []
				arguments['mode_'] = 'planetary'
				arguments['bodies_'] = bodies
			
			# self.prog_bar_thread = threading.Thread(group=None,target=self.run_prog_bar, \
			# 	name=None,args=(10,), daemon=True)
			# self.prog_bar_thread.start()
			if len(error_msg) == 0:
				self.loading_thread = threading.Thread(group=None,target=d.numerics, \
					name=None,args=(arguments,), daemon=False)
				# self.run_prog_bar(10)
				self.loading_thread.start()


		else:
			opts = self.data_option.get().split(',')
			approx = opts[0].split('=')[1]
			force = opts[1].split('=')[1]
			bodies = list_from_string(opts[2].split('=')[1])
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
		

		if len(error_msg) == 0:
			inputs = ['approx={}'.format(approx),'force={}'.format(force), \
				'num_planets={}'.format(bodies),'dt={}'.format(use_dt), \
				'total_time={}'.format(use_tt)]
			self.make_graph(inputs)
		else:
			self.lbl_message.set(error_msg[:-1])

		os.system("rm ./data_dump/ftp/*")


	#what happens when the user clicks the "Add Body" button.
	#	errors if user input is not in right form or missing
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
			self.lbl_message.set(error_msg[:-1])

	#makes the delete data GUI when the "Delete Saved Data" button is pressed
	def handle_delete_btn_click(self,event):
		for index,value in enumerate(self.check_buttons):
			if self.check_buttons_ints[index].get() or self.delete_all_ck_btn.get():
				os.system('rm ./data_dump/usr_data/data_{}.hdf5'.format(get_data_num_single_str(value['text'])))
		self.make_delete_list_frame()
		self.set_data_amount()

	#what happens when the "Delete" button is pressed from the 
	#	Delete Data GUI
	def handle_delete_data_click(self,event):
		self.delete_data_window = tk.Toplevel(self.window)
		self.delete_data_window.title('Delete Data')
		self.delete_data_window.resizable(True, True)

		master_ = self.delete_data_window

		self.lbl_delete_window = tk.Label(master=master_,text='Select data and click delete to permanently delete')
		self.lbl_delete_window.grid(row=1,column=1,padx=15,pady=5,sticky='W')

		self.delete_all_ck_btn = tk.IntVar()
		self.btn_all = tk.Checkbutton(master=master_,text='Delete All',variable=self.delete_all_ck_btn) 
			# command=self.delete_all_ck_btn_ck)
		self.btn_all.grid(row=2,column=1,sticky='W',padx=5)

		self.btn_delete = tk.Button(master=master_,text='Delete')
		self.btn_delete.bind("<Button-1>", self.handle_delete_btn_click)
		self.btn_delete.grid(row=2,column=2,sticky='E',padx=15)

		self.make_delete_list_frame()
		
		# self.data_list = get_existing_data()

		# master_.rowconfigure(0,weight=0)
		# master_.rowconfigure(1,weight=0)
		# master_.rowconfigure(2,weight=0)
		master_.rowconfigure(3,weight=1)
		# master_.rowconfigure(4,weight=0)
		# master_.columnconfigure(0,weight=0)
		master_.columnconfigure(1,weight=1)
		# master_.columnconfigure(2,weight=0)	

	#updates the existing data dropdown menu when user data changes
	def update_menu(self,new_menu,update_me,update_option):
		menu = update_me["menu"]
		menu.delete(0, "end")
		for string in new_menu:
			menu.add_command(label=string, 
							 command=lambda value=string: update_option.set(value))
		if len(new_menu) > 0:
			update_option.set(new_menu[0])

	#Enables and disables widgets in a certain frame
	#exceptions is a list of widget types (as strings) that should not be 
	#	enabled or disables
	#numbered_exceptions is a dictionary where the keys are the widget type
	#	and the value is the number of this type of widget before that
	#	type of widget gets disabled
	#mode = 'normal' -> enable children
	#mode = 'disable' -> disable children
	def able(self,frame,mode='normal',exceptions=[""],numbered_exceptions=[""]):
		check_me = dict()
		if type(numbered_exceptions) == dict:
			check_me = numbered_exceptions

		for child in frame.winfo_children():
			wtype = child.winfo_class()
			config = True
			if len(check_me.keys()) > 0:

				if wtype in list(check_me.keys()):
					check_me[wtype] -= 1
					if check_me[wtype] == 0:
						config = False

			if wtype not in exceptions and config:
				child.configure(state=mode)
			elif wtype == 'Frame':
				self.able(child,mode=mode)


def main():
	GUI = gui()
	GUI.window.mainloop()


if __name__ == '__main__':
	main()
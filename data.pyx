#By Lucas Kolanz

#This file contains the numerics class which, given inital conditions,
#	propages the body position and velocity based on Newtons law of
#	universal gravitation.



import numpy as np
import timing as t
import data_py
cimport numpy as np
# # cimport cython
from cython.view cimport array as cvarray
from cpython.array cimport array

# import numpy
# from random import seed
# from random import randint
from datetime import datetime
import os
import sys
import h5py


#Important conversion factors
AU_TO_M = 149597870691
DAY_TO_SEC = 86400;
EM_TO_SM = 333030;
AUPERDAY_TO_MPERSEC = 149597870691/86400;
KM_TO_M = 1000;
GG = 6.67408e-11;#units m^3kg^-1s^-2
G = GG*(DAY_TO_SEC**2)*((EM_TO_SM)*5.9722e24)/(AU_TO_M**3) #units au^3 Msol-1 day^-2
max_solar_system_bodies = 10


# seed(datetime.now())



class numerics:
	"""This class contains helper functions and cython code to 
		propagate bodies using Newtons Universal Law of Gravitation"""

	pos = 0
	vel = 1
	acc = 2
	x = 0
	y = 1
	z = 2
	mass = 0
	radi = 1

	max_len = 100000 # max length of data array before extending dataset (doubles every extnsion)
	
	#supported forces: 
	#	'Grav' = gravitational
	#TODO forces:
	#	'em' = electromagnetic
	def __init__(self, arg):
		super(numerics, self).__init__()
		
		if not isinstance(arg,dict):
			print("arg attribute must be dict type")
		
		if 'total_time_' in arg.keys():
			self.total_time = arg['total_time_']
		else:
			self.total_time = 36500
		if 'central_force_' in arg.keys():
			self.central_force = arg['central_force_']
		else:
			self.central_force = False
		if 'init_dt_' in arg.keys():
			self.dt = arg['init_dt_']
		else:
			self.dt = 0.1
		if 'names_' in arg.keys():
			self.names = arg['names_']
		else:
			self.names = []
		if 'force_' in arg.keys():
			self.force = arg['force_']
		else:
			self.force = 'grav'
		if 'initial_cond_' in arg.keys():
			self.initial_cond = arg['initial_cond_']
		else:
			self.initial_cond = []
		if 'other_data_' in arg.keys():
			self.other_data = arg['other_data_']
		else:
			self.other_data = []
		if 'bodies_' in arg.keys():
			self.bodies = arg['bodies_']
		else:
			self.bodies = -1
		if 'mode_' in arg.keys():
			self.mode = arg['mode_']
		else:
			self.mode = 'planetary' #other option is 'custom'

		if self.central_force:
			self.approx = 'central'
		else:
			self.approx = 'many-body' 
		if self.mode == 'planetary':
			self.op = 1
		else:
			self.op = 0
		#data[iteration][body][{x},{y},{z}]   (only position data)
		self.current_time = 0.0
		self.previous_velocity = []
		self.f = h5py.File('./data_dump/usr_data/'+data_py.get_new_data_name(), 'w')
		self.data_index = 0
		self.num_writes = 0
		self.previous_angmom = np.nan
		self.data = []

		if isinstance(self.bodies,int):
			self.bodies = list(range(0,self.bodies))

		self.ti = t.stopwatch()

		
		# if bodies_ == -1 and (len(initial_cond_) == 0 and len(other_data_) == 0):
		# 	self.initial_cond = []
		# 	self.other_data = []
		# 	self.previous_velocity = []
		# 	self.bodies = -1
		if len(self.initial_cond) != 0:
			self.bodies = np.array(self.initial_cond).shape[0]
			self.previous_velocity = self.initial_cond[:,self.vel,:]
		# if self.bodies != -1:
		# 	self.data = self.f.create_dataset('position_data', \
		# 		(self.max_len, self.bodies, 3), \
		# 		dtype=np.float64, \
		# 		maxshape=(None,self.bodies,3))
		# 	if len(self.initial_cond) != 0:
		# 		self.data[0,:,:] = self.initial_cond[:,self.pos,:]
		self.make_data(self.op)

	#option=0 -> position magnitude
	#option=1 -> velocity magnitude
	# returns an array of magnitudes by body
	def magnitude(self,option):
		if option == 0:
			return_me = np.square(self.data[self.data_index,:,self.x])
			return_me = np.add(return_me, np.square(self.data[self.data_index,:,self.y]))
			return_me = np.add(return_me, np.square(self.data[self.data_index,:,self.z]))
			return np.sqrt(return_me)
		else:
			return_me = np.square(self.previous_velocity[:,self.x])
			return_me = np.add(return_me, np.square(self.previous_velocity[:,self.y]))
			return_me = np.add(return_me, np.square(self.previous_velocity[:,self.z]))
			
			return np.sqrt(return_me)

	def change_dataset_size(self):
		self.data.resize((self.max_len,len(self.bodies),3))

	def write_datas(self):
	
		self.f.attrs['bodies'] = self.bodies
		self.f.attrs['force'] = self.force
		self.f.attrs['approximation'] = self.approx
		self.f.attrs['dt'] = self.dt
		self.f.attrs['total_time'] = self.total_time
		self.f.attrs['iterations'] = self.data_index
		self.f.attrs['names'] = self.names
		# self.f.attrs['masses'] = self.other_data[:][self.mass]
		if len(np.array(self.other_data).shape) > 1:
			self.f.attrs['radii'] = self.other_data[self.radi][:]

		self.f.close()

	def set_init_conds(self, init_cond, other_init,names):
		self.initial_cond = init_cond
		self.previous_velocity = init_cond[:,self.vel,:]
		self.other_data = other_init
		self.names = names


	def play(self):
		self.ti.start(race='play')
		self.data_index = int(self.total_time/self.dt)+1
		
		num_bodies = len(self.bodies)


		temp_data = np.zeros((self.data_index,num_bodies,3),dtype=np.float64)
		temp_data[0,:,:] = np.array(self.initial_cond[:,self.pos,:])
		cdef double c_current_time,c_total_time
		cdef int c_data_index,data_len

		# cdef int [:] c_bodies = np.array(self.bodies)
		cdef double [:,:,:] c_data = temp_data
		# for iii in range(c_data.shape[1]):
		# 	for ii in range(c_data.shape[2]):
		# 		print(c_data[0][iii][ii])
		cdef double [:,:] c_other_data = self.other_data
		cdef double [:,:] c_veloc = np.array(self.initial_cond[:,self.vel,:])
		cdef int c_num_bodies,x,y,z,mass,dt,dat_ind,i,j
		cdef int c_central_force
		cdef double mag, vec, acci, r
		

		c_current_time = self.current_time
		c_total_time = self.total_time
		data_len = self.data_index
		c_num_bodies = num_bodies

		c_central_force = self.central_force
		x = self.x
		y = self.y
		z = self.z
		pos = self.pos
		vel = self.vel
		dt = self.dt
		mass = self.mass

		# for k in range(c_bodies):
			# c_veloc[k][:] = self.initial_conditions[k,vel,:]  

		for dat_ind in range(data_len-1):
			# for a in range(c_veloc.shape[0]):
			# 	for b in range(c_veloc.shape[1]):
			# 		print(c_veloc[a,b])
			for i in range(c_num_bodies):

				if c_central_force and i == 0:
					continue

				for j in range(c_num_bodies):
					mag = 0
					vec = 0
					r = 0

					if c_central_force:
						j=0

					if i != j:
						for m in range(3):
							r += (c_data[dat_ind][i][m] - c_data[dat_ind][j][m])**2
						#units au^3 Msol-1 day^-2
						c_data[dat_ind+1,i,:] = c_data[dat_ind,i,:]
						mag = G*c_other_data[mass][j]/(r**(3/2))

						vec = (c_data[dat_ind][j][x] - c_data[dat_ind][i][x])
						acci = mag*vec
						c_veloc[i][x] += acci*dt
						c_data[dat_ind+1][i][x] += c_veloc[i][x]*dt
						
						vec = (c_data[dat_ind][j][y] - c_data[dat_ind][i][y])
						acci = mag*vec
						c_veloc[i][y] += acci*dt
						c_data[dat_ind+1][i][y] += c_veloc[i][y]*dt
						
						vec = (c_data[dat_ind][j][z] - c_data[dat_ind][i][z])
						acci = mag*vec
						c_veloc[i][z] += acci*dt
						c_data[dat_ind+1][i][z] += c_veloc[i][z]*dt

					if c_central_force:
						break

		self.data = np.array(c_data)
		self.f.create_dataset('position_data', \
				(self.data_index, c_num_bodies, 3), \
				dtype=np.float64, data=self.data, \
				maxshape=(self.data_index,c_num_bodies,3))

		self.write_datas()
		self.ti.stop(race='play',option='v')


	def get_force_name(self):
		approx = ''
		force = ''
		if self.central_force:
			approx = 'central'
		else:
			approx = 'many-body'

		return approx+self.force


	def get_angular_momentum(self):
		return_me = 0
		pos_mag = self.magnitude(option=0)
		vel_mag = self.magnitude(option=1)
		for i in range(self.bodies):
			return_me += self.other_data[self.mass][i]*pos_mag[i]*vel_mag[i]
		return return_me

	def update_dt(self):

		current_angmom = self.get_angular_momentum()
		if not np.isnan(self.previous_angmom):
			if np.abs(current_angmom - self.previous_angmom) < 0.00001:
				self.dt += self.dt * 0.01
			else:
				self.dt -= self.dt * 0.10
		
		self.previous_angmom = current_angmom
		print(self.dt)
		return


	#option == 0 -> all initial conditions are already set
	#option == 1 -> need to get initial conditions of planets 
	def make_data(self,option):

		if option == 0:
			self.play()
			return
		else:

			if isinstance(self.bodies,int):
				if self.bodies > 0:
					list_bodies = np.arange(0,self.bodies)
				else:
					print("Error: Please enter number of bodies as list or positive int")
					return -1
			elif isinstance(self.bodies,list):
				list_bodies = np.array(self.bodies)
			else:
				print("Error: 'bodies' attribute in make_data() not found")
				return -1
			#initial_conditions[body,{pos}{vel},{x}{y}{z}]
			
			dat,o_dat,names = data_py.get_planet_init_cond(list_bodies)
			self.set_init_conds(dat,o_dat,names)
			# print("after sic: {}".format(os.listdir('./data_dump/ftp/')))
			self.play()
			return
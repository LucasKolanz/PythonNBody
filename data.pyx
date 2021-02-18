import numpy as np
import timing as t
cimport numpy as cnp
# cimport cython
from cython.view cimport array as cvarray
from cpython.array cimport array
import os
import sys
import h5py

AU_TO_M = 149597870691
DAY_TO_SEC = 86400;
EM_TO_SM = 333030;
AUPERDAY_TO_MPERSEC = 149597870691/86400;
KM_TO_M = 1000;
GG = 6.67408e-11;#units m^3kg^-1s^-2
G = GG*(DAY_TO_SEC**2)*((EM_TO_SM)*5.9722e24)/(AU_TO_M**3) #units au^3 Msol-1 day^-2
max_solar_system_bodies = 9



# data_name = 'position_data.hdf5'




def get_planet_init_cond(list_bodies):
	initial_conditions = np.zeros((list_bodies.shape[0],2,3))
	#other_info[{mass}{radius},body]
	other_info = np.zeros((2,list_bodies.shape[0]))
	names = []

	# velocities in au/day
	# positions in au
	# mass in solar mass
	if 0 in list_bodies:
		i = 0
		#sun
		names.append('Sun')
		initial_conditions[i][0][0] = 0 #X0
		initial_conditions[i][0][1] = 0 #Y0
		initial_conditions[i][0][2] = 0 #Z0
		
		initial_conditions[i][1][0] = 0 #Vx0
		initial_conditions[i][1][1] = 0 #Vy0
		initial_conditions[i][1][2] = 0 #Vz0

		other_info[0][i] = 1 #mass
		other_info[1][i] = 0.00465047 #radius

	if 1 in list_bodies:
		i += 1
		#mercury
		names.append('Mercury')
		initial_conditions[i][0][0] = -3.124921389426347E-01 #X0
		initial_conditions[i][0][1] = -3.231017308099852E-01 #Y0
		initial_conditions[i][0][2] = 2.264004677880896E-03 #Z0
		
		initial_conditions[i][1][0] = 1.450098838504057E-02 #Vx0
		initial_conditions[i][1][1] = -1.827392737866101E-02 #Vy0
		initial_conditions[i][1][2] = -2.823480785896841E-03 #Vz0

		other_info[0][i] = 1.651e-7  #mass
		other_info[1][i] = 1.63083872e-5 #radius

	if 2 in list_bodies:
		i += 1
		#venus
		names.append('Venus')
		initial_conditions[i][0][0] = -4.531869011211467E-02 #X0
		initial_conditions[i][0][1] = -7.253165832792150E-01 #Y0
		initial_conditions[i][0][2] = -7.337816726564671E-03 #Z0
		
		initial_conditions[i][1][0] = 2.005150325251360E-02 #Vx0
		initial_conditions[i][1][1] = -1.338183192105111E-03 #Vy0
		initial_conditions[i][1][2] = -1.175477383638605E-03 #Vz0

		other_info[0][i] = 0.000002447 #mass
		other_info[1][i] = 4.04537843e-5 #radius


	if 3 in list_bodies:
		i += 1
		#earth
		names.append('Earth')
		initial_conditions[i][0][0] = -1.550257085548271E-01 #X0
		initial_conditions[i][0][1] = -1.003588459006916E+00 #Y0
		initial_conditions[i][0][2] = 4.967984437823963E-05 #Z0
		
		initial_conditions[i][1][0] = 1.671964880246573E-02 #Vx0
		initial_conditions[i][1][1] = -2.696563942942344E-03 #Vy0
		initial_conditions[i][1][2] = 3.499545652652556E-07 #Vz0

		other_info[0][i] = 1/EM_TO_SM #mass
		other_info[1][i] = 1/23454.8 #radius


	if 4 in list_bodies:
		i += 1
		#mars
		names.append('Mars')
		initial_conditions[i][0][0] = 7.656049322021028E-01 #X0
		initial_conditions[i][0][1] = -1.172049785802159E+00 #Y0
		initial_conditions[i][0][2] = -4.334114585942423E-02 #Z0
		
		initial_conditions[i][1][0] = 1.224571787006004E-02 #Vx0
		initial_conditions[i][1][1] = 8.853276243753566E-03 #Vy0
		initial_conditions[i][1][2] = -1.149047792967216E-04 #Vz0

		other_info[0][i] = 3.213e-7 #mass
		other_info[1][i] = 2.27075425e-5 #radius


	if 5 in list_bodies:
		i += 1
		#jupiter
		names.append('Jupiter')
		initial_conditions[i][0][0] = 1.710479118687038E+00 #X0
		initial_conditions[i][0][1] = -4.876479343950519E+00 #Y0
		initial_conditions[i][0][2] = -1.801532969637167E-02 #Z0
		
		initial_conditions[i][1][0] = 7.037611366618768E-03 #Vx0
		initial_conditions[i][1][1] = 2.856954462047065E-03 #Vy0
		initial_conditions[i][1][2] = -1.693039791075531E-04 #Vz0

		other_info[0][i] = 0.0009543 #mass
		other_info[1][i] = 0.000477894503 #radius


	if 6 in list_bodies:
		i += 1
		#saturn
		names.append('Saturn')
		initial_conditions[i][0][0] = 4.574047748292517E+00 #X0
		initial_conditions[i][0][1] = -8.910379134359962E+00 #Y0
		initial_conditions[i][0][2] = -2.714155779463191E-02 #Z0
		
		initial_conditions[i][1][0] = 4.660833672965436E-03 #Vx0
		initial_conditions[i][1][1] = 2.535827026110950E-03 #Vy0
		initial_conditions[i][1][2] = -2.296255933767816E-04 #Vz0

		other_info[0][i] = 0.0002857 #mass
		other_info[1][i] = 0.000402866697 #radius


	if 7 in list_bodies:
		i += 1
		#uranus
		names.append('Uranus')
		initial_conditions[i][0][0] = 1.584565831457336E+01 #X0
		initial_conditions[i][0][1] = 1.186850271611982E+01 #Y0
		initial_conditions[i][0][2] = -1.611705227327084E-01 #Z0
		
		initial_conditions[i][1][0] = -2.380000642410224E-03 #Vx0
		initial_conditions[i][1][1] = 2.967412286201140E-03 #Vy0
		initial_conditions[i][1][2] = 4.190342137343341E-05 #Vz0

		other_info[0][i] = 0.00004365 #mass
		other_info[1][i] = 0.000170851362 #radius


	if 8 in list_bodies:
		i += 1
		#neptune
		names.append('Neptune')
		initial_conditions[i][0][0] = 2.934520587108444E+01 #X0
		initial_conditions[i][0][1] = -5.862792939590141E+00 #Y0
		initial_conditions[i][0][2] = -5.556420990247191E-01 #Z0
		
		initial_conditions[i][1][0] = 6.020858054847442E-04 #Vx0
		initial_conditions[i][1][1] = 3.100842483536389E-03 #Vy0
		initial_conditions[i][1][2] = -7.799193902035271E-05 #Vz0

		other_info[0][i] = 0.00005149 #mass
		other_info[1][i] = 0.000165537115 #radius

	return initial_conditions,other_info,names




#option == 0 -> regular planet data
#option == 1 -> custom body data
def get_new_data_name(option=0):
	largest_num = 0
	add_me = ''
	if option == 1:
		add_me = 'custom'
	for i in os.listdir('./data_dump/'):
		d = i.split("_")
		num = int(d[1].split('.')[0])
		if num > largest_num:
			largest_num = num

	return '{}data_{}.hdf5'.format(add_me,largest_num+1)
	


class numerics:
	"""docstring for numerics"""

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
		self.f = h5py.File('./data_dump/'+get_new_data_name(), 'w')
		self.data_index = 0
		self.num_writes = 0
		self.previous_angmom = np.nan
		self.data = []
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
		self.data.resize((self.max_len,self.bodies,3))

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
		temp_data = np.zeros((self.data_index,self.bodies,3),dtype=np.float64)
		temp_data[0,:,:] = np.array(self.initial_cond[:,self.pos,:])
		cdef double c_current_time,c_total_time
		cdef int c_data_index,data_len

		cdef double [:,:,:] c_data = temp_data
		# for iii in range(c_data.shape[1]):
		# 	for ii in range(c_data.shape[2]):
		# 		print(c_data[0][iii][ii])
		cdef double [:,:] c_other_data = self.other_data
		cdef double [:,:] c_veloc = np.array(self.initial_cond[:,self.vel,:])
		cdef int c_bodies,x,y,z,mass,dt,dat_ind,i,j
		cdef int c_central_force
		cdef double mag, vec, acci, r
		

		c_current_time = self.current_time
		c_total_time = self.total_time
		data_len = self.data_index

		c_bodies = self.bodies
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
			for i in range(c_bodies):

				if c_central_force and i == 0:
					continue

				for j in range(c_bodies):
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
				(self.data_index, self.bodies, 3), \
				dtype=np.float64, data=self.data, \
				maxshape=(self.data_index,self.bodies,3))

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
			
			dat,o_dat,names = get_planet_init_cond(list_bodies)
			self.set_init_conds(dat,o_dat,names)
			self.play()
			return
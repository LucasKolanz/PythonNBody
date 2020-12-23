import numpy as np
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



# option = 0 -> append to data file, if one exists
# option = 1 -> make new data file, regardless
# def write_datas(self):

# 	if self.num_writes == 0 or not os.path.isfile(data_name):
# 		f = h5py.File(data_name, 'w')
# 		data_set = f.create_dataset(data_name.split('.')[0], \
# 			(self.max_len, \
# 			self.data.shape[1], self.data.shape[2]), \
# 			dtype=np.float64)
# 		data_set[:,:,:] = self.data
# 		f.close()
# 	else:
# 		'''TODO'''
# 		first = self.max_len*self.num_writes
# 		rest = self.data_index
# 		read_me = h5py.File(data_name, 'r')
# 		prev_data = read_me['position_data'][:][:][:]
# 		read_me.close() 
# 		f = h5py.File(data_name, 'w')
# 		data_set = f.create_dataset(data_name.split('.')[0], \
# 			(first+rest,self.data.shape[1], \
# 			self.data.shape[2]), \
# 			dtype=np.float64)
# 		data_set[:first,:,:] = prev_data
# 		data_set[first:first+rest,:,:] = self.data


def make_data(force,approx,dt,total_time,bodies=-1,data=[],other_data=[]):
	#use if planet_data_or_not_text.get() == 'Input Body Variables'
	if len(data) != 0 and len(other_data) != 0:
		initial_conditions = np.array(data)
		other_info = np.array(other_data)

		sim = numerics(initial_conditions, other_info, force,central_force_=app,init_dt_=dt,total_time_=total_time)
		# sim.write_datas()
		sim.play()
		return
	#use if planet_data_or_not_text.get() != 'Input Body Variables'
	else:
		if approx == 'central':
			app = True
		else:
			app = False
		if isinstance(bodies,int):
			if bodies > 0:
				list_bodies = np.arange(0,bodies)
			else:
				print("Error: Please enter number of bodies as list or positive int")
				return -1
		elif isinstance(bodies,list):
			list_bodies = bodies
		else:
			print("Error: 'bodies' attribute in make_data() not found")
			return -1
		#initial_conditions[body,{pos}{vel},{x}{y}{z}]
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
		
		sim = numerics(initial_conditions, other_info, force,names_=names, central_force_=app,init_dt_=dt,total_time_=total_time)
		# sim.write_datas()
		sim.play()
		# sim.write_datas()
		return


def get_new_data_name():
	largest_num = 0
	for i in os.listdir('./data_dump/'):
		d = i.split("_")
		if int(d[1].strip('.hdf5')) > largest_num:
			largest_num = int(d[1].strip('.hdf5'))

	return 'data_{}.hdf5'.format(largest_num+1)
	


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
	def __init__(self, initial_cond_, other_data_, force_='grav', names_ = [], total_time_=3650*4*6, init_dt_=0.1, central_force_=False):
		super(numerics, self).__init__()
		self.initial_cond = initial_cond_
		self.other_data = other_data_
		self.total_time = total_time_
		self.current_time = 0.0
		self.central_force = central_force_
		self.bodies = initial_cond_.shape[0]
		self.dt = init_dt_
		self.names = names_
		self.force = force_
		if self.central_force:
			self.approx = 'central'
		else:
			self.approx = 'many-body' 
		#data[iteration][body][{x},{y},{z}]   (only position data)
		# self.data = np.full((self.max_len, self.bodies, 3),np.nan)
		self.f = h5py.File('./data_dump/'+get_new_data_name(), 'w')
		self.data = self.f.create_dataset('position_data', \
			(self.max_len, self.bodies, 3), \
			dtype=np.float64, \
			maxshape=(None,self.bodies,3))
		self.data_index = 0
		self.data[0,:,:] = self.initial_cond[:,self.pos,:]
		self.previous_velocity = self.initial_cond[:,self.vel,:]
		self.num_writes = 0
		self.previous_angmom = np.nan

	#option=0 -> position magnitude
	#option=1 -> velocity magnitude
	# returns an array of magnitudes by body
	def magnitude(self,option):
		if option == 0:
			# print(self.data[self.data_index,:,self.x])
			return_me = np.square(self.data[self.data_index,:,self.x])
			# print(return_me)
			# print('\n')
			return_me = np.add(return_me, np.square(self.data[self.data_index,:,self.y]))
			# print(self.data[self.data_index,:,self.y])
			# print(return_me)
			return_me = np.add(return_me, np.square(self.data[self.data_index,:,self.z]))
			# sys.exit(0)
			return np.sqrt(return_me)
		else:
			# print(self.previous_velocity)
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
		self.f.attrs['radii'] = self.other_data[self.radi][:]

		self.f.close()

	def play(self):
		while self.current_time < self.total_time:
			new_data = self.iterate(self.data[self.data_index])
			# print(self.data[self.data_index])
			# print('\n')
			# print(new_data)
			self.data_index += 1
			if self.data_index >= self.max_len:
				self.num_writes += 1
				self.max_len *= 2
				self.change_dataset_size()
				# self.data = np.full((self.max_len, self.bodies, 3),np.nan)
				# self.data_index = 0

			self.data[self.data_index] = new_data
			# self.update_dt()
			self.current_time += self.dt
		self.write_datas()

	def get_force_name():
		approx = ''
		force = ''
		if self.central_force:
			approx = 'central'
		else:
			approx = 'many-body'

		return approx+self.force

	#can be made faster
	def iterate(self, data):
		return_me = np.array(data)
		veloc = self.previous_velocity
		for i in range(self.bodies):
			if self.central_force and i == 0:
				continue

			for j in range(self.bodies):
				mag = 0
				vec = 0
				r = 0

				if self.central_force:
					j=0

				if i != j:
					for m in range(3):
						r += (return_me[i][m] - return_me[j][m])**2
					# print(r)
					#units au^3 Msol-1 day^-2
					mag = G*self.other_data[self.mass][j]/(r**(3/2))

					vec = (return_me[j][self.x] - return_me[i][self.x])
					acci = mag*vec
					veloc[i][self.x] += acci*self.dt
					return_me[i][self.x] += veloc[i][self.x]*self.dt
					
					vec = (return_me[j][self.y] - return_me[i][self.y])
					acci = mag*vec
					veloc[i][self.y] += acci*self.dt
					return_me[i][self.y] += veloc[i][self.y]*self.dt
					
					vec = (return_me[j][self.z] - return_me[i][self.z])
					acci = mag*vec
					veloc[i][self.z] += acci*self.dt
					return_me[i][self.z] += veloc[i][self.z]*self.dt

				if self.central_force:
					break

				# # print(veloc)
				# for k in range(3):
				# 	if k == 0:
				# 		acci = mag*x_vec
				# 	elif k == 1:
				# 		acci = mag*y_vec
				# 	else:
				# 		acci = mag*z_vec

				# 	veloc[i][k] += acci*self.dt
				# 	return_me[i][k] += veloc[i][k]*self.dt

		self.previous_velocity = veloc
		
		return return_me

	def get_angular_momentum(self):
		return_me = 0
		pos_mag = self.magnitude(option=0)
		vel_mag = self.magnitude(option=1)
		for i in range(self.bodies):
			return_me += self.other_data[self.mass][i]*pos_mag[i]*vel_mag[i]
		return return_me

	def update_dt(self):
		# current_angmom = np.sum(np.multiply( \
			# np.multiply(self.other_data[:,self.mass],self.magnitude(option=self.vel)), \
			# self.magnitude(option=self.pos)))
		# print(self.previous_angmom)
		current_angmom = self.get_angular_momentum()
		if not np.isnan(self.previous_angmom):
			if np.abs(current_angmom - self.previous_angmom) < 0.00001:
				self.dt += self.dt * 0.01
			else:
				self.dt -= self.dt * 0.10
		
		self.previous_angmom = current_angmom
		print(self.dt)
		return

		# for i in range(self.bodies):


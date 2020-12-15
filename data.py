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


def get_data_name(force,approx,num_planets):
	return 'force_{}-approx_{}-{}_bodies.hdf5'.format(force,approx,num_planets)
	


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

	max_len = 100000 # max length of data array extending dataset (doubles every extnsion)
	
	#supported forces: 
	#	'Grav' = gravitational
	def __init__(self, initial_cond_, other_data_, force_='Grav', names_ = [], total_time_=3650*4*6, init_dt_=0.1, central_force_=False):
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
		self.f = h5py.File(get_data_name(self.force,self.approx,self.bodies), 'w')
		self.data = self.f.create_dataset('position_data', \
			(self.max_len, self.bodies, 3), \
			dtype=np.float64, \
			maxshape=(None,self.bodies,3))
		self.data_index = 0
		self.data[0,:,:] = self.initial_cond[:,self.pos,:]
		self.previous_velocity = self.initial_cond[:,self.vel,:]
		# print(self.previous_velocity)
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


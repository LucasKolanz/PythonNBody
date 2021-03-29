#By Lucas Kolanz

#This file contains the helper functions for data that have no
#	cython code.


import numpy
import os
import sys
import h5py
import pp 
import timing as t
import subprocess



#Given the file name of the horizons file containing planet mass and radius
#	this funciton returns the mass and radius in the file
def other_from_raw_file(file_name):
	return_me = numpy.zeros((2))
	with open('./data_dump/ftp/'+file_name,'r') as fp:
		mass_index = -1
		mass_found = False
		radius_index = -1
		mass = -1
		radius = -1
		for line in fp.readlines():
			line = line.replace('\n','')	
			line = line.split(' ')
			line = [i for i in line if i!='']
			try:
				if not mass_found:
					mass_index = line.index('Mass') 
					#mass in kg
					try:
						mass = float('{}e{}'.format(line[mass_index+4],line[mass_index+1][4:]))
					except:
						mass = float('{}e{}'.format(line[mass_index+3].split('+')[0],line[mass_index+1][4:])) 
					mass_found = True
					continue
				else:
					pass
			except ValueError:	
				pass
			try:
				radius_index = line.index('Radius') 
				#radius in km
				radius = float(line[radius_index+3].split('+')[0])
			except ValueError:	
				pass

		return_me[0] = mass/1.989e30 #in solar masses
		return_me[1] = radius/1.496e8 #in AU

	# os.system('rm ./data_dump/ftp/{}'.format(file_name))
	return return_me


#Given the file name of the horizons file containing planet position and velocity
#	this funciton returns the mass and radius in the file
def init_cond_from_raw_file(file_name):
	return_me = numpy.zeros((2,3))
	with open('./data_dump/ftp/'+file_name,'r') as fp:
		read = False
		for line in fp.readlines():
			line = line.replace('\n','')	
		

			if line == '$$SOE':
				read = True
			elif read:
				inits = line.replace(' ','').split(',')
				init_vals = [float(i) for i in inits[2:-1]]
				return_me[0,0] = init_vals[0]
				return_me[0,1] = init_vals[1]
				return_me[0,2] = init_vals[2]
				return_me[1,0] = init_vals[3]
				return_me[1,1] = init_vals[4]
				return_me[1,2] = init_vals[5]
				break
			
	# os.system('rm ./data_dump/ftp/{}'.format(file_name))
	return return_me

#Given Horizons options and a unique (for this sim) index this function
#	calls necessary files and functions to extract planet data from 
#	NASA Horizon site
def get_planet_init_cond_from_horizon(index,option,body,frame,start_date,start_time,end_date,end_time):
	init_data = numpy.zeros((2,3))
	other_data = numpy.zeros((2))
	random_num = str(index)
	file_name1 = 'state_vector_{}.log'.format(random_num)
	file_name2 = 'other_{}.log'.format(random_num)
	out = subprocess.run(['bash', 'get_horizons_data.sh', option, random_num, body, frame, start_date, start_time, end_date, end_time])
	if option == 'both':
		init_data = init_cond_from_raw_file(file_name1)
		other_data = other_from_raw_file(file_name2)
		return init_data, other_data
	elif option == 'state_vector':
		init_data = init_cond_from_raw_file(file_name1)
		return init_data
	elif option == 'other':
		other_data = other_from_raw_file(file_name2)
		return other_data


#Given a list of bodies to include, as well as a start date and time, This
#	funciton calls get_planet_init_cond_from_horizon() for every body
#	using multiprocessing to finish all body calls faster
def get_planet_init_cond(list_bodies,start_date="2000-Jan-1",start_time="00:00"):
	ti = t.stopwatch()
	ti.start(race='Get horizon init cond')
	initial_conditions = numpy.zeros((list_bodies.shape[0],2,3))
	#other_info[{mass}{radius},body]
	other_info = numpy.zeros((2,list_bodies.shape[0]))
	names = []
	end_date = start_date[:-1]+str(int(start_date.split('-')[-1])+1)
	end_time = start_time 

	# velocities in au/day
	# positions in au
	# mass in solar mass
	solor_system_body_names = ['Sun','Mercury','Venus','Earth','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
	horizons_planet_id = ['sun','199','299','399','499','599','699','799','899','999']

	#run initial condition getting jobs with parallel processing
	if 1:
		job_server = pp.Server()
		jobs = []

		for index,bod_index in enumerate(list_bodies):
			names.append(solor_system_body_names[bod_index])
			
			func = 'get_planet_init_cond_from_horizon'
			modules = ('numpy','subprocess','os')
			depfuncs = (eval('init_cond_from_raw_file'),eval('other_from_raw_file'))
			if index != 0:
				args = (index,'both',horizons_planet_id[index],'@sun', start_date, start_time, end_date, end_time)					
			else:
				args = (index,'other',horizons_planet_id[index],'@sun', start_date, start_time, end_date, end_time)
			jobs.append(job_server.submit(func=eval(func),args=args,modules=modules,depfuncs=depfuncs))

		job_server.wait()
		for i,job in enumerate(jobs):
			if i != 0:
				initial_conditions[i], temp = job()#get_planet_init_cond_from_horizon()

				other_info[0][i] = temp[0] #mass
				other_info[1][i] = temp[1] #radius
			else:
				temp = job()#get_planet_init_cond_from_horizon(index,'other',horizons_planet_id[index],'@sun', start_date, start_time, end_date, end_time)
				other_info[0][i] = 1  #mass
				other_info[1][i] = temp[1] #radius


	#run initial condition getting jobs sequentially
	else:
		for index,bod_index in enumerate(list_bodies):
			names.append(solor_system_body_names[bod_index])

			if index != 0:
				initial_conditions[index], temp = get_planet_init_cond_from_horizon(index,'both',horizons_planet_id[index],'@sun', start_date, start_time, end_date, end_time)

				other_info[0][index] = temp[0] #mass
				other_info[1][index] = temp[1] #radius
			else:
				temp = get_planet_init_cond_from_horizon(index,'other',horizons_planet_id[index],'@sun', start_date, start_time, end_date, end_time)
				
				other_info[0][index] = 1  #mass
				other_info[1][index] = temp[1] #radius

	ti.stop(race='Get horizon init cond',option='v')
	return initial_conditions,other_info,names

	# if 0 in list_bodies:
	# 	i = 0
	# 	#sun
	# 	names.append('Sun')
	# 	initial_conditions[i][0][0] = 0 #X0
	# 	initial_conditions[i][0][1] = 0 #Y0
	# 	initial_conditions[i][0][2] = 0 #Z0
		
	# 	initial_conditions[i][1][0] = 0 #Vx0
	# 	initial_conditions[i][1][1] = 0 #Vy0
	# 	initial_conditions[i][1][2] = 0 #Vz0
		
	# 	temp = get_planet_init_cond_from_horizon(i,'other','sun','@sun', start_date, start_time, end_date, end_time)

	# 	other_info[0][i] = 1  #mass
	# 	other_info[1][i] = temp[1] #radius

	# if 1 in list_bodies:
	# 	i += 1
	# 	#mercury
	# 	names.append('Mercury')

	# 	initial_conditions[i], temp = get_planet_init_cond_from_horizon(i,'both','199','@sun', start_date, start_time, end_date, end_time)

	# 	other_info[0][i] = temp[0] #mass
	# 	other_info[1][i] = temp[1] #radius


	# 	# other_info[0][i] = 1.651e-7  #mass
	# 	# other_info[1][i] = 1.63083872e-5 #radius

	# if 2 in list_bodies:
	# 	i += 1
	# 	#venus
	# 	names.append('Venus')
	# 	initial_conditions[i], temp = get_planet_init_cond_from_horizon(i,'both','299','@sun', start_date, start_time, end_date, end_time)

	# 	other_info[0][i] = temp[0] #mass
	# 	other_info[1][i] = temp[1] #radius


	# if 3 in list_bodies:
	# 	i += 1
	# 	#earth
	# 	names.append('Earth')
	# 	initial_conditions[i], temp = get_planet_init_cond_from_horizon(i,'both','399','@sun', start_date, start_time, end_date, end_time)

	# 	other_info[0][i] = temp[0] #mass
	# 	other_info[1][i] = temp[1] #radius

	# 	# initial_conditions[i][0][0] = -1.550257085548271E-01 #X0
	# 	# initial_conditions[i][0][1] = -1.003588459006916E+00 #Y0
	# 	# initial_conditions[i][0][2] = 4.967984437823963E-05 #Z0
		
	# 	# initial_conditions[i][1][0] = 1.671964880246573E-02 #Vx0
	# 	# initial_conditions[i][1][1] = -2.696563942942344E-03 #Vy0
	# 	# initial_conditions[i][1][2] = 3.499545652652556E-07 #Vz0

	# 	# other_info[0][i] = 1/EM_TO_SM #mass
	# 	# other_info[1][i] = 1/23454.8 #radius


	# if 4 in list_bodies:
	# 	i += 1
	# 	#mars
	# 	names.append('Mars')
	# 	initial_conditions[i], temp = get_planet_init_cond_from_horizon(i,'both','499','@sun', start_date, start_time, end_date, end_time)

	# 	other_info[0][i] = temp[0] #mass
	# 	other_info[1][i] = temp[1] #radius

	# 	# initial_conditions[i][0][0] = 7.656049322021028E-01 #X0
	# 	# initial_conditions[i][0][1] = -1.172049785802159E+00 #Y0
	# 	# initial_conditions[i][0][2] = -4.334114585942423E-02 #Z0
		
	# 	# initial_conditions[i][1][0] = 1.224571787006004E-02 #Vx0
	# 	# initial_conditions[i][1][1] = 8.853276243753566E-03 #Vy0
	# 	# initial_conditions[i][1][2] = -1.149047792967216E-04 #Vz0

	# 	# other_info[0][i] = 3.213e-7 #mass
	# 	# other_info[1][i] = 2.27075425e-5 #radius


	# if 5 in list_bodies:
	# 	i += 1
	# 	#jupiter
	# 	names.append('Jupiter')
	# 	initial_conditions[i], temp = get_planet_init_cond_from_horizon(i,'both','599','@sun', start_date, start_time, end_date, end_time)

	# 	other_info[0][i] = temp[0] #mass
	# 	other_info[1][i] = temp[1] #radius

	# 	# initial_conditions[i][0][0] = 1.710479118687038E+00 #X0
	# 	# initial_conditions[i][0][1] = -4.876479343950519E+00 #Y0
	# 	# initial_conditions[i][0][2] = -1.801532969637167E-02 #Z0
		
	# 	# initial_conditions[i][1][0] = 7.037611366618768E-03 #Vx0
	# 	# initial_conditions[i][1][1] = 2.856954462047065E-03 #Vy0
	# 	# initial_conditions[i][1][2] = -1.693039791075531E-04 #Vz0

	# 	# other_info[0][i] = 0.0009543 #mass
	# 	# other_info[1][i] = 0.000477894503 #radius


	# if 6 in list_bodies:
	# 	i += 1
	# 	#saturn
	# 	names.append('Saturn')
	# 	initial_conditions[i], temp = get_planet_init_cond_from_horizon(i,'both','699','@sun', start_date, start_time, end_date, end_time)

	# 	other_info[0][i] = temp[0] #mass
	# 	other_info[1][i] = temp[1] #radius
	# 	# initial_conditions[i][0][0] = 4.574047748292517E+00 #X0
	# 	# initial_conditions[i][0][1] = -8.910379134359962E+00 #Y0
	# 	# initial_conditions[i][0][2] = -2.714155779463191E-02 #Z0
		
	# 	# initial_conditions[i][1][0] = 4.660833672965436E-03 #Vx0
	# 	# initial_conditions[i][1][1] = 2.535827026110950E-03 #Vy0
	# 	# initial_conditions[i][1][2] = -2.296255933767816E-04 #Vz0

	# 	# other_info[0][i] = 0.0002857 #mass
	# 	# other_info[1][i] = 0.000402866697 #radius


	# if 7 in list_bodies:
	# 	i += 1
	# 	#uranus
	# 	names.append('Uranus')
	# 	initial_conditions[i], temp = get_planet_init_cond_from_horizon(i,'both','799','@sun', start_date, start_time, end_date, end_time)

	# 	other_info[0][i] = temp[0] #mass
	# 	other_info[1][i] = temp[1] #radius
	# 	# initial_conditions[i][0][0] = 1.584565831457336E+01 #X0
	# 	# initial_conditions[i][0][1] = 1.186850271611982E+01 #Y0
	# 	# initial_conditions[i][0][2] = -1.611705227327084E-01 #Z0
		
	# 	# initial_conditions[i][1][0] = -2.380000642410224E-03 #Vx0
	# 	# initial_conditions[i][1][1] = 2.967412286201140E-03 #Vy0
	# 	# initial_conditions[i][1][2] = 4.190342137343341E-05 #Vz0

	# 	# other_info[0][i] = 0.00004365 #mass
	# 	# other_info[1][i] = 0.000170851362 #radius


	# if 8 in list_bodies:
	# 	i += 1
	# 	#neptune
	# 	names.append('Neptune')
	# 	initial_conditions[i], temp = get_planet_init_cond_from_horizon(i,'both','899','@sun', start_date, start_time, end_date, end_time)

	# 	other_info[0][i] = temp[0] #mass
	# 	other_info[1][i] = temp[1] #radius
	# 	# initial_conditions[i][0][0] = 2.934520587108444E+01 #X0
	# 	# initial_conditions[i][0][1] = -5.862792939590141E+00 #Y0
	# 	# initial_conditions[i][0][2] = -5.556420990247191E-01 #Z0
		
	# 	# initial_conditions[i][1][0] = 6.020858054847442E-04 #Vx0
	# 	# initial_conditions[i][1][1] = 3.100842483536389E-03 #Vy0
	# 	# initial_conditions[i][1][2] = -7.799193902035271E-05 #Vz0

	# 	# other_info[0][i] = 0.00005149 #mass
	# 	# other_info[1][i] = 0.000165537115 #radius

	# if 9 in list_bodies:
	# 	i += 1
	# 	#pluto
	# 	names.append('Pluto')
	# 	initial_conditions[i], temp = get_planet_init_cond_from_horizon(i,'both','999','@sun', start_date, start_time, end_date, end_time)

	# 	other_info[0][i] = temp[0] #mass
	# 	other_info[1][i] = temp[1] #radius 

	# return initial_conditions,other_info,names



#This function returns a new, unique data name when called
#option == 0 -> regular planet data
#option == 1 -> custom body data
def get_new_data_name(option=0):
	largest_num = 0
	add_me = ''
	if option == 1:
		add_me = 'custom'
	for i in os.listdir('./data_dump/usr_data/'):
		d = i.split("_")
		num = int(d[1].split('.')[0])
		if num > largest_num:
			largest_num = num

	return '{}data_{}.hdf5'.format(add_me,largest_num+1)
	

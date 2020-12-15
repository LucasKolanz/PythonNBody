import numpy as np
import data as d
import sys


def make_data(force,approx,bodies):
	if approx == 'central':
		app = True
	else:
		app = False

	if isinstance(bodies,int):
		list_bodies = np.arange(0,bodies)
	elif isinstance(bodies,list):
		list_bodies = bodies
	else:
		print("Error: Bodies attribute in make_data() not found")
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

		other_info[0][i] = 1/d.EM_TO_SM #mass
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
	
	sim = d.numerics(initial_conditions, other_info, force,names_=names, central_force_=app)
	# sim.write_datas()
	sim.play()
	# sim.write_datas()


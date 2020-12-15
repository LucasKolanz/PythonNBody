import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation

fig = plt.figure()
ax = p3.Axes3D(fig)
line = ax.plot([], [])

def update_points(num):
	for point, data in zip(points, dataPoints):
		print(data)
		# NOTE: there is no .set_data() for 3 dim data...
		point.set_data(data[0:2])
		point.set_3d_properties(data[:])
	return points

def init():
    line.set_3d_properties([], [], [])
    return line

def main():

	data = [[[10,20,30],[40,50,60],[70,80,90]],[[5,10,15],[20,25,30],[35,40,45]]]
	


	#lines = [ax.plot([data[0][0][0]],[data[0][i][1]],[data[0][i][2]])[0] for i in range(3)]


	# Setting the axes properties
	ax.set_xlim3d([0.0, 100.0])
	ax.set_xlabel('X')

	ax.set_ylim3d([0.0, 100.0])
	ax.set_ylabel('Y')

	ax.set_zlim3d([0.0, 100.0])
	ax.set_zlabel('Z')

	ax.set_title('3D Test')

	# Creating the Animation object
	line_ani = animation.FuncAnimation(fig, update_points, init_func = init,
	                                   interval=200, blit=False, repeat = False)

	plt.show()

if __name__ == '__main__':
	main()
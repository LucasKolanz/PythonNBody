import time


class stopwatch:
	"""docstring for stopwatch"""
	def __init__(self):
		super(stopwatch, self).__init__()
		self.timings = dict()


	def start(self,race):
		self.timings[race] = time.time()

	def stop(self,race,option=''):
		self.timings[race] = time.time() - self.timings[race]
		if option == 'v':
			self.print_timing()

	def print_timing(self):
		print('=====================================================================')
		for k in self.timings.keys():
			print('Race "{}" took {}sec'.format(k,self.timings[k]))
		print('=====================================================================')
		
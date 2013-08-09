#! /usr/bin/env python3

if __name__ == '__main__':

	class X():
		def g(self):
			for x in range(5): yield x

		class task():
			def __init__(self, gen):
				self.gen = gen
			def __get__(self, inst, owner):
				class Task():
					@staticmethod
					def __call__(): return self.gen(inst)
				r = Task()
				setattr(inst, self.gen.__name__, r)
				return r

		@task
		def t(self):
			for x in self.g(): yield x

	x = X()

	print('implicit')
	for y in x.g(): print(y)

	print('explicit')
	y = x.g()
	while True:
		try: z = next(y)
		except StopIteration: break
		print(z)

	def exec_task(t):
		try: t._done
		except AttributeError: t._done = False
		if not t._done:
			y = t()
			while True:
				try: z = next(y)
				except StopIteration: break
				print(z)
			t._done = True

	print('@task: first')
	exec_task(x.t)

	print('@task: second')
	exec_task(x.t)

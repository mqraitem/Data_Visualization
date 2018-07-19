#Maan Qraitem 
#CS251 
#Project 5

import numpy as np
from math import cos, sin


class View: 
	def __init__(self): 


		self.vrp = None 
		self.vpn = None 
		self.vup = None 
		self.u = None 
		self.extent = None 
		self.screen = None 
		self.offset = None 

		self.reset() 


	#resets back the VRC to default values.
	def reset(self):

		self.vrp = np.matrix([0.5, 0.5, 1])
		self.vpn = np.matrix([0,0,-1])
		self.vup = np.matrix([0,1,0])
		self.u = np.matrix([-1, 0, 0])
		self.extent = [1., 1., 1.]
		self.constScreen = [600., 600.]
		self.screen = [450., 550.]
		self.constOffset = [400., 50.]
		self.offset = [400., 50.]


	#return a normalized version of the vector. 
	def normalize_vector(self, vector):

		Vnorm = np.matrix([1., 1., 1.])
		length = np.linalg.norm(vector) 

		Vnorm[0,0] = vector[0,0] / length
		Vnorm[0,1] = vector[0,1] / length
		Vnorm[0,2] = vector[0,2] / length

		return Vnorm


	#builds the VTM 
	def build(self): 

		vtm = np.identity( 4, float )
		
		t1 = np.matrix( [[1, 0, 0, -self.vrp[0, 0]],
						[0, 1, 0, -self.vrp[0, 1]],
						[0, 0, 1, -self.vrp[0, 2]],
						[0, 0, 0, 1] ] )

		vtm = t1 * vtm

		tu = np.cross(self.vup, self.vpn)
		tvup = np.cross(self.vpn, tu)
		tvpn = np.copy(self.vpn)

		tu = self.normalize_vector(tu)
		tvup = self.normalize_vector(tvup)
		tvpn = self.normalize_vector(tvpn)


		self.u = np.copy(tu)
		self.vup = np.copy(tvup)
		self.tvpn = np.copy(tvpn) 

		r1 = np.matrix( [[ tu[0, 0], tu[0, 1], tu[0, 2], 0.0 ],
							[ tvup[0, 0], tvup[0, 1], tvup[0, 2], 0.0 ],
							[ tvpn[0, 0], tvpn[0, 1], tvpn[0, 2], 0.0 ],
							[ 0.0, 0.0, 0.0, 1.0 ] ] )

		vtm = r1 * vtm


		t2 = np.matrix( [[1, 0, 0, 0.5*self.extent[0]],
						[0, 1, 0, 0.5*self.extent[1]],
						[0, 0, 1, 0],
						[0, 0, 0, 1] ] )

		vtm = t2 * vtm 


		s1 = np.matrix( [[-self.screen[0] / self.extent[0], 0, 0, 0],
						[0 , -self.screen[1] / self.extent[1],0, 0 ],
						[0, 0, 1.0 / self.extent[2], 0],
						[0, 0, 0, 1.0 ] ])

		vtm = s1 * vtm


		t3 = np.matrix( [[1, 0, 0, self.screen[0] + self.offset[0]],
						[0, 1, 0, self.screen[1] + self.offset[1]],
						[0, 0, 1, 0],
						[0, 0, 0, 1] ] )

		vtm = t3 * vtm

		return vtm


	def get_screenX(self):
		return self.screen[0]

	def get_screenY(self): 
		return self.screen[1]

	def get_extentX(self):
		return self.extent[0]

	def get_extentY(self): 
		return self.extent[1] 

	def update_screen(self, dx, dy):
		self.screen[0] = dx * self.constScreen[0]
		self.screen[1] = dy * self.constScreen[1]

		self.offset[0] = dx * self.constOffset[0]
		self.offset[1] = dy * self.constOffset[1]

	#updates the VRP (panning) 
	def update_vrp_translate(self, delta0, delta1): 

		self.vrp[0,0] += self.u[0,0]*delta0 + self.vup[0,0]*delta1
		self.vrp[0,1] += self.u[0,1]*delta0 + self.vup[0,1]*delta1
		self.vrp[0,2] += self.u[0,2]*delta0 + self.vup[0,2]*delta1

	#updates the extent (scaling) 
	def update_extent_scale(self, factor): 

		self.extent[0] = factor
		self.extent[1] = factor 

	#updates the VRC (rotating)
	def update_vrc_rotate(self, thetaUp, thetaU):

		t1 = np.matrix( [[1, 0, 0, -self.vrp[0, 0] - ((self.extent[2]/2) * self.vpn[0,0])],
						[0, 1, 0,  -self.vrp[0, 1] - ((self.extent[2]/2) * self.vpn[0,1])],
						[0, 0, 1,  -self.vrp[0, 2] - ((self.extent[2]/2) * self.vpn[0,2])],
						[0, 0, 0, 1] ] ) 

		Rxyz = np.matrix([[self.u[0,0], self.u[0,1], self.u[0,2], 0],
						   [self.vup[0,0], self.vup[0,1], self.vup[0,2], 0],
						   [self.vpn[0,0], self.vpn[0,1], self.vpn[0,2], 0],
						   [0, 0, 0, 1]])

		r1 = np.matrix([[cos(thetaUp), 0, sin(thetaUp), 0],
						[0, 1, 0, 0],
						[-sin(thetaUp), 0, cos(thetaUp), 0],
						[0, 0, 0, 1]])

		r2 = np.matrix([[1, 0, 0, 0],
						[0, cos(thetaU), -sin(thetaU), 0],
						[0, sin(thetaU), cos(thetaU), 0],
						[0, 0, 0, 1]])

		t2 = np.matrix( [[1, 0, 0, self.vrp[0, 0] + ((self.extent[2]/2) * self.vpn[0,0])],
						[0, 1, 0,  self.vrp[0, 1] + ((self.extent[2]/2) * self.vpn[0,1])],
						[0, 0, 1,  self.vrp[0, 2] + ((self.extent[2]/2) * self.vpn[0,2])],
						[0, 0, 0, 1] ] ) 

		tvrc = np.matrix([[self.vrp[0,0], self.vrp[0,1], self.vrp[0,2], 1],
						   [self.u[0,0], self.u[0,1], self.u[0,2], 0], 
						   [self.vup[0,0], self.vup[0,1], self.vup[0,2], 0],
						   [self.vpn[0,0], self.vpn[0,1], self.vpn[0,2], 0]])

		tvrc = (t2*Rxyz.T*r2*r1*Rxyz*t1*tvrc.T).T

		self.u = np.copy(np.matrix([tvrc[1,0], tvrc[1,1], tvrc[1,2]]))
		self.vup = np.copy(np.matrix([tvrc[2,0], tvrc[2,1], tvrc[2,2]]))
		self.vpn = np.copy(np.matrix([tvrc[3,0], tvrc[3,1], tvrc[3,2]]))
		self.vrp = np.copy(np.matrix([tvrc[0,0], tvrc[0,1], tvrc[0,2]]))

	#clones the view object. 
	def cloneView(self):
		view = View()
		
		view.vrp = np.copy(self.vrp) 
		view.vpn = np.copy(self.vpn)
		view.vup = np.copy(self.vup)
		view.u = np.copy(self.u)
		view.extent = self.extent[:] 
		view.screen = self.screen[:]
		view.offset = self.offset[:]

		return view





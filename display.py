import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import math
import random
import numpy as np
from view import View
from data import Data
import analysis as ay
import matplotlib.pyplot as plt
import csv
from LRdialog import LinearRgressionDialog
from AxesDialog import AxesDialog
from PCADialog import PCADialog
from EigenDialog import EigenDialog
from ClusterDialog import ClusterDialog
from ClusterAxesDialog import ClusterAxesDialog
from ClusterDataDialog import ClusterDataDialog

class DisplayApp:

	def __init__(self, width, height):

		# create a tk object, which is the root window
		self.root = tk.Tk()

		# width and height of the window
		self.initDx = width
		self.initDy = height

		# set up the geometry for the window
		self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )

		# set the title of the window
		self.root.title("Data Cruncher")

		# set the maximum size of the window for resizing
		self.root.maxsize( 1280, 1024 )

		# bring the window to the front
		self.root.lift()

		# Create a View object and set up the default parameters
		self.view = View() 

		# Create the axes fields and build the axes
		self.axes = np.matrix([ [0,0,0,1], 
		                        [1,0,0,1],
		                        [0,1,0,1],
		                        [0,0,1,1] ])


		#easily differentiable colors. 
		self.COLORS = ["#e6194b", "#3cb44b", "#ffe119", "#0082c8", "#f58231", "#911eb4", "#46f0f0", "#f032e6", 
				  "#d2f53c", "#fabebe", "#008080", "#e6beff", "#aa6e28"]

		#holds the lines canvas objects that represent the axis. 
		self.lines = []

		#holds the text objects that represent the x y z axes labels. 
		self.xyz = [] 

		#holds the thetas by which the view has been rotated. 
		self.thetas = [0, 0] 
		
		#used for tracking theta when rotating is taking place. ..
		self.tempThetas = [0, 0]

		#holds the points sizes values for different plots. 
		self.sizes = {}

		#holds the colors values for different plots. 
		self.colors = {}

		#variables for managing the different mouse motions. 
		self.baseClick1 = [0, 0]

		self.baseClick2 = [0, 0]

		self.baseClick3 = [0, 0]

		#variable used for managing the change of the extent value displayed on the screen. 
		self.extentOrigin = [0, 0]

		#variables for managing the resize functionality. 
		self.canvasSizes = [620, 720]

		self.canvasTemp = [620, 715]

		#holds the original view object (used for managing the change of view)
		self.viewOrigin = None

		#default cieling level when generating the sizes. 
		self.sizeValue = 9

		#keeps track of the current factor value. 
		self.factor = 1

		#manages the change of the factor value while doing the rescaling. 
		self.tempFactor = 1

		#all the points objects the represent different scatter plots. 
		self.objects = {}

		#all the data objects the represent different plots. 
		self.data = {}

		#numpy matrices that represent the different data being drawn on canvas. 
		self.current_data = {}

		#holds the lines objects for linear regression. 
		self.lrObject=  {}

		#holds the start and end points for the linear regression lines. 
		self.lrPoints = {}

		#holds the values for each linear regression process: R_squared, coeffecients ... 
		self.lrResults = {}

		#holds the PCAData objects for different PCA analysis. 
		self.PCAanalysis = {}

		#holds the ClusterData objects for different cluster analysis
		self.ClusterAnalysis = {} 

		# setup the menus
		self.buildMenus()

		# build the controls
		self.buildControls()

		#set up the status bar
		self.buildStatusBar()

		# build the objects on the Canvas
		self.buildCanvas()

		# set up the key bindings
		self.setBindings()

		#builds the axes in the canvas. 
		self.buildAxes()


#######################################################
#-Handles cleaning and clearing 
#	- clean data for replotting
#	- handles deleting an entry 
#	- deletes one entry 
# 	- deletes all entries
#######################################################

	#clean any objects drawn on the canvas in order to prepare 
	#for a new plot. 

	def clean_plot(self, filename):
		
		rows = self.data[filename].get_num_points()
		
		de=("%02x"%random.randint(0,255))
		re=("%02x"%random.randint(0,255))
		we=("%02x"%random.randint(0,255))
		ge="#"
		color=ge+de+re+we

		self.colors[filename] = [color for i in range(rows)]
		self.sizes[filename] = [3 for i in range(rows)]

		for pt in self.objects[filename]:
			self.canvas.delete(pt) 

		for line in self.lrObject[filename]:
			self.canvas.delete(line)
		
		self.objects[filename] = [] 
		self.current_data[filename] = [] 
		self.lrObject[filename] = []
		self.lrPoints[filename] = []

	def delete_entry(self, filename): 

		for line in self.lrObject[filename]: 
			self.canvas.delete(line)

		for pt in self.objects[filename]:
			self.canvas.delete(pt) 
		
		del self.lrObject[filename]
		del self.lrPoints[filename]
		del self.lrResults[filename]

		self.labelLR(2, filename)	

		del self.colors[filename]
		del self.sizes[filename]
		del self.objects[filename]
		del self.current_data[filename]

		to_delete_i = []

		for i, PCAname in enumerate(self.PCAbox.get(0, tk.END)):
			if (PCAname.split('_')[0] == filename):
				del self.PCAanalysis[PCAname]
				to_delete_i.append(i)
		
		for i in to_delete_i[::-1]: 
			self.PCAbox.delete(i)

		to_delete_i = []

		for i, Clustername in enumerate(self.clusterListbox.get(0, tk.END)):
			if (Clustername.split('_')[0] == filename):
				del self.ClusterAnalysis[Clustername]
				to_delete_i.append(i)
		
		for i in to_delete_i[::-1]: 
			self.ClusterAnalysis.delete(i)


	def handleDeletePCAEntry(self): 
		
		if len(self.PCAbox.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a CSV file from the listbox first"
			)
			return

		filename = self.PCAbox.get(tk.ACTIVE)
		self.clean_plot(filename.split("_")[0])
		del self.PCAanalysis[filename]
		self.PCAbox.delete(self.PCAbox.curselection()[0])

	def handleDeleteClusterEntry(self): 
		
		if len(self.clusterListbox.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a CSV file from the listbox first"
			)
			return

		filename = self.clusterListbox.get(tk.ACTIVE)
		self.clean_plot(filename.split("_")[0])
		del self.ClusterAnalysis[filename]
		self.clusterListbox.delete(self.clusterListbox.curselection()[0])


	def handleDeleteEntry(self):

		if len(self.dataOpened.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a CSV file from the listbox first"
			)
			return

		filename = self.dataOpened.get(tk.ACTIVE)
		self.delete_entry(filename)
		self.dataOpened.delete(self.dataOpened.curselection()[0])

	def handleDeleteEverything(self): 

		for i, filename in enumerate(self.dataOpened.get(0, tk.END)):
			self.delete_entry(filename)	
		
		self.dataOpened.delete(0, tk.END)


########################################################################
# Handles openning a new file and adding its data.  
# Creates all the important fields in the data stuctures of the GUI. 
#########################################################################

	def handleOpen(self):
		fn = filedialog.askopenfilename( parent=self.root,
		title='Choose a data file', initialdir='.' )
		#checks if the user didn't enter a proper entry or 
		#hit cancel
		if (fn != '' and fn != ()):
			filename = fn.split("/")[-1]
			self.data[filename] = (Data(fn))
			rows = self.data[filename].get_num_points()
			self.sizes[filename] = ([3 for i in range(rows)])

			de=("%02x"%random.randint(0,255))
			re=("%02x"%random.randint(0,255))
			we=("%02x"%random.randint(0,255))
			ge="#"
			color=ge+de+re+we

			self.colors[filename] =([color for i in range(rows)])
			self.dataOpened.insert("end", filename)

			self.current_data[filename] = []
			self.objects[filename] = []
			
			self.lrObject[filename] = []
			self.lrPoints[filename] = []
			self.lrResults[filename] = []


###############################################################################
# Build functions. 															  
# Builds the GUI components like: Menus, buttons ...
# 														  
###############################################################################

	def buildMenus(self):

		# create a new menu
		self.menu = tk.Menu(self.root)

		# set the root menu to our new menu
		self.root.config(menu = self.menu)

		# create a variable to hold the individual menus
		self.menulist = []

		# create a file menu
		filemenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "File", menu = filemenu )
		self.menulist.append(filemenu)


		# menu text for the elements
		menutext = [ [ 'Open   Command-O', '-', 'Linear Regression  Command-L', '-', 'Quit   Command-Q'] ]

		# menu callback functions
		menucmd = [ [self.handleOpen, None, self.handleLinearRegression, None,  self.handleQuit]  ]

		# build the menu elements and callbacks
		for i in range( len( self.menulist ) ):
		    for j in range( len( menutext[i]) ):
		        if menutext[i][j] != '-':
		            self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
		        else:
		            self.menulist[i].add_separator()

	# create the canvas object
	def buildCanvas(self):
		self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy )
		self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
		return

	# build a frame and put controls in it
	def buildControls(self):


		#Rigth Frame and its content frames: 	
		self.rightFrame = tk.Frame(self.root)
		self.sep_right = tk.Frame(self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN)
		self.clusterLabelFrame = tk.Frame(self.rightFrame)
		self.clusterListboxFrame = tk.Frame(self.rightFrame)
		self.openedButtonsClustering = tk.Frame(self.rightFrame)
		self.underopenedButtonsClustering = tk.Frame(self.rightFrame)
		self.finalButtonsClustering = tk.Frame(self.rightFrame)



		#Central Frame and its content frames:
		#-------------------
		self.cntlframe = tk.Frame(self.root)
		self.sep = tk.Frame(self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN)
		self.mainLabelFrame = tk.Frame(self.cntlframe) 
		self.lbFrame = tk.Frame(self.cntlframe)
		self.openedButtons = tk.Frame(self.cntlframe)
		self.underOpenedButtons = tk.Frame(self.cntlframe)
		self.lr_Frame = tk.Frame(self.cntlframe)
		self.lrinfo1 = tk.Frame(self.cntlframe) 
		self.lrinfo2 = tk.Frame(self.cntlframe) 
		self.lrinfo3 = tk.Frame(self.cntlframe) 
		self.lrSave = tk.Frame(self.cntlframe)
		self.PCAlabel_frame = tk.Frame(self.cntlframe) 
		self.PCAFrame = tk.Frame(self.cntlframe); 
		self.PCAButtons = tk.Frame(self.cntlframe);
		self.PCAButtons2 = tk.Frame(self.cntlframe);
		#-------------------

		#Buttons
		#----------------------

		self.buttons_right = [] 	
		self.buttons_right.append(( 'Preform Clustering', tk.Button(self.openedButtonsClustering, text= "Create Cluster", command = self.handleAddCluster, width = 10) ) )
		self.buttons_right.append(( 'Plot Clustering', tk.Button(self.openedButtonsClustering, text= "Plot Clustering", command = self.handlePlotCluster, width = 10) ) )
		self.buttons_right.append(( 'Delete Clustering', tk.Button(self.underopenedButtonsClustering, text= "Delete Clustering", command = self.handleDeleteClusterEntry, width = 10) ) )
		self.buttons_right.append(( 'View Clustering', tk.Button(self.underopenedButtonsClustering, text= "View Clustering", command = self.handleShowCluster, width = 10) ) )
		self.buttons_right.append(( 'Silhouette Analysis', tk.Button(self.finalButtonsClustering, text= "Silhouette Analysis", command = self. handleSilhouetteAnalysis, width = 10) ) )

		#Buttons for central frame 
		self.buttons = []
		self.buttons.append( ( 'plotData', tk.Button(self.openedButtons, text= "Plot Data", command = self.handlePlotData, width = 10) ) )
		self.buttons.append( ( 'Reset view', tk.Button( self.underOpenedButtons, text="Reset view", command=self.handleResetButton, width=10 ) ) )
		self.buttons.append( ( 'Delete', tk.Button( self.openedButtons, text="Delete", command=self.handleDeleteEntry, width=10 ) ) )
		self.buttons.append( ( 'Save', tk.Button( self.lrSave, text="Save LR model", command=self.handleSaveLRModel, width=10 ) ) )
		self.buttons.append( ( 'Load', tk.Button( self.lrSave, text="Load LR model", command=self.handeloadLRmodel, width=10 ) ) )
		self.buttons.append( ( 'Preform PCA', tk.Button( self.PCAButtons, text="Preform PCA", command=self.handleAddPCA, width=10 ) ) )
		self.buttons.append( ( 'Project PCA', tk.Button( self.PCAButtons, text="Project PCA", command=self.handleProjectPCA, width=10 ) ) )
		self.buttons.append( ( 'Delete all', tk.Button( self.underOpenedButtons, text="Delete all", command=self.handleDeleteEverything, width=10 ) ) )
		self.buttons.append( ( 'Show PCA', tk.Button( self.PCAButtons2, text="Show PCA", command=self.handleShowPCA, width=10 ) ) )
		self.buttons.append( ( 'Delete PCA', tk.Button( self.PCAButtons2, text="Delete PCA", command=self.handleDeletePCAEntry, width=10 ) ) )

		#---------------------


		#Listboxes for right frame: 
		#---------------------------
		self.clusterListbox = tk.Listbox(self.clusterListboxFrame, selectmode = "multiple")

		#Listboxes for central frame 
		#--------------------
		self.dataOpened = tk.Listbox(self.lbFrame)
		self.dataOpened.bind('<<ListboxSelect>>', self.onselect)

		self.PCAbox = tk.Listbox(self.PCAFrame); 
		#--------------------

		#Labels

		#labels for right frame
		self.cluster_label = tk.Label(self.clusterLabelFrame, text = "------------------------\nCluster Analysis:\n------------------------")


		#labels for central frame
		#-------------------
		self.main_control = tk.Label( self.mainLabelFrame, text = "--------------------\nMain Control:\n--------------------")
		self.lr_label = tk.Label( self.lr_Frame, text = "----------------------------\nLinear Regression:\n----------------------------")
		self.pca_label = tk.Label( self.PCAlabel_frame, text = "--------------------\nPCA Analysis:\n--------------------")
		self.lr_r_squared = tk.Label( self.lrinfo1, text = "R_Squared: ?" )
		self.lr_intercept = tk.Label( self.lrinfo2, text = "Intercept: ?")
		self.lr_slope = tk.Label( self.lrinfo3, text = "Slope: ?")
		#-------------------

		#Packing:
		#------------------

		#packing right frame and its content. 
		self.rightFrame.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y)
		self.sep_right.pack(side=tk.LEFT, padx = 2, pady = 2, fill=tk.Y)
		self.clusterLabelFrame.pack(side = tk.TOP, fill = tk.X)
		self.clusterListboxFrame.pack(side = tk.TOP, fill = tk.X)
		self.openedButtonsClustering.pack(side=tk.TOP, fill=tk.X, pady = 4)
		self.underopenedButtonsClustering.pack(side=tk.TOP, fill=tk.X)
		self.finalButtonsClustering.pack(side=tk.TOP, fill=tk.X, pady=4)


		#packing cluster Label Frame content
		self.cluster_label.pack(side=tk.LEFT, fill = tk.BOTH)

		#packing cluster Listbox Frame content 
		self.clusterListbox.pack(side=tk.TOP,  fill=tk.BOTH)

		#packing opened buttons
		self.buttons_right[0][1].pack(side=tk.LEFT, fill=tk.BOTH)
		self.buttons_right[1][1].pack(side=tk.RIGHT, fill=tk.BOTH)

		#packing under opened buttons
		self.buttons_right[2][1].pack(side=tk.LEFT, fill=tk.BOTH)
		self.buttons_right[3][1].pack(side=tk.RIGHT, fill=tk.BOTH)

		#packing final layer buttons
		self.buttons_right[4][1].pack(side=tk.TOP, fill=tk.BOTH)

		#packing central frame and its content 
		self.cntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)
		self.sep.pack(side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)
		self.mainLabelFrame.pack(side = tk.TOP, fill = tk.X)
		self.lbFrame.pack(side=tk.TOP, fill=tk.X)
		self.openedButtons.pack(side=tk.TOP, fill=tk.X, pady = 4)
		self.underOpenedButtons.pack(side=tk.TOP, fill=tk.X)
		self.lr_Frame.pack(side=tk.TOP, fill=tk.X, pady = 6)
		self.lrinfo1.pack(side=tk.TOP, fill = tk.X, pady = 2)
		self.lrinfo2.pack(side=tk.TOP, fill = tk.X, pady = 2)
		self.lrinfo3.pack(side=tk.TOP, fill = tk.X, pady = 2)
		self.lrSave.pack(side=tk.TOP, fill=tk.BOTH, pady = 4)
		self.PCAlabel_frame.pack(side=tk.TOP, fill = tk.X, pady = 4)
		self.PCAFrame.pack(side=tk.TOP, fill=tk.BOTH)
		self.PCAButtons.pack(side=tk.TOP, fill=tk.BOTH, pady = 4)
		self.PCAButtons2.pack(side=tk.TOP, fill=tk.BOTH, pady = 4)

		
		#packing main control content
		self.main_control.pack(side=tk.LEFT, fill = tk.BOTH)

		#packing lbframe content
		self.dataOpened.pack(side=tk.TOP,  fill=tk.BOTH)
		
		#packing data opened content 
		self.buttons[0][1].pack(side=tk.LEFT, fill=tk.BOTH)
		self.buttons[2][1].pack(side=tk.RIGHT, fill=tk.BOTH)

		#packing data under opened content
		self.buttons[1][1].pack(side=tk.LEFT, fill=tk.BOTH) 
		self.buttons[7][1].pack(side=tk.RIGHT, fill=tk.BOTH) 

		#packing lr_Frame content
		self.lr_label.pack(side = tk.LEFT, fill = tk.BOTH)

		#packing lr_info content
		self.lr_r_squared.pack(side=tk.LEFT)
		self.lr_intercept.pack(side=tk.LEFT) 
		self.lr_slope.pack(side=tk.LEFT)

		#packing LRsave content 
		self.buttons[3][1].pack(side=tk.LEFT)
		self.buttons[4][1].pack(side=tk.RIGHT)

		self.pca_label.pack(side=tk.LEFT)

		#packing PCAFrame content 
		self.PCAbox.pack(side=tk.TOP,  fill=tk.BOTH)

		#packing PCAButtons content
		self.buttons[5][1].pack(side=tk.LEFT)
		self.buttons[6][1].pack(side=tk.RIGHT)

		#packing PCAButtons2 content 
		self.buttons[8][1].pack(side=tk.LEFT)
		self.buttons[9][1].pack(side=tk.RIGHT)
		#-----------------


		return

	#binding method for the listbox (opened data): 
	def onselect(self, event): 
		w = event.widget
		
		if (len(w.curselection()) == 0): 
			return 

		filename = w.get(int(w.curselection()[0]))

		if (filename not in self.lrResults):
			self.labelLR(0, filename)

		elif len(self.lrResults[filename]) == 0: 
			self.labelLR(0, filename)

		else: 
			self.labelLR(1, filename)


	#Builds the status bar and adds the two labels: X, Y (position of the mouse)
	def buildStatusBar(self): 
		downframe = tk.Frame(self.root)
		downframe.pack(side=tk.BOTTOM, padx=2, pady=2, fill=tk.X)

		# make a separator frame
		sep = tk.Frame( self.root, height=2, width=self.initDx, bd=1, relief=tk.SUNKEN )
		sep.pack( side=tk.BOTTOM, padx = 2, pady = 2, fill=tk.X)

		# use a label to set the size of the right panel
		self.scaleFactor = tk.StringVar()
		self.orientation = [tk.StringVar(), tk.StringVar()]  
		scale = tk.Label( downframe, textvariable=self.scaleFactor, width=20 )
		thetaUp = tk.Label( downframe, textvariable=self.orientation[0], width=20 )
		thetaU = tk.Label( downframe, textvariable=self.orientation[1], width=20 )
		self.scaleFactor.set("Scale: " + str(1))
		
		self.orientation[0].set("Horizental angle: 0.00")
		self.orientation[1].set("Vertical angle: 0.00")

		scale.pack(side = tk.LEFT)
		thetaUp.pack(side = tk.RIGHT)
		thetaU.pack(side = tk.RIGHT) 

		return

###############################################################################
# Axes / Points methods 														  
# Build and update methods for: 
# 	* Points
#	* Axes 			  
###############################################################################


	# create the axis line objects in their default location
	def buildAxes(self):
		vtm = self.view.build()

		pts = (vtm * self.axes.T).T

		self.lines.append(self.canvas.create_line(pts[0,0], pts[0,1], pts[1,0], pts[1,1]))
		self.lines.append(self.canvas.create_line(pts[0,0], pts[0,1], pts[2,0], pts[2,1]))
		self.lines.append(self.canvas.create_line(pts[0,0], pts[0,1], pts[3,0], pts[3,1]))

		self.xyz.append(self.canvas.create_text(pts[1, 0] + 10, pts[1, 1], text = 'X'))
		self.xyz.append(self.canvas.create_text(pts[2, 0] + 10, pts[2, 1], text = 'Y'))
		self.xyz.append(self.canvas.create_text(pts[3, 0] - 10, pts[3, 1], text = 'Z'))

		return 


	# modify the endpoints of the axes to their new location
	def updateAxes(self):  
		vtm = self.view.build()
		pts = (vtm * self.axes.T).T


		for i, line in enumerate(self.lines): 
			self.canvas.coords(line, pts[0,0], pts[0,1], pts[i+1,0], pts[i+1,1])

		self.canvas.coords(self.xyz[0], pts[1, 0] + 10, pts[1, 1])
		self.canvas.coords(self.xyz[1], pts[2, 0] + 10, pts[2, 1])
		self.canvas.coords(self.xyz[2], pts[3, 0] - 10, pts[3, 1])


	#Transform points to window view and plot them accordingly. 
	def buildPoints(self, headers, filename):
		

		if (headers[2] == None):
			data = ay.normalize_columns_separately(headers[:2], self.data[filename])
			data = np.append(data,np.zeros([len(data),1]),1)
			data = np.append(data,np.ones([len(data), 1]),1)
		
		else: 
			data = ay.normalize_columns_separately(headers[:3], self.data[filename])
			data = np.append(data,np.ones([len(data), 1]),1)

		self.current_data[filename] = data
		vtm = self.view.build() 
		pts = (vtm * data.T).T

		for i, pt in enumerate(pts):
			self.objects[filename].append(self.canvas.create_oval( pt[0,0] - self.sizes[filename][i], 
							pt[0,1] - self.sizes[filename][i], pt[0,0] + self.sizes[filename][i], 
							pt[0,1] + self.sizes[filename][i], fill=self.colors[filename][i]))


	#update the view of the points as a respone to change in view.
	def updatePoints(self):  

		if len(self.current_data) == 0:
			return

		for filename in self.current_data.keys(): 

			if (len(self.current_data[filename]) == 0):
				continue

			vtm = self.view.build()
			pts = (vtm * self.current_data[filename].T).T

			for i, pt in enumerate(self.objects[filename]): 
				self.canvas.coords(pt, pts[i,0] - self.sizes[filename][i], pts[i,1] - self.sizes[filename][i], 
					pts[i,0] + self.sizes[filename][i], pts[i,1] + self.sizes[filename][i])
				self.canvas.itemconfig(pt, fill = self.colors[filename][i])


###############################################################################
# All methods necessary for plotting the points of any data set: 														  
# - Generate colors and size in case of fourth or fifrth dimension. 
# - Generate Histo. 
# - Handle choosing the axes and plotting the points. 		  
###############################################################################


	#generate a distribution of colors that matches the range of data. 
	def generateColors(self, header, filename, PCAname, type):
		if header == None: 
			return 

		if (type == "non-PCA"): 
			dataColors = self.data[filename].get_LimitedHeaders([header])
			
		else: 
			dataColors = self.PCAanalysis[PCAname].get_LimitedHeaders([header])

		std = np.std(dataColors, 0)
		mean = np.mean(dataColors, 0)
		for i, data in enumerate(dataColors):
			#alpha = 1/(1 + np.exp(-self.B_sigmoid * (data[0,0] - median)))
			value = (data - mean)/std
			if value > 2: 
				value = 2
			if value < -2:
				value = -2
			value /= 4
			value += 0.5
			color = '#%02x%02x%02x' % (int(255*value), 0, 255 - int(255*value)) 
			self.colors[filename][i] = color

	#generate a distribution of sizes that matches the range of data. 
	def generateSizes(self, header, filename, analysis_name, type): 
		if header == None: 
			return 

		if (type == "non-PCA"): 
			dataSizes = self.data[filename].get_LimitedHeaders([header])

		elif (type == "PCA"): 
			dataSizes = self.PCAanalysis[analysis_name].get_LimitedHeaders([header])

		else: 
			dataSizes = self.ClusterAnalysis[analysis_name].get_LimitedHeaders([header])

		std = np.std(dataSizes, 0)
		mean = np.mean(dataSizes, 0)
		for i, data in enumerate(dataSizes):
			#alpha = 1/(1 + np.exp(-self.B_sigmoid * (data[0,0] - median)))
			value = (data[0,0] - mean[0,0])/std[0,0]
			if value > 2: 
				value = 2
			if value < -2:
				value = -2
			value /= 4
			value += 0.5

			self.sizes[filename][i] = int(value*self.sizeValue)

	#generate a histogram according to num_bins. 
	def generateHisto(self, header, numBins, filename): 
		if header == None:
			return 

		dataHisto = self.data[filename].get_LimitedHeaders([header])
		plt.hist(dataHisto, bins=numBins,edgecolor='black', linewidth=1.2)
		plt.ylabel(header)
		plt.show()

	#handles initializing the dialog the enables the user to choose relevant axes. 
	def handleChooseAxes(self, filename):
		Axesdialog = AxesDialog(self.root, self.data[filename].get_headers())
		if (Axesdialog.cancelled):
			return None

		return (Axesdialog.getResult(), Axesdialog.getNumHisto())

	#handles plotting the point after transforming them to view plane coords. 
	def handlePlotData(self): 

		if len(self.dataOpened.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a CSV file from the listbox first"
			)
			return

		filename = self.dataOpened.get(tk.ACTIVE)
		results = self.handleChooseAxes(filename)

		if results == None:
			return

		self.clean_plot(filename)


		headers = results[0]
		numBins = results[1]

		self.generateColors(headers[3],filename, None, "non-PCA")
		self.generateSizes(headers[4],filename, None, "non-PCA")
		self.buildPoints(headers[:3],filename)
		self.generateHisto(headers[5], numBins, filename)


######################################################################################
# All methods necessary for linear regression 									 	 #					  
# - handle linear regression: handle the process of chossing the right variables     #
# - build linear regression: preforms the actual process and correctly plot the data #
# - Load and save linear regression models. 										 #
######################################################################################

	# handles the process of linear regression by managing: 
	#	* choosing features.
	#	* updating axes, fits, and points. 
	#	* preforming linear regression. 
	def handleLinearRegression(self):
		if len(self.dataOpened.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a CSV file from the listbox first"
			)
			return None

		filename = self.dataOpened.get(tk.ACTIVE)

		LrDialog = LinearRgressionDialog(self.root, self.data[filename].get_headers())
		
		if (LrDialog.cancelled):
			return None

		self.clean_plot(filename)

		self.view.reset()
		wscale = self.canvasSizes[0]/self.initDx
		hscale = self.canvasSizes[1]/self.initDy
		self.view.update_screen(wscale, hscale)

		self.updateAxes()
		self.updatefits()
		self.updatePoints()

		self.buildLinearRegression(LrDialog.getResult(), filename)


	#builds a linear regression by:
	#	* preforming linear regression 
	#	* creating the line object. 
	#	* creating the relevant points objects. 
	#	* tranforming everything to view coords. 
	def buildLinearRegression(self, headers, filename):

		columns = ay.normalize_columns_separately(headers, self.data[filename])
		columns = np.column_stack((columns, np.zeros(columns.shape[0])))
		columns = np.column_stack((columns, np.ones(columns.shape[0])))
		
		self.current_data[filename] = columns
		
		vtm = self.view.build() 
		pts = (vtm * columns.T).T

		for i, pt in enumerate(pts):
			self.objects[filename].append(self.canvas.create_oval( pt[0,0] - self.sizes[filename][i], 
							pt[0,1] - self.sizes[filename][i], pt[0,0] + self.sizes[filename][i], 
							pt[0,1] + self.sizes[filename][i], fill=self.colors[filename][i]))

		m, b, r_value, p_value, std_err, xmin, xmax, ymin, ymax = ay.single_linear_regression(self.data[filename],
																	 headers[0], headers[1])

		self.lrResults[filename] = [m, b, r_value, [xmin, xmax, ymin, ymax], headers]
		self.labelLR(1, filename)


		firstPoint = ((xmin * m + b) - ymin)/(ymax - ymin)
		secondPoint = ((xmax * m + b) - ymin)/(ymax - ymin)

		points = np.matrix([ [0,firstPoint[0],0,1], 
		                  [1,secondPoint[0],0,1] ])

		self.lrPoints[filename] = points
		pts = (vtm * points.T).T
		self.lrObject[filename].append(self.canvas.create_line(pts[0,0], pts[0,1], pts[1,0], pts[1,1], fill = self.colors[filename][0], width = 2.0))
	
	#updates the linear regresion lines according to the view properities. 
	def updatefits(self):  

		if len(self.lrPoints) == 0:
			return


		vtm = self.view.build()

		for filename in self.lrPoints.keys(): 

			if (len(self.lrPoints[filename]) == 0):
				continue

			pts = (vtm * self.lrPoints[filename].T).T

			for line in self.lrObject[filename]: 
				self.canvas.coords(line, pts[0,0], pts[0,1], pts[1,0], pts[1,1])

	#organize changing the linear regression labels
	def labelLR(self, phase, filename): 
		if phase == 0: 
			self.lr_slope.config(text = "Slope: None")
			self.lr_intercept.config(text = "Intercept: None")
			self.lr_r_squared.config(text = "R_Squared: None")

		elif phase == 1: 
			self.lr_slope.config(text = "Slope:" + "{:15.2f}".format(self.lrResults[filename][0]) )
			self.lr_intercept.config(text = "Intercept: " + "{:8.2f}".format(self.lrResults[filename][1]) )
			self.lr_r_squared.config(text = "R_Squared: " + "{:6.2f}".format(self.lrResults[filename][2]))	

		else: 
			self.lr_slope.config(text = "Slope: None")
			self.lr_intercept.config(text = "Intercept: None")
			self.lr_r_squared.config(text = "R_Squared: None")


	#handle saving an LR model. 
	def handleSaveLRModel(self):
		if len(self.dataOpened.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a CSV file from the listbox first"
			)
			return

		filename = self.dataOpened.get(tk.ACTIVE)
		
		if len(self.lrObject[index]) == 0:
			tk.messagebox.showerror(
				"Missing LR model",
				"There is no LR Model currently related to the selected data"
			)
			return

		self.writeLRmodelCSV(filename)

	#handles loading a linear regression model. 
	def handeloadLRmodel(self):
		
		if len(self.dataOpened.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a CSV file from the listbox first"
			)
			return

		fn = self.dataOpened.get(tk.ACTIVE)
		filename = fn + "_LrModel.csv"
		final = [] 
		try: 
			with open(filename, 'r') as csvfile:
				results = csv.reader(csvfile, delimiter=',', quotechar='|')
				tmp = [] 
				for i, row in enumerate(results):
					if (i == 0): 
						tmp.append([row[1], row[2]])
					if (i == 1 or i == 2 or i == 3):
						tmp.append([float(row[1])])
					if (i == 4): 
						tmp.append([float(row[1]), float(row[2]), float(row[3]), float(row[4])])

				self.loadLRmodelCSV(tmp, fn)
		except: 
			tk.messagebox.showerror(
				"Missing file",
				"There is no matching model in your directory"
			)
			return


	#writes a linear regression model to a CSV
	def writeLRmodelCSV(self, fn): 
		
		filename = fn + "_LrModel.csv"

		with open(filename, 'w') as csvfile:
			
			results = csv.writer(csvfile, delimiter=',',
					quotechar='|', quoting=csv.QUOTE_MINIMAL)

			headers = ['Headers ', self.lrResults[fn][4][0], self.lrResults[fn][4][1]]
			results.writerow(headers)

			slope = ['Slope', self.lrResults[fn][0]] 
			results.writerow(slope)

			Intercept = ['Intercept', self.lrResults[fn][1]] 
			results.writerow(Intercept)

			R_Squared = ['R_Squared', self.lrResults[fn][2]]
			results.writerow(R_Squared)

			Points = ["Points", self.lrResults[fn][3][0][0], 
								self.lrResults[fn][3][1][0], 
								self.lrResults[fn][3][2][0],
								self.lrResults[fn][3][3][0]]
			
			results.writerow(Points)

	#loads and draw a CSV model. 
	def loadLRmodelCSV(self, results, filename): 
		
		self.clean_plot(filename)

		headers = [results[0][0], results[0][1]]

		columns = ay.normalize_columns_separately(headers, self.data[filename])
		columns = np.column_stack((columns, np.zeros(columns.shape[0])))
		columns = np.column_stack((columns, np.ones(columns.shape[0])))

		self.current_data[filename] = columns
		
		vtm = self.view.build() 
		pts = (vtm * columns.T).T

		for i, pt in enumerate(pts):
			self.objects[index].append(self.canvas.create_oval( pt[0,0] - self.sizes[filename][i], 
							pt[0,1] - self.sizes[filename][i], pt[0,0] + self.sizes[filename][i], 
							pt[0,1] + self.sizes[filename][i], fill=self.colors[filename][i]))



		m = results[1][0]
		b = results[2][0]
		r_2 = results[3][0]
		xmin = results[4][0]
		xmax = results[4][1]
		ymin = results[4][2]
		ymax = results[4][3]

		self.lrResults[filename] = [m, b, r_2, [xmin, xmax, ymin, ymax]]
		self.labelLR(1, filename)


		firstPoint = ((xmin * m + b) - ymin)/(ymax - ymin)
		secondPoint = ((xmax * m + b) - ymin)/(ymax - ymin)

		points = np.matrix([ [0,firstPoint,0,1], 
		                  [1,secondPoint,0,1] ])

		self.lrPoints[filename] = points
		pts = (vtm * points.T).T
		self.lrObject[filename].append(self.canvas.create_line(pts[0,0], pts[0,1], pts[1,0], pts[1,1]))



###############################################################################
# Methods for handling PCA Analaysis										  #	  
# - Methods for creating creating a PCA object 								  #
# - Methods for projecting the PCA on data points. 							  #
# - Methods for showing the PCA analysis values 							  #
###############################################################################

	# handles preforming PCA on a data set and storing information. 
	def handleAddPCA(self): 

		if len(self.dataOpened.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a CSV file from the listbox first"
			)
			return

		filename = self.dataOpened.get(tk.ACTIVE)
		dialog = PCADialog(self.root, self.data[filename].get_headers(), 0)

		if (dialog.cancelled):
			return None

		results = dialog.getResult()

		id = filename
		id = id + "_PCA_#" + str(random.randint(1000, 9999))

		self.PCAbox.insert("end", id)
		self.PCAanalysis[id] = ay.pca( self.data[filename], results, True )

	# handles projecting PCA on the data set and plotting the points. 
	def handleProjectPCA(self): 

		if len(self.PCAbox.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a PCA analysis from the listbox first"
			)
			return

		PCAname = self.PCAbox.get(self.PCAbox.curselection()[0])
		filename = PCAname.split("_")[0] 

		self.clean_plot(filename)

		dialog = PCADialog(self.root, self.PCAanalysis[PCAname].get_headers(), 1)
		if (dialog.cancelled):
			return None

		headers = dialog.getResult()

		if (len(headers) < 3):
			data = ay.normalize_columns_together(headers[:2], self.PCAanalysis[PCAname])
			data = np.append(data,np.zeros([len(data),1]),1)
			data = np.append(data,np.ones([len(data), 1]),1)
		
		else: 
			data = ay.normalize_columns_together(headers[:3], self.PCAanalysis[PCAname])
			data = np.append(data,np.ones([len(data), 1]),1)

		if (len(headers) > 3):
			self.generateColors(headers[3],filename, PCAname, "PCA")
		
		if (len(headers) > 4):
			self.generateSizes(headers[4],filename, PCAname, "PCA")

		self.current_data[filename] = data
		vtm = self.view.build() 
		pts = (vtm * data.T).T

		for i, pt in enumerate(pts):
			self.objects[filename].append(self.canvas.create_oval( pt[0,0] - self.sizes[filename][i], 
							pt[0,1] - self.sizes[filename][i], pt[0,0] + self.sizes[filename][i], 
							pt[0,1] + self.sizes[filename][i], fill=self.colors[filename][i]))


	# handles showing the PCA analysis values in a seperate dialog. 
	def handleShowPCA(self): 
		if len(self.PCAbox.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a PCA analysis from the listbox first"
			)
			return

		PCAname = self.PCAbox.get(self.PCAbox.curselection()[0])
		data = self.PCAanalysis[PCAname]
		eigenVectors = data.get_eigenvectors()
		eigenValues = data.get_eigenvalues()
		headers = data.get_headers()
		original_headers = data.get_original_headers()

		EigenDialog(self.root, headers, eigenValues, eigenVectors, original_headers)




###############################################################################
# Methods for handling Clustering Analaysis								      #	  
# - Methods for creating creating a Cluster object 						      #
# - Methods for plotting Cluster Analysis. 						  			  #
###############################################################################

	#adds a cluster analysis data object to its respective dictionary. 
	def handleAddCluster(self): 

		if len(self.dataOpened.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a CSV file from the listbox first"
			)
			return

		filename = self.dataOpened.get(tk.ACTIVE)
		dialog = ClusterDialog(self.root, self.data[filename].get_headers())

		if (dialog.cancelled):
			return None

		headers = dialog.getResult() 
		K = dialog.getK() 
		whiten = dialog.getWhiten() 
		distance = dialog.getDistance()

		if (whiten == 1):
			whiten = True

		else: 
			whiten = False


		id = filename
		id = id + "_Cluster_#" + str(random.randint(1000, 9999))
		
		self.clusterListbox.insert("end", id)
		self.ClusterAnalysis[id] = ay.kmeans(self.data[filename], headers, K, distance, whiten)
		self.computeQualityEstimateCluster(id)



	#assigns points their clusters colors.
	def generateColorsCluster(self, filename, codes, K): 	

		chosen_colors = random.sample(self.COLORS, K)
		D = codes.shape[0]
		for i in range(D): 
			self.colors[filename][i] = chosen_colors[int(codes[i, 0])]


	#computes the quality estimate of the clustering analysis
	def computeQualityEstimateCluster(self, filename): 
		
		d = self.ClusterAnalysis[filename]

		error = d.getErrors() 
		k = d.getK() 
		N = d.getN() 

		sum_squared = np.square(error)
		sum_total = np.sum(sum_squared) 
		addition = k/2 * (np.log2(N))
		final = sum_total + addition 

		return final


	#handles displaying the cluster information 
	def handleShowCluster(self): 
		if len(self.clusterListbox.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a Cluster analysis from the listbox first"
			)
			return

		Clustername = self.clusterListbox.get(self.clusterListbox.curselection()[0])
		d = self.ClusterAnalysis[Clustername]

		ClusterDataDialog(self.root, d.getCodeBooks(), d.getCodes(), d.getErrors(), 
						  self.computeQualityEstimateCluster(Clustername))


	#handles preforming Silhouette Analysis
	def handleSilhouetteAnalysis(self): 
		
		if len(self.clusterListbox.curselection()) < 2:
			tk.messagebox.showerror(
				"Not enough selections",
				"Please select at least 2 Cluster analysis from the listbox first"
			)
			return	

		selected = self.clusterListbox.curselection()
		
		Cluster_names = [self.clusterListbox.get(i) for i in selected]
		Cluster_data =  [self.ClusterAnalysis[name] for name in Cluster_names]
		
		K = [data.getK() for data in Cluster_data]
		results = [0 for i in range(len(Cluster_data))]
		
		for i, data in enumerate(Cluster_data):
			results[i] = ay.silhouette_average(data, data.get_headers(), data.getCodeBooks(), data.getCodes()) 

		plt.xlabel('K')
		plt.ylabel('Silhouette Average')

		plt.scatter(K, results)
		plt.plot(K, results)
		plt.show()

	# handles plotting the clustering analysis. 
	def handlePlotCluster(self): 

		if len(self.clusterListbox.curselection()) == 0:
			tk.messagebox.showerror(
				"Missing selections",
				"Please select a Cluster analysis from the listbox first"
			)
			return

		Clustername = self.clusterListbox.get(self.clusterListbox.curselection()[0])
		filename = Clustername.split("_")[0] 
		d = self.data[filename]
		d_cluster = self.ClusterAnalysis[Clustername]

		self.clean_plot(filename)

		dialog = ClusterAxesDialog(self.root, d.get_headers())
		
		if (dialog.cancelled):
			return None

		headers = dialog.getResult()


		if (headers[2] == None):
			data = ay.normalize_columns_separately(headers[:2], d)
			data = np.append(data,np.zeros([len(data),1]),1)
			data = np.append(data,np.ones([len(data), 1]),1)
		
		else: 
			data = ay.normalize_columns_separately(headers[:3], d)
			data = np.append(data,np.ones([len(data), 1]),1)
		

		if (headers[3] != None):
			self.generateSizes(headers[3],filename, Clustername, "Cluster")

		self.generateColorsCluster(filename, d_cluster.getCodes(), d_cluster.getCodeBooks().shape[0])

		self.current_data[filename] = data
		vtm = self.view.build() 
		pts = (vtm * data.T).T

		for i, pt in enumerate(pts):
			self.objects[filename].append(self.canvas.create_oval( pt[0,0] - self.sizes[filename][i], 
							pt[0,1] - self.sizes[filename][i], pt[0,0] + self.sizes[filename][i], 
							pt[0,1] + self.sizes[filename][i], fill=self.colors[filename][i]))




###############################################################################
# Bindings and their methods 												  #	  
# - Handle the mouse motion  												  #
# - Hnadle Keyboard shortucts												  #
###############################################################################

	# sets the bindings for shortucts, mouse motion. 
	def setBindings(self):
		self.root.bind( '<Button-1>', self.handleButton1 )
		self.root.bind( '<Button-2>', self.handleButton2 )
		self.root.bind( '<Button-3>', self.handleButton3 )
		self.root.bind( '<B1-Motion>', self.handleButton1Motion )
		self.root.bind( '<B2-Motion>', self.handleButton2Motion )
		self.root.bind( '<B3-Motion>', self.handleButton3Motion )
		self.root.bind( '<Control-q>', self.handleQuit )
		self.root.bind( '<Control-o>', self.handleModO )
		self.root.bind( '<Control-l>', self.handleLr )
		self.root.bind( '<Control-Button-1>', self.handleButton2 )
		self.root.bind( '<Control-B1-Motion>', self.handleButton2Motion )
		self.canvas.bind( '<Configure>', self.handleResize )
		return

	#handles preforming a resize process. 
	def handleResize(self, event=None):
		wscale = float(event.width)/self.initDx
		hscale = float(event.height)/self.initDy

		self.canvasSizes[0] = event.width 
		self.canvasSizes[1] = event.height

		self.view.update_screen(wscale, hscale)

		self.updateAxes()
		self.updatefits()
		self.updatePoints()

	#handles preforming a linear regression. 
	def handleLr(self, event):
		self.handleLinearRegression()

	#handles openning a new file. 
	def handleModO(self, event):
		self.handleOpen()

	# handles quitting the display. 
	def handleQuit(self, event=None):
		print('Terminating')
		self.root.destroy()

	# handles pressing the reset button that reset the view. 
	def handleResetButton(self):
		
		self.view.reset()

		wscale = self.canvasSizes[0]/self.initDx
		hscale = self.canvasSizes[1]/self.initDy

		self.view.update_screen(wscale, hscale)

		self.factor = 1 
		self.tempFactor = 1 
		self.thetas = [0, 0] 
		self.baseClick1 = [0, 0]
		self.baseClick2 = [0, 0]
		self.baseClick3 = [0, 0]

		self.updateAxes()
		self.updatefits()
		self.updatePoints()
		
		self.orientation[0].set("Horizental angle: {:0.2f}".format(self.thetas[0] + self.tempThetas[0]))
		self.orientation[1].set("Vertical angle: {:0.2f}".format(self.thetas[1] + self.tempThetas[1]))

		self.scaleFactor.set("Scale: {:0.2f}".format(1.0))


	#stores the basic clicks for panning 
	def handleButton1(self, event):


		self.baseClick1[0] = event.x
		self.baseClick1[1] = event.y

	# handles the base level of rotation. 
	def handleButton2(self, event):

		self.baseClick3[0] = event.x 
		self.baseClick3[1] = event.y 
		self.viewOrigin = self.view.cloneView() 

		self.thetas[0] += self.tempThetas[0]
		self.thetas[1] += self.tempThetas[1] 

		self.tempThetas = [0,0]


	# handles the base level of scaling. 
	def handleButton3(self, event):

		self.baseClick2[0] = event.x 
		self.baseClick2[1] = event.y 
		self.tempFactor = self.factor


	# handles panning while in process. 
	def handleButton1Motion(self, event):


		dx = event.x - self.baseClick1[0]
		dy = event.y - self.baseClick1[1]

		self.baseClick1[0] = event.x
		self.baseClick1[1] = event.y

		#calcuates the difference in vertical 
		#and horizental motion. 
		dx = dx/self.view.get_screenX() 
		dy = dy/self.view.get_screenY()

		dx = dx*self.view.get_extentX()
		dy = dy*self.view.get_extentY()

		#updates the vrp. 
		self.view.update_vrp_translate(dx, dy)

		#updates and redraw axes. 
		self.updateAxes()
		self.updatefits()
		self.updatePoints()

	#handles rotation
	def handleButton2Motion(self, event):
		

		dx = event.x - self.baseClick3[0]
		dy = event.y - self.baseClick3[1]

		#calculates the angles
		thetaUp = (-dx/(0.5*self.view.get_screenX()) *math.pi/3)
		thetaU =  (dy/(0.5*self.view.get_screenY()) *math.pi/3)

		self.tempThetas[0] = thetaUp*(180/math.pi)
		self.tempThetas[1] = thetaU*(180/math.pi)

		self.orientation[0].set("Horizental angle: {:0.2f}".format(self.thetas[0] + self.tempThetas[0]))
		self.orientation[1].set("Vertical angle: {:0.2f}".format(self.thetas[1] + self.tempThetas[1]))

		#updatet the view object 
		self.view = self.viewOrigin.cloneView() 
		self.view.update_vrc_rotate(thetaUp, thetaU)

		#update and redraw axes. 
		self.updateAxes()
		self.updatefits()
		self.updatePoints()

	# handles scaling. 
	def handleButton3Motion( self, event):


		#calculates the vertical differencec. 
		dy = event.y - self.baseClick2[1]

		#calculates the factor that controls the scaling
		#motion. 
		self.factor = self.tempFactor + (0.002*dy) 

		if self.factor > 3.0: 
		    self.factor = 3.0
		if self.factor < 0.1: 
		    self.factor = 0.1 

		self.scaleFactor.set("Scale: {:0.2f}".format(self.factor))

		#updates the extent
		self.view.update_extent_scale(self.factor)

		#updates and redraw the axes. 
		self.updateAxes()
		self.updatefits()
		self.updatePoints()

	def main(self):
		self.root.mainloop()


if __name__ == "__main__":
	dapp = DisplayApp(1280, 768)
	dapp.main()



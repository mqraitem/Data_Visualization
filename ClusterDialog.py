# Maan Qraitem 
# CS 251
# Project 6 

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


###############################################################################
# Dialog for matching data with axis. 	  
# - The dialog is called for the plot functionality. 
# 							  
###############################################################################

class ClusterDialog(tk.Toplevel):

	def __init__(self, parent, headers):

		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		self.title("Choose Clustering features")

		self.headers = headers

		self.cancelled = True

		self.parent = parent

		self.whitenornot = 0

		self.result = []

		self.K = 0

		self.distance = "L1"

		body = tk.Frame(self)
		self.initial_focus = self.body(body)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
									parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)


	def addHeaderListBox(self, listbox): 
		for header in self.headers:
			listbox.insert(tk.END, header)


	def getResult(self): 
		return self.result

	def getK(self): 
		return self.K

	def getWhiten(self): 
		return self.whitenornot

	def getDistance(self):
		return self.distance

	def whitencommand(self): 
		self.whitenornot = self.varCheck.get()

	def chooseDistance(self, value): 
		self.variable.set(value)


	#Builds the entry widget. 
	#Returns the widget to set it as initial focus. 
	def body(self, master):

		frame = tk.Frame(master)
		frame1 = tk.Frame(master)
		frame2 = tk.Frame(master)
		frame3 = tk.Frame(master)

		#frame one content. 
		self.label_features = tk.Label( frame, text="feautres", width=10 )
		self.listbox = tk.Listbox(frame, height = len(self.headers), selectmode='multiple',exportselection=0)
		self.addHeaderListBox(self.listbox)

		self.label_k = tk.Label(frame1, text="K number", width = 10)
		self.entryK = tk.Entry(frame1)
		
		self.label_whiten = tk.Label(frame2, text= "Whiten data", width = 10)
		self.varCheck = tk.IntVar()
		self.check = tk.Checkbutton(frame2, command = self.whitencommand, variable=self.varCheck)

		self.variable = tk.StringVar(master)
		self.variable.set("L1") # default value
		self.menu = tk.OptionMenu(frame3, self.variable, "L1", "L2", command = self.chooseDistance)
		self.label_distance = tk.Label(frame3, text = "distance", width = 10)

		frame.pack(pady = 5)
		frame1.pack(pady = 5,fill=tk.BOTH)
		frame2.pack(pady = 5, fill=tk.BOTH)
		frame3.pack(pady = 5, fill=tk.BOTH)

		#packing frame content 
		self.label_features.pack()
		self.listbox.pack(fill=tk.BOTH) 

		self.label_k.pack(side = tk.LEFT)
		self.entryK.pack(side = tk.LEFT)

		self.label_whiten.pack(side=tk.LEFT)
		self.check.pack(side=tk.LEFT)

		self.label_distance.pack(side=tk.LEFT)
		self.menu.pack(side=tk.LEFT)

		return self.listbox


    #Set up the standard (OK, Cancel) buttons. 
	def buttonbox(self):

		box = tk.Frame(self)

		w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	#Handles pressing the Ok button. 
	#if the inputs was validated: destroyes the window and call cancel/apply. 
	#otherwise, set the focus back to entry widget. 
	def ok(self, event=None):

		if not self.validate():
			self.initial_focus.focus_set() # put focus back
			return

		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()


	#destroys the dialog and reset the focus to parent window. 
	def cancel(self, event=None):

		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()


	def getSelections(self, listbox): 
		if len(listbox.curselection()) == 0: 
			return None 
		else:
			for i in listbox.curselection(): 
				self.result.append(self.headers[i])

	#Validates the input in the entry widget: 
	#if not integer or out of range --> returns 0 
	#Otherwise, returns 1. 
	def validate(self):
		if len(self.listbox.curselection()) == 0:
			tk.messagebox.showerror(
				"Not enough selections",
				"Please select at least one entry"
				)
			return 0

		try:
			self.K = int(self.entryK.get())
		except: 
			tk.messagebox.showerror(
				"Value Error",
				"You have entered an illegal value for your number of K"
				)
			return 0

		if self.K == 0: 
			tk.messagebox.showerror(
				"Value Error",
				"You can't have K = 0"
				)
			return 0

		self.distance = self.variable.get()

		return 1

    #The method is called after validate. 
    #Update the numPoints and cancelled fields accordingly.
	def apply(self):
		self.getSelections(self.listbox)
		self.cancelled = False


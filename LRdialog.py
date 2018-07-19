# Maan Qraitem 
# CS 251
# Project 6 


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



###############################################################################
# Dialog for matching data with linear regression features. 	  
# - The dialog is called for the linaer regression functionality functionality. 
# 							  
###############################################################################

class LinearRgressionDialog(tk.Toplevel):

	def __init__(self, parent, headers):

		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		self.title("Linear Regression")

		self.headers = headers

		self.cancelled = True

		self.parent = parent

		self.result = []

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

		self.binhisto = None


	def addHeaderListBox(self, listbox): 
		for header in self.headers:
			listbox.insert(tk.END, header)

	def getResult(self):
		return self.result

	def getNumHisto(self):
		return self.binhisto

	#Builds the entry widget. 
	#Returns the widget to set it as initial focus. 
	def body(self, master):

		frame1 = tk.Frame(master)
		frame2 = tk.Frame(master)

		self.listboxX = tk.Listbox(frame1, height = len(self.headers), exportselection = 0)
		self.listboxY = tk.Listbox(frame2, height = len(self.headers), exportselection = 0)

		self.addHeaderListBox(self.listboxX)
		self.addHeaderListBox(self.listboxY)

		frame1.grid(row = 0, column = 1) 
		frame2.grid(row = 0, column = 2) 

		tk.Label( frame1, text="Independant Variable", width=20 ).pack(side=tk.TOP)
		tk.Label( frame2, text="Dependant Variable", width=20 ).pack(side=tk.TOP)


		self.listboxX.pack(side = tk.BOTTOM) 
		self.listboxY.pack(side = tk.BOTTOM) 


		return self.listboxX


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
			return self.headers[listbox.curselection()[0]] 

	#Validates the input in the entry widget: 
	#if not integer or out of range --> returns 0 
	#Otherwise, returns 1. 
	def validate(self):
		if len(self.listboxX.curselection()) == 0 or len(self.listboxY.curselection()) == 0:
			tk.messagebox.showerror(
				"Not enough selections",
				"Please select at least a Dependant and Independant variables"
				)
			return 0
		return 1

    #The method is called after validate. 
    #Update the numPoints and cancelled fields accordingly.
	def apply(self):
		self.result.append(self.getSelections(self.listboxX))
		self.result.append(self.getSelections(self.listboxY))
		self.cancelled = False
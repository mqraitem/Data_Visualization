# Maan Qraitem 
# CS 251

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox



###############################################################################
# Dialog for matching data with axis. 	  
# - The dialog is called for the plot functionality. 
# 							  
###############################################################################

class PCADialog(tk.Toplevel):

	def __init__(self, parent, headers, choice):

		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		self.title("Choose PCA features")

		self.headers = headers

		self.cancelled = True

		self.parent = parent

		self.choice = choice

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

		frame = tk.Frame(master)

		#frame one content. 
		self.label_features = tk.Label( frame, text="feautres", width=20 )
		self.listbox = tk.Listbox(frame, height = len(self.headers), selectmode='multiple',exportselection=0)
		self.addHeaderListBox(self.listbox)

		frame.pack(pady = 5, fill = tk.BOTH)

		#packing frame content 
		self.label_features.pack()
		self.listbox.pack(fill=tk.BOTH) 

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

		if len(self.listbox.curselection()) > 5 and self.choice == 1:
			tk.messagebox.showerror(
				"Extra selections",
				"Please select only five entries"
				)
			return 0

		return 1

    #The method is called after validate. 
    #Update the numPoints and cancelled fields accordingly.
	def apply(self):
		self.getSelections(self.listbox)
		self.cancelled = False


import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


###############################################################################
# Dialog for matching data with axis. 	  
# - The dialog is called for the plot functionality. 
# 							  
###############################################################################

class EigenDialog(tk.Toplevel):

	def __init__(self, parent, headers, eigenValues, eigenVectors, original_headers):

		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		self.title("Choose Axes")

		self.headers = headers

		self.eigenVectors = eigenVectors

		self.eigenValues = eigenValues

		self.original_headers = original_headers

		self.numFeatures = eigenVectors.shape[0]

		self.numEigenVectors = eigenVectors.shape[1]

		self.cumulative = eigenValues/(np.sum(eigenValues))

		self.cancelled = True

		self.parent = parent

		self.result = []

		body = tk.Frame(self)
		self.body(body)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
									parent.winfo_rooty()+50))

		self.wait_window(self)

	def body(self, master):

		frame = tk.Frame(master)

		Labels = []

		Labels.append(tk.Label(frame, text= "E-vec", width=10 ).grid(row = 0, column = 0))
		for j in range(self.numFeatures): 
			Labels.append(tk.Label(frame, text= self.headers[j], width=10 ).grid(row = j + 1, column = 0))

		Labels.append(tk.Label(frame, text= "E-val", width=10 ).grid(row = 0, column = 1))
		for j in range(self.numFeatures): 
			Labels.append(tk.Label(frame, text= "{:0.4f}".format(self.eigenValues[j]), width=10 ).grid(row = j + 1, column = 1))

		Labels.append(tk.Label(frame, text= "Cumulative", width=10 ).grid(row = 0, column = 2))
		for j in range(self.numFeatures): 
			Labels.append(tk.Label(frame, text= "{:0.4f}".format(self.cumulative[j]), width=10 ).grid(row = j + 1, column = 2))

		for i in range(self.numEigenVectors): 
			Labels.append(tk.Label(frame, text= self.original_headers[i], width=10 ).grid(row = 0, column = i + 3))
			for j in range(self.numFeatures): 
				Labels.append(tk.Label(frame, text= "{:0.4f}".format(self.eigenVectors[j,i]), width=10 ).grid(row = j + 1, column = i + 3)) 

		frame.grid()


	def buttonbox(self):

		box = tk.Frame(self)

		w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	def ok(self, event=None):

		if not self.validate():
			self.initial_focus.focus_set() # put focus back
			return

		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()


	def cancel(self, event=None):

		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()

	def validate(self):
		return 1

	def apply(self):
		self.cancelled = False


from data import Data

class PCAData(Data):
	
	#initializes all the PCAData relevent fields. 
	def __init__(self, projected_data, eigenvectors, eigenvalues, original_means, data_headers):
		
		Data.__init__(self)
		self.data = projected_data
		self.eigenvalues = eigenvalues
		self.eigenvectors = eigenvectors
		self.original_means = original_means
		self.original_headers = data_headers  	
		self.organize_stuff()

	#fills out: 
	#	- the dictionary that maps headers to columns
	#	- the types list 
	#	- rows and cols 
	#	- headers names 
	def organize_stuff(self):
		
		self.rows = self.data.shape[0]
		self.cols = self.data.shape[1] 
		name = "PCA"

		for i in range(self.cols): 
			self.types.append("numeric")
			self.headers.append(name + str(i)) 
			self.header2col[self.headers[i]] = i; 

	#returns the eigenvalues
	def get_eigenvalues(self):
		return self.eigenvalues[:]

	#returns the eigenvectors
	def get_eigenvectors(self): 
		return self.eigenvectors[:]

	#returns the original means
	def get_original_means(self):
		return self.original_means[:]

	#returns the original headers
	def get_original_headers(self): 
		return self.original_headers[:]


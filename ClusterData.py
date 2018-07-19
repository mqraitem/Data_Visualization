#Maan Qraitem 
#Cluster Data class 



from data import Data

class ClusterData(Data): 

	def __init__(self, data, headers, codebooks, codes, errors): 

		Data.__init__(self)
		self.data = data
		self.headers = headers 
		self.codebooks = codebooks 
		self.codes = codes 
		self.errors = errors
		self.k = self.codebooks.shape[0]
		self.N = self.codes.shape[0]
		self.organize_stuff()

	def organize_stuff(self):
		
		self.rows = self.data.shape[0]
		self.cols = self.data.shape[1] 

		for i in range(self.cols): 
			self.types.append("numeric")
			self.header2col[self.headers[i]] = i; 


	def getCodeBooks(self): 
		return self.codebooks 

	def getCodes(self): 
		return self.codes 

	def getErrors(self): 
		return self.errors

	def getK(self): 
		return self.k

	def getN(self): 
		return self.N


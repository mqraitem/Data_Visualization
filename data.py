import numpy as np 
import csv
from datetime import datetime
from matplotlib.dates import num2date 
from matplotlib.dates import date2num

class Data: 

	def __init__(self, filename = None):
		self.headers = [] 
		self.types = []
		self.data = []
		self.rows = None 
		self.cols = None
		self.header2col = {} 
		self.enums = {}
		self.acceptedValues = ["numeric", "enum", "date"]
		if filename != None: 
			self.read(filename)

	def cleanLine(self, line):
		return [x.strip() for x in line]

	def buildHeader2col(self): 
		for i in range(len(self.headers)):
			if self.headers[i] not in self.header2col:
				self.header2col[self.headers[i]] = i

	def cleanData(self, line, row): 
		final = []

		for col in range(len(self.headers)):
			if self.types[col] == "numeric":
				final.append(float(line[col]))
			
			elif self.types[col] == "enum":
				if (line[col] not in self.enums):
					self.enums[line[col]] = float(row)
					final.append(row)
				else:
					final.append(self.enums[line[col]])
			
			elif self.types[col] == "date":
				if "/" in line[col]:
					date = datetime.strptime(line[col], '%m/%d/%y')
					final.append(date2num(date))
				
				elif "-" in line[col]:
					date = datetime.strptime(line[col], '%m-%d-%y')
					final.append(date2num(date))
				else: 
					print("Unsupported date")
					quit()

		return final


	def cleanTypesHeaders(self):
		skip = [True if x in self.acceptedValues else False for x in self.types]
		self.types = [x for x in self.types if x in self.acceptedValues]
		self.headers = [self.headers[x] for x in range(len(self.headers)) if skip[x]]


	def read(self, filename): 
		with open(filename, 'rU') as fp:
			reader = csv.reader(fp)
			linesNum = 0 
			skip = []
			#Reading the file
			for line in reader: 
				line = self.cleanLine(line)
				#Reading the headers
				if linesNum == 0: 
					self.headers = line[:]
				#Reading the types
				elif linesNum == 1:
					self.types = line[:]
				#Reading the data
				else:
					self.data.append(self.cleanData(line, linesNum - 2))
				linesNum += 1

			self.cleanTypesHeaders()
			self.rows = len(self.data) 
			self.cols = len(self.headers)
			self.buildHeader2col()
			self.data = np.matrix(self.data)

	def get_LimitedHeaders(self, headersList):
		extracted = [ self.header2col[header] for header in headersList
					if header in self.headers ]

		return self.data[:, extracted]

	def updateParams(self, header, type): 
		self.headers.append(header)
		self.types.append(type)
		self.cols += 1 
		self.buildHeader2col()


	def getData(self): 
		temp = np.copy(self.data)
		return np.hstack((temp,np.ones((temp.shape[0],1))))
		
	def addColumn(self, header, type, data):

		if (len(data) == self.rows):
			if type == "numeric":
				self.updateParams(header, type)
				self.data = np.hstack((self.data,np.matrix([float(i) for i in data]).reshape(self.rows, 1)))

			elif type == "enum":
				self.updateParams(header, type)
				final = []
				for i in range(len(data)):
					if data[i] not in self.enums:
						self.enums[data[i]] = i
						final.append(i) 
					else:
						final.append(self.enums[data[i]])
				self.data = np.hstack((self.data, np.matrix(final).reshape(self.rows, 1)))


			elif type == "date":
				final = [] 
				self.updateParams(header, type)
				for date in data: 
					if "/" in date:
						temp = datetime.strptime(date, '%m/%d/%y')
						final.append(date2num(temp))

					elif "-" in line[col]:
						temp = datetime.strptime(date, '%m-%d-%y')
						final.append(date2num(temp))
					else: 
						print("Unsupported date")
						quit()

				self.data = np.hstack((self.data, np.matrix(final).reshape(self.rows, 1)))


			else:
				print("Unsupported data value")
				quit()
		else:
			print("Incorrect number of rows")
			quit()

	def get_headers(self): 
		return self.headers 

	def get_types(self): 
		return self.types

	def get_num_dimensions(self): 
		return self.cols 

	def get_num_points(self): 
		return self.rows 

	def get_row(self, rowIndex):
		return self.data[rowIndex, :]

	def get_value(self, header, rowIndex):
		return self.data[rowIndex, self.header2col[header]]

	def __str__(self): 

		data = ""

		data += 'Number of rows:    ' + str(self.get_num_points()) + "\n"
		data += 'Number of columns: ' + str(self.get_num_dimensions()) + "\n"

		# print out the headers
		data += "\nHeaders:\n"
		headers = self.get_headers()
		data += headers[0]
		for header in headers[1:]:
		    data += ", " + header

		data += "\n"
		# print out the types
		data += "\nTypes\n"
		types = self.get_types()
		data += types[0]
		for type in types[1:]:
		    data += ", " + type

		data += "\n"

		data += "\nData\n"
		if (self.get_num_points() > 5):
			nums = 5
		else:
			nums = self.get_num_points() 
		for i in range(nums):
			data += "%0.3f" % (self.get_value( self.headers[0], i ))
			for j in range(self.get_num_dimensions())[1:]:
				if (self.types[j] == "date"):
					date = num2date(self.get_value( self.headers[j], i ))
					data += "\t"
					data += date.strftime('%m/%d/%Y')
				else:
					data += "%15.3f" % (self.get_value( self.headers[j], i ))
			data += "\n"
	
		return data






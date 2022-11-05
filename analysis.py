import numpy as np 
from scipy import stats
import scipy.cluster.vq as vq
import data 
import PCAData
import ClusterData
import random as rand
import math

def data_range(headers, data):
	extracted = data.get_LimitedHeaders(headers)
	Allmin = extracted.min(axis = 0)
	Allmax = extracted.max(axis = 0)
	final = [[Allmin[0, i], Allmax[0, i]] for i in range(Allmin.shape[1])]
	return final

def mean(headers, data): 
	extracted = data.get_LimitedHeaders(headers)
	return [x[0, 0] for x in np.mean(extracted, axis = 0).T]

def stdev(headers, data): 
	extracted = data.get_LimitedHeaders(headers)
	return [x[0, 0] for x in np.std(extracted, axis = 0).T]

def normalize_columns_separately(headers, data):
	extracted = data.get_LimitedHeaders(headers)
	extracted = extracted - extracted.min(axis = 0)
	extracted = extracted/(extracted.max(axis = 0))
	return extracted

def normalize_columns_together(headers, data):
	extracted = data.get_LimitedHeaders(headers)
	extracted = extracted - np.amin(extracted)
	extracted = np.divide(extracted, np.amax(extracted))
	return extracted

def median(headers, data):
	extracted = data.get_LimitedHeaders(headers)
	return np.median(extracted, axis = 0) 

def get_range(headers, data):
	extracted = data.get_LimitedHeaders(headers)
	return np.ptp(extracted,axis=0)

def single_linear_regression(data_obj, ind_var, dep_var):
	X = np.array(data_obj.get_LimitedHeaders([ind_var]))
	Y = np.array(data_obj.get_LimitedHeaders([dep_var]))
	slope, intercept, r_value, p_value, std_err = stats.linregress(X.reshape(X.shape[0]), Y.reshape(X.shape[0]))	
	return (slope, intercept, r_value, p_value, std_err, X.min(axis = 0), X.max(axis = 0), Y.min(axis = 0), Y.max(axis = 0))

def linear_regression(data_obj, ind, dep):

	y = data_obj.get_LimitedHeaders([dep])
	A = data_obj.get_LimitedHeaders(ind)

	A = np.column_stack((A, np.ones(A.shape[0])))

	AAinv = np.linalg.inv(np.dot(A.T, A))

	x = np.linalg.lstsq(A, y)

	b = x[0] 
	N = y.shape[0]
	C = b.shape[0]
	df_e = N - C
	df_r = C - 1 
	error = y - np.dot(A, b)
	sse = np.dot(error.T, error) / df_e
	stderr = np.sqrt(np.diagonal(sse[0,0] * AAinv))
	t = b.T / stderr
	p = 2 * (1 - stats.t.cdf(abs(t), df_e))
	r2 = 1 - error.var() / y.var()
	
	return (b, sse, r2, t, p)



def pca(d, headers, normalize=True):
	'''Calculates the PCA for the selected headers.'''
	if normalize:
		A = normalize_columns_separately(headers, d)

	else: 
		A = d.get_LimitedHeaders(headers) 

	print(A)

	m = np.mean(A, axis = 0) 
	D = A - m 
	U, S, V = np.linalg.svd(D, full_matrices = False)
	eigenvalues = np.square(S) / (A.shape[0] - 1)
	projected_data = ((V) * (D.T)).T

	return PCAData.PCAData(projected_data, V, eigenvalues, m, headers)

def kmeans_numpy( d, headers, K, whiten = True):
	'''computes the kmeans clutser and represent that by returning codebook, codes, and representation error.'''

	A = d.get_LimitedHeaders(headers)
	W = vq.whiten(A)

	codebook, bookerror = vq.kmeans(W, K) 
	codes, error = vq.vq(W, codebook) 

	return codebook, codes, error


def kmeans_init(A, K):

	pickfrom = A[:]
	picks = [] 
	final = np.zeros((K, A.shape[1]))

	if (A.shape[0] < K):
		print("Your data doesn't have enough data points")
		return 

	while len(picks) != K: 
		pick = rand.randint(0, A.shape[0] - 1) 
		if (pick not in picks): 
			final[len(picks)] = pickfrom[pick, :]
			picks.append(pick) 

	return(final)

def L2_distance(codebook, A): 
	diff = codebook - A
	squared = np.square(diff) 
	summed = np.sum(squared, axis = 1)
	square_root = np.sqrt(summed)
	return square_root

def L1_distance(codebook, A): 
	diff = np.abs(codebook - A)
	summed = np.sum(diff, axis = 1)
	return summed

def compute_ai(A, Point_index, codes):
	indices = [i for i, x in enumerate(codes) if int(x) == int(codes[Point_index])]
	a_i = 0 
	
	for index in indices:
		a_i += L2_distance(A[Point_index, :], A[index, :])[0,0]
	
	return (a_i/len(indices))

def compute_bi(A, Point_index, codes, codebook): 

	distance = L2_distance(codebook, A[Point_index,:]) 
	min_val = math.inf
	smallest_index = 0
	for j, row in enumerate(distance): 
		if (row[0] < min_val and j != int(codes[Point_index])):
			min_val = row[0]
			smallest_index = j

	indices = [i for i, x in enumerate(codes) if int(x) == smallest_index]
	b_i = 0

	for index in indices:
		b_i += L2_distance(A[Point_index, :], A[index, :])[0,0]
	return (b_i/len(indices))


def silhouette_average(d, headers, codebook, codes):
	A = d.get_LimitedHeaders(headers)
	N = A.shape[0]
	final = 0 
	newCodes = codes.reshape(codes.shape[0]).tolist()
	for i in range(N): 
		a_i = compute_ai(A, i, codes)
		b_i = compute_bi(A, i, codes, codebook)
		final += (b_i - a_i)/(max(b_i, a_i))

	return final/N

def kmeans_classify(A, codebook, measure):

	distances = np.zeros((A.shape[0], codebook.shape[0]))
	ids = np.zeros((A.shape[0], 1))
	distances = np.zeros((A.shape[0], 1))

	for i in range(A.shape[0]): 

		if (measure == "L1"):
			distance = L1_distance(codebook, A[i,:])
		
		elif (measure == "L2"):
			distance = L2_distance(codebook, A[i,:]) 

		ids[i, 0] = np.argmin(distance)
		distances[i, 0] = np.min(distance)

	return (ids, distances)

def kmeans_algorithm(A, means, measure):

	MIN_CHANGE = 1e-7     
	MAX_ITERATIONS = 100  
	D = means.shape[1]    # number of dimensions
	K = means.shape[0]    # number of clusters
	N = A.shape[0]        # number of data points

	# iterate no more than MAX_ITERATIONS
	for i in range(MAX_ITERATIONS): 

		codes, distances = kmeans_classify(A, means, measure)
		
		newmeans = np.zeros((K, D))
		counts = np.zeros((K, 1))
		A = np.array(A)

		for num in range(N): 
			newmeans[int(codes[num, 0]), :] += A[num,:]
			counts[int(codes[num, 0]), 0] += 1 

		for num in range(K): 
			if counts[num, 0] != 0:
				newmeans[num] /= counts[num, 0] 
			else:
				newmeans[num] = A[rand.randint(0, A.shape[0]), :]

		diff = np.sum(np.square(means - newmeans))
		means = newmeans
		if diff < MIN_CHANGE:
			break

	codes, errors = kmeans_classify( A, means, measure )

	# return the means, codes, and errors
	return (means, codes, errors)

def kmeans(d, headers, K, measure, whiten=True):
	'''Takes in a Data object, a set of headers, and the number of clusters to create
	Computes and returns the codebook, codes and representation errors. 
	'''

	A = d.get_LimitedHeaders(headers)
	
	if whiten: 
		W = vq.whiten(A)
	else:
		W = A 

	codebook = kmeans_init(W, K) 

	codebook, codes, errors = kmeans_algorithm(W, codebook, measure) 

	return ClusterData.ClusterData(d.get_LimitedHeaders(headers), headers, codebook, codes, errors)

   
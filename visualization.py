import numpy as np
import tensorflow as tf
import weightedmatrix as wm
import matplotlib.pyplot as plt

NUM_HIDDEN_UNITS = 1000;
NUM_OUTPUT_UNITS = 10;
BATCH_SIZE = 500;
NUM_ITERATIONS = 200;
NUM_PIXELS = 784
LAMDA = 0.0003
BEST_LEARNING_RATE = 0.0001
HIDDEN_UNIT_OPTIONS = [500]
KEEP_RATE = 0.5 

if __name__ == "__main__":

	with np.load("notMNIST.npz") as data:
		Data, Target = data ["images"], data["labels"]
		np.random.seed(521)
		randIndx = np.arange(len(Data))
		np.random.shuffle(randIndx)
		Data = Data[randIndx]/255.
		Target = Target[randIndx]
		trainData, trainTarget = Data[:15000], Target[:15000]
		validData, validTarget = Data[15000:16000], Target[15000:16000]
		testData, testTarget = Data[16000:], Target[16000:] 

	###setting up lists to store error

	#store cross entropy error
	crossTrainVals = []
	crossValidVals = [] 
	crossTestVals = []

	#store minimum value to detect early stopping
	minCrossTrain = 9999
	minCrossValid = 9999
	minCrossTest = 9999

	#store classifcation error
	#classTrainVals = []
	#classValidVals = []
	#classTestVals = [] 

	#store min value for early stopping
	#minClassTrain = 9999
	#minClassValid = 9999
	#minClassTest = 9999



	start = 0;


	###setting up tf's graph

	#reset graph to start from blank
	tf.reset_default_graph()

	#current hidden units
	numHiddenUnits = 1000 

	#format data
	numTrainingPoints = trainData.shape[0]

	trainX = np.reshape(trainData, (trainData.shape[0], -1) );
	trainY = trainTarget.astype(np.float64);

	num_batches = trainX.shape[0] // BATCH_SIZE

	validX = np.reshape(validData, (validData.shape[0], -1) );
	validY = validTarget.astype(np.float64);    

	testX = np.reshape(testData, (testData.shape[0], -1) );
	testY = testTarget.astype(np.float64); 

	#input layer
	x0 = tf.placeholder(tf.float64, name="input_layer", shape = [None, NUM_PIXELS]);
	#target values for input
	y = tf.placeholder(tf.int64, name="target");

	#one hot enncoding for softmax
	faty = tf.one_hot(indices = y, depth = 10);

	#hidden layer1
	[w1, b1, s1] = wm.weighted_matrix(x0, numHiddenUnits);
	

	x1 = tf.nn.relu(s1);
	x1Drop = tf.nn.dropout(x1, KEEP_RATE);

	[w2, b2, s2] = wm.weighted_matrix(x1, NUM_OUTPUT_UNITS);
	print(tf.shape(w2))
	[w2d, b2d, s2d] = wm.weighted_matrix(x1Drop, NUM_OUTPUT_UNITS);

	yhat = s2
	yhatDrop = s2d
    
	#error
	cross = tf.nn.softmax_cross_entropy_with_logits(logits = yhat, labels = faty);
	weightDecay = (tf.reduce_sum(w1**2) + tf.reduce_sum(w2**2) )*(LAMDA)    
	crossDrop = tf.nn.softmax_cross_entropy_with_logits(logits = yhatDrop, labels = faty);

	lossDrop = tf.reduce_mean((crossDrop + weightDecay)/2.0)
	loss = tf.reduce_mean((cross + weightDecay)/2.0)

	#misclassification = tf.reduce_mean( tf.cast(tf.not_equal(tf.argmax(yhat,axis=1), y), tf.float64) )

	learningRate = BEST_LEARNING_RATE
	descendGradient = tf.train.AdamOptimizer(learningRate).minimize(lossDrop);

	#initializer has to be done after declaring adam optimizer
	initializer = tf.global_variables_initializer();

	###gradient descent
	count = 0
	with tf.Session() as sess:
		sess.run(initializer)
		
		for i in range(NUM_ITERATIONS): 

			end = start + BATCH_SIZE;
			sess.run(descendGradient, feed_dict={x0:  trainX[start:end], y: trainY[start: end]})
			w1matrix = np.array(sess.run(w1))
#			print("Shape of w1 matrix")
#			print(sess.run(w1).shape)
#			print ("Shape of w2 matrix")
#			print(sess.run(w2).shape)
#			print("w2d ")
#			print(sess.run(w2d).shape)
#			print(w1matrix.shape) #784x500
			w1matrix = w1matrix[:,:100]
			#print("Shape")
			#print(w1matrix.shape)
			w1matrix = np.reshape(np.transpose(w1matrix), (100,28,28))
			#print(w1matrix.shape)#100x28x28
			w1matrix = tf.convert_to_tensor(w1matrix)#100x28x28
			#print(w1matrix.shape)

			w1matrix = tf.unstack(w1matrix) #unstacks it into a list of 28 x 28 images
			#w1matrix = tf.convert_to_tensor(w1matrix)
			#print(w1matrix.shape)
			#w1matrix = tf.concat (w1matrix,axis = 1) #now a single row of 28*28*100 
			#print(w1matrix.shape)
			#w1matrix = tf.split(w1matrix,10)#split this into 10 rows
			#w1matrix = tf.convert_to_tensor(w1matrix)	#this is (10,10,28,28)
			#print(w1matrix.shape)

			if (i== 0.25*NUM_ITERATIONS):
				weightM = sess.run(w1matrix)
				weightMatrix25 = np.array(weightM)
				print(weightMatrix25.shape)
				print("Reached")


			if (i == NUM_ITERATIONS-1):
				weightM = sess.run(w1matrix)
				weightMatrix100 = np.array(weightM)


			if( ((i+1)% num_batches) == 0):
				print(i)


				#get cross entropy loss values
				trainCross = sess.run(loss, feed_dict={x0:  trainX, y: trainY })
				validCross = sess.run(loss, feed_dict={x0: validX , y: validY })
				testCross = sess.run(loss, feed_dict={x0: testX , y: testY })              

				minCrossTrain = min(minCrossTrain, trainCross)
				minCrossValid = min(minCrossValid, validCross)
				minCrossTest = min(minCrossTest, testCross)

				crossTrainVals.append(trainCross)
				crossValidVals.append(validCross)
				crossTestVals.append(testCross)


				count = count + 1

		        
				#get classification error values
				#trainClass = sess.run(misclassification, feed_dict ={x0: trainX, y:  trainY})
				#validClass = sess.run(misclassification, feed_dict ={x0: validX, y:  validY})
				#testClass = sess.run(misclassification, feed_dict ={x0: testX, y:  testY})

				#minClassTrain = min(minClassTrain, trainClass)
				#minClassValid = min(minClassValid, validClass)
				#minClassTest = min(minClassTest, testClass)

				#classTrainVals.append(trainClass)
				#classValidVals.append(validClass)
				#classTestVals.append(testClass)

				#increment batch
				start = end % numTrainingPoints
        

	###plotting

	#get list of numbers from 0 to num iterations
	xVals = np.arange(len(crossTrainVals));

	print("hidden units  = " + str(numHiddenUnits))

	print("minimum cross Train was " + str(minCrossTrain))
	print("minimum cross Valid  was " + str(minCrossValid))
	print("minimum cross Test was " + str(minCrossTest))

	#print("minimum class Train was " + str(minClassTrain))
	#print("minimum class Valid was " + str(minClassTrain))
	#print("minimum class Test was " + str(minClassTrain))

	plt.plot(xVals, crossTrainVals, label= "training pts" )        
	plt.plot(xVals, crossValidVals, label= "validation pts" )
	plt.plot(xVals, crossTestVals, label="test points")

	plt.xlabel('Epoch #');
	plt.ylabel('Loss');
	plt.legend();
	plt.title("Cross Entropy Loss vs Num Epochs with HU = " + str(numHiddenUnits) )

	#plt.show() 

	
	fig=plt.figure(figsize=(12, 12))
	columns = 10
	rows = 10
	
	for i in range(1, columns*rows +1):

		fig.add_subplot(rows, columns, i)
		plt.imshow(weightMatrix100[i-1], cmap = 'gray')
	plt.show()

	#for i in range(9):
	#	for j in range(9):
	#		plt.subplot(28,28,1+i)
	#		plt.imshow(weightMatrix25[i][j], cmap = 'gray')
	#plt.show()
	#plt.imshow(weightMatrix100[1][1], cmap = 'gray')
	#plt.show()

	#plt.imshow(weightMatrix25, cmap = 'gray')
	#plt.show()
	#plt.imshow(weightMatrix100, cmap = 'gray')
	#plt.show()

	#plt.figure()

	#plt.plot(xVals, classTrainVals, label="training pts" )
	#plt.plot(xVals, classValidVals, label="validation pts" )
	#plt.plot(xVals, classTestVals, label="test points")

	#plt.xlabel('Epoch #');
	#plt.ylabel('Classification Error');
	#plt.legend();
	#plt.title("Classification Error vs Num Epochs with HU = " + str(numHiddenUnits))

#plt.show()

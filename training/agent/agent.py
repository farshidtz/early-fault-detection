"""
Training / Prediction Agent
"""

import numpy as np
import random
import matplotlib.pyplot as plt
import json
import time
from sklearn.externals import joblib
from os import path
from _converter import SensorThings2Dict
from _evaluation import print_metrics
import _models


class Agent(object):

    def build(self, classifier):
        print("agent.build: %s" % classifier)
        self.clf_name = classifier["name"]
        self.clf_conf = classifier["conf"]
        self.model_dir = ""
        if "dir" in classifier:
            self.model_dir = classifier["dir"]
            if path.isfile(self.model_dir+'/model.pkl'):
                self.clf = joblib.load(self.model_dir+'/model.pkl')
                self.means = joblib.load(self.model_dir+'/means.pkl')
                print("Loaded pre-trained model from disk.")
                return

        # construct the classifier
        self.clf = getattr(_models, self.clf_name)(self.clf_conf)
        print("Built a new %s classifier" % self.clf_name)

        self.pre_train(["C:/Users/Farshid/Desktop/thesis/early-fault-detection/training/agent/ABU1.txt"])

        self.corrects = 0
        self.wrongs = 0
        # return self.clf

    def pre_train(self, training_files):
        print("agent.pre_train: %s" % training_files)
        data = []
        bad = 0
        for filename in training_files:
            if not path.exists(filename):
                print("File does not exist: %s" % filename)
                continue
            print("Loading rows... {}".format(filename))
            with open(filename) as f:
                for line in f:
                    try:
                        features = SensorThings2Dict(json.loads(line))
                        data.append(list(features.values()))
                    except Exception, e:
                        # print(e)
                        bad+=1

        print("Incomplete rows: {}".format(bad))
        print("Loaded: {}".format(len(data)))

        """ random split seed """
        data = np.asarray(data)
        mask = np.random.rand(len(data)) < 0.9

        """ split into train and test sets """
        train = data[mask]
        test = data[~mask]
        print("Train Total: {} Good: {} Faulty: {} Ratio: {}".format(len(train), len(train[train[:,-1]=='True']), len(train[train[:,-1]=='False']), float(len(train[train[:,-1]=='False']))/len(train)))
        print("Test  Total: {} Good: {} Faulty: {} Ratio: {}".format(len(test), len(test[test[:,-1]=='True']), len(test[test[:,-1]=='False']), float(len(test[test[:,-1]=='False']))/len(train)))

        faulty = train[train[:,-1]=='False']
        not_faulty = train[train[:,-1]=='True']

        self.means = np.mean(not_faulty[:,2:-1].astype(np.float32), axis=0)
        # save means to disk
        joblib.dump(self.means, self.model_dir+'/means.pkl')

        """ down/up sample data """
        samples = np.random.choice(len(not_faulty), 5000, replace=False)
        train = np.concatenate((not_faulty[samples], faulty))
        print("Train Total: {} Good: {} Faulty: {} Ratio: {}".format(len(train), len(train[train[:,-1]=='True']), len(train[train[:,-1]=='False']), float(len(train[train[:,-1]=='False']))/len(train)))

        train_data = train[:,2:-1].astype(np.float32)
        test_data = test[:,2:-1].astype(np.float32)
        """
        Quality_OK is mapped to Faultiness
            'False' -> 1 (Faulty)
            'True'  -> 0 (Good)
        """
        train_labels = np.array(train[:,-1]=='False').astype(np.int32)
        test_labels = np.array(test[:,-1]=='False').astype(np.int32)

        """ train model """
        self.clf = self.clf.fit(train_data, train_labels)
        print_metrics(train_labels, self.clf.predict(train_data))
        print_metrics(test_labels, self.clf.predict(test_data))

        # save model to disk
        joblib.dump(self.clf, self.model_dir+'/model.pkl')

    def learn(self, datapoint):
        # print("agent.learn: %s" % datapoint)
        return

    def predict(self, datapoint):
        print("agent.predict: %s" % datapoint)
        return 1

        features = SensorThings2Dict(datapoint, complete=False)
        features = np.array(features.values())
        # convert measurements to numpy array
        r = features[2:-1].astype(np.float32)
        # fill nans with global means
        w = np.where(np.isnan(r))
        r[w] = self.means[w]
        start_time = time.time()
        p = self.clf.predict(r.reshape(1, -1))[0]
        elapsed_time = time.time() - start_time
        #print("Prediction: {} in {}s".format(p, elapsed_time))

        # functional test is done
        if features[-1] != None:
            label = np.array(features[-1]=='False').astype(np.int)
            if label != p:
                self.wrongs += 1
                print("WRONG PREDICTION. Predicted {} Label was {} -- {} / {}".format(p, label, self.wrongs, self.corrects))
            else:
                self.corrects += 1
                print("CORRECT -- {} / {}".format(self.corrects, self.corrects+self.wrongs))

        return {'prediction': p.item()}

    def batchLearn(self, datapoints):
        # print("agent.learn: %s" % datapoint)
        return

    def batchPredict(self, datapoints):
        return np.ones(len(datapoints)).astype(int).tolist()

    def destroy(self):
        print("agent.learn")

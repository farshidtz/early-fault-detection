"""
Training / Prediction Agent
"""

import numpy as np
import random, json, time, thread, threading, logging, traceback
from scipy.stats import logistic
from collections import deque
from sklearn.externals import joblib
from copy import deepcopy
from os import path, makedirs
from _converter import SensorThings2Dict, Event2Dict, validate
from _evaluation import print_metrics
import _models

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

"""
Quality_OK is mapped to Faultiness
    'False' -> 1 (Faulty)
    'True'  -> 0 (Good)
"""
_false = "false"
_true = "true"

class Agent(object):

    def build(self, classifier):
        logger.info("agent.build: %s" % classifier)
        self.loadParameters(classifier)
        self.fitted = False
        self.data = deque([], maxlen=20000)
        self.lock = threading.Lock()

        if not path.exists(self.model_dir):
            makedirs(self.model_dir)

        if path.isfile(self.path('model.pkl')) and \
            path.isfile(self.path('means.pkl')) and \
            path.isfile(self.path('data.pkl')):
            self.clf = joblib.load(self.path('model.pkl'))
            self.means = joblib.load(self.path('means.pkl'))
            self.data = joblib.load(self.path('data.pkl'))
            self.fitted = True
            logger.info("Loaded pre-trained model from disk.")
            return

        # construct the classifier
        self.clf = getattr(_models, self.clf_name)(self.clf_conf)
        logger.info("Built a new %s classifier" % self.clf_name)

        # self.pre_train(["C:/Users/Farshid/Desktop/thesis/early-fault-detection/training/agent/ABU1.txt"])
        # return self.clf

    def learn(self, datapoint):
        logger.info("agent.learn: %s" % "datapoint")
        raise NotImplementedError

    def predict(self, datapoint):

        if not self.fitted:
            logger.info("Model not trained yet.")
            return 0

        features = Event2Dict(datapoint, self.production_layout, complete=False)
        features = np.array(features.values())
        # convert measurements to numpy array
        r = features[2:-1].astype(np.float32)
        # fill nans with global means
        w = np.where(np.isnan(r))
        r[w] = self.means[w]
        start_time = time.time()
        p = self.clf.predict(r.reshape(1, -1))[0]
        logger.info("Prediction for {}:{} in {:0.3f}s -> {}".format(datapoint['type'], datapoint['id'], time.time() - start_time, p))
        return p.item()

    # Take random numbers from a logistic probability density function
    def logistic_choice(self, total, sample_size, replace=False):
        p = logistic.pdf(np.arange(0,total), loc=0, scale=total/5.0)
        p /= np.sum(p)
        return np.random.choice(total, size=sample_size, replace=replace, p=p)

    def batchLearn(self, datapoints):
        logger.info("agent.batchLearn.")
        with self.lock:
            for datapoint in datapoints:
                try:
                    features = Event2Dict(datapoint,  self.production_layout, complete=True)
                    features = np.asarray(features.values())
                    self.data.append(features)
                except Exception as e:
                    logger.error(e)

            train = np.asarray(self.data)
            # print(train)
            faulty = train[train[:,-1]==_false]
            not_faulty = train[train[:,-1]==_true]
            logger.info("Train Total: {} Good: {} Faulty: {} Ratio: {}".format(len(train), len(not_faulty), len(faulty), len(faulty)/float(len(train))))
            if(len(faulty)==0 or len(not_faulty)==0):
                logger.info("Waiting for samples from both classes.")
                return

            sample_size = np.min([5000, len(not_faulty)])
            samples = self.logistic_choice(len(not_faulty), sample_size)
            # TODO: Upsample faulties with logistic_choice(replace=True)
            f_sample_size = np.min([1000, len(faulty)])
            f_samples = self.logistic_choice(len(faulty), f_sample_size)
            # Put samples together and shuffle
            train = np.concatenate((not_faulty[samples], faulty[f_samples]))
            train = np.random.permutation(train)
            logger.info("Resampled Train Total: {} Good: {} Faulty: {} Ratio: {}".format(len(train), len(samples), len(f_samples), len(f_samples)/float(len(train))))

            train_data = train[:,2:-1].astype(np.float32)
            train_labels = np.array(train[:,-1]==_false).astype(np.int32)

            """ train model """
            start_time = time.time()
            self.clf = self.clf.fit(train_data, train_labels)
            self.fitted = True

            # re-calculate means of this sub-sample
            self.means = np.mean(not_faulty[samples,2:-1].astype(np.float32), axis=0)

            logger.info("Trained in {:0.3f}s".format(time.time() - start_time))
            #print_metrics(train_labels, self.clf.predict(train_data))

            # Save model to disk
            #self.saveModel(np.copy(self.clf), np.copy(self.means), np.copy(self.data))
            thread.start_new_thread(self.saveModel, (deepcopy(self.clf), deepcopy(self.means), deepcopy(self.data),))

    def batchPredict(self, datapoints):
        logger.info("agent.batchPredict.")
        # return np.zeros(len(datapoints)).astype(int).tolist()
        if not self.fitted:
            logger.info("Model not trained yet.")
            return np.zeros(len(datapoints)).astype(int).tolist()

        data = []
        for datapoint in datapoints:
            try:
                features = Event2Dict(datapoint, self.production_layout, complete=False)
                # del features['Id'], features['Type'], features['Label']
                features = np.asarray(features.values())
                features = features[2:-1].astype(np.float32)

                # fill nans with global means
                w = np.where(np.isnan(features))
                if np.any(w):
                    logger.warning("Missing: {}".format(validate(datapoint, self.production_layout)))
                features[w] = self.means[w]

                data.append(features)
            except Exception as e:
                logger.error(e)
                logger.debug(traceback.format_exc())

        data = np.asarray(data)
        start_time = time.time()
        try:
            predictions = self.clf.predict(data)
        except Exception as e:
            logger.error(e)
            logger.debug("Data: {}".format(json.dumps(data)))
            logger.info("Batch prediction failed.")
            return np.zeros(len(datapoints)).astype(int).tolist()

        logger.info("Batch Prediction in {:0.3f}s".format(time.time() - start_time))
        return predictions.tolist()


    def destroy(self):
        logger.info("agent.destroy")

    def exportModel(self):
        raise NotImplementedError
        # Zip tmp directory and return binaries?
        # http://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
        # pmml: https://github.com/alex-pirozhenko/sklearn-pmml

    def importModel(self):
        raise NotImplementedError

    """ UTILITY FUNCTIONS """
    def loadParameters(self, classifier):
        try:
            self.clf_name = classifier["name"]
            self.clf_conf = classifier["conf"]
            self.production_layout = classifier["production_layout"]
            self.model_dir = path.join(classifier["dir"], self.production_layout["type"])
        except KeyError as e:
            raise KeyError("Attribute `%s` is not set in the classifier object." % e.message)

    # returns the filename appended to the model path
    def path(self, filename):
        return path.join(self.model_dir, filename)

    def saveModel(self, clf, means, data):
        start_time = time.time()
        try:
            # Save to disk
            joblib.dump(clf, self.path('model.pkl'))
            joblib.dump(means, self.path('means.pkl'))
            joblib.dump(data, self.path('data.pkl'))
        except Exception as e:
            logger.error("Unable to save model.")
            raise IOError(str(e))
        logger.info("Saved to {} in {:0.3f}s".format(self.model_dir, time.time() - start_time))

    # def pre_train(self, training_files):
    #     print("agent.pre_train: %s" % training_files)
    #     data = []
    #     bad = 0
    #     for filename in training_files:
    #         if not path.exists(filename):
    #             print("File does not exist: %s" % filename)
    #             continue
    #         print("Loading rows... {}".format(filename))
    #         with open(filename) as f:
    #             for line in f:
    #                 try:
    #                     features = SensorThings2Dict(json.loads(line))
    #                     data.append(list(features.values()))
    #                 except Exception, e:
    #                     # print(e)
    #                     bad+=1
    #
    #     print("Incomplete rows: {}".format(bad))
    #     print("Loaded: {}".format(len(data)))
    #
    #     """ random split seed """
    #     data = np.asarray(data)
    #     mask = np.random.rand(len(data)) < 0.9
    #
    #     """ split into train and test sets """
    #     train = data[mask]
    #     test = data[~mask]
    #     print("Train Total: {} Good: {} Faulty: {} Ratio: {}".format(len(train), len(train[train[:,-1]=='True']), len(train[train[:,-1]=='False']), float(len(train[train[:,-1]=='False']))/len(train)))
    #     print("Test  Total: {} Good: {} Faulty: {} Ratio: {}".format(len(test), len(test[test[:,-1]=='True']), len(test[test[:,-1]=='False']), float(len(test[test[:,-1]=='False']))/len(train)))
    #
    #     faulty = train[train[:,-1]=='False']
    #     not_faulty = train[train[:,-1]=='True']
    #
    #     self.means = np.mean(not_faulty[:,2:-1].astype(np.float32), axis=0)
    #
    #     """ down/up sample data """
    #     samples = np.random.choice(len(not_faulty), 5000, replace=False)
    #     train = np.concatenate((not_faulty[samples], faulty))
    #     print("Train Total: {} Good: {} Faulty: {} Ratio: {}".format(len(train), len(train[train[:,-1]=='True']), len(train[train[:,-1]=='False']), float(len(train[train[:,-1]=='False']))/len(train)))
    #
    #     train_data = train[:,2:-1].astype(np.float32)
    #     test_data = test[:,2:-1].astype(np.float32)
    #
    #     train_labels = np.array(train[:,-1]=='False').astype(np.int32)
    #     test_labels = np.array(test[:,-1]=='False').astype(np.int32)
    #
    #     """ train model """
    #     self.clf = self.clf.fit(train_data, train_labels)
    #     self.fitted = True
    #     print_metrics(train_labels, self.clf.predict(train_data))
    #     print_metrics(test_labels, self.clf.predict(test_data))
    #
    #     # save to disk
    #     joblib.dump(self.means, self.path('/means.pkl'))
    #     joblib.dump(self.clf, self.path('model.pkl'))

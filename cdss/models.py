from django.db import models
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
class LWGMKNN(BaseEstimator, ClassifierMixin):
    def __init__(self, n_neighbors=9):
        self.n_neighbors = n_neighbors
        self.model = KNeighborsClassifier(n_neighbors=n_neighbors)
    
    def fit(self, X, y):
        self.model.fit(X, y)
        #print(self.model._fit_X.dtypes)
        return self
    
    def predict(self, X):
        predictions = []
        for row_data in X:
            distances_0 = []
            distances_1 = []
            # Calculate distances between the test row and all training rows
            for train_data, train_label in zip(self.model._fit_X, self.model._y):
                
                distance = np.sqrt(np.sum((row_data - train_data) ** 2))
                if train_label == 0:
                    distances_0.append(distance)
                else:
                    distances_1.append(distance)

            # Compute weighted distance averages
            idw_0 = np.sum(1 / np.sort(distances_0)[:self.n_neighbors])
            idw_1 = np.sum(1 / np.sort(distances_1)[:self.n_neighbors])
            m_0 = np.mean(distances_0)
            m_1 = np.mean(distances_1)
            p_0 = idw_0 * m_0
            p_1 = idw_1 * m_1

            # Make prediction based on minimum weighted distance average
            pc = 0 if p_0 > p_1 else 1
            predictions.append(pc)

        return np.array(predictions)

    
    def score(self, X, y):
        return self.model.score(X, y)
# Create your models here.

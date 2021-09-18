# Use this file as shortcut import to import all Machine Learning imports that you may need in a project

#Processing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification

#Unsupervised learning
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from pyod.models.auto_encoder import AutoEncoder
# from pyod.models.feature_bagging import FeatureBagging
from pyod.models.knn     import KNN
from pyod.models.lof     import LOF
from pyod.models.hbos    import HBOS
from pyod.models.iforest import IForest

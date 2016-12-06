
""" Random Forest """
def random_forest(params):
    from sklearn.ensemble import RandomForestClassifier
    clf = RandomForestClassifier(n_estimators=100,  class_weight={0:1.0, 1:0.05}, max_depth=90, n_jobs=4)
    return clf

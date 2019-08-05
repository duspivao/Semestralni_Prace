




"""
Can be used for cound normalized version of features
    # >>> from sklearn.preprocessing import StandardScaler
    # >>> data = [[0, 0], [0, 0], [1, 1], [1, 1]]
    # >>> scaler = StandardScaler()
    # >>> print(scaler.fit(data))
    # StandardScaler(copy=True, with_mean=True, with_std=True)
    # >>> print(scaler.mean_)
    # [0.5 0.5]
    # >>> print(scaler.transform(data))
    # [[-1. -1.]
    #  [-1. -1.]
    #  [ 1.  1.]
    #  [ 1.  1.]]
    # >>> print(scaler.transform([[2, 2]]))
    # [[3. 3.]]
"""
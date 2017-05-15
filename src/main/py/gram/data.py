import numpy as np

class DataSet:
    def __init__(self, data=[]):
        self._data = list(data)

    def get(self, i):
        return self._data[i]

    def get_data(self):
        return self._data

    def get_size(self):
        return len(self._data)

    def copy(self):
        return DataSet(data=list(self._data))

    def shuffle(self):
        perm = np.random.permutation(len(self._data))
        shuffled_data = []
        for i in range(len(perm)):
            shuffled_data.append(self._data.get(perm[i]))
        self._data = shuffled_data

    def split(self, sizes):
        datas = []
        index = 0
        for size in sizes:
            part_data = []
            max_index = min(len(self._data), index + size*len(self._data))
            while index < max_index:
                part_data.append(self._data[index])
                index += 1
            datas.append(DataSet(data=part_data))
        return datas



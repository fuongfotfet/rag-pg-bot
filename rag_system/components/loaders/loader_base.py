from abc import ABC, abstractmethod

class DataLoaderBase(ABC): 
    def __init__(self): 
        pass

    @abstractmethod
    def load(self, data_url): 
        pass

    
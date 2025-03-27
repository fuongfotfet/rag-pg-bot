from abc import ABC, abstractmethod

class SearchBase(ABC): 
    def __init__(self): 
        pass

    @abstractmethod
    def search(self, question): 
        pass

    
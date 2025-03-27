from abc import ABC, abstractmethod

class EmbedderBase(ABC): 
    def __init__(self): 
        pass

    @abstractmethod
    def embed(self, data_chunks): 
        pass

    
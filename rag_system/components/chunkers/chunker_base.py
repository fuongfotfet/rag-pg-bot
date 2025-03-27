from abc import ABC, abstractmethod
from typing import List
from rag_system.core.data_chunk import DataChunk

class ChunkerBase(ABC): 
    def __init__(self): 
        pass

    @abstractmethod
    def chunk(self, data: List[DataChunk]) -> List[DataChunk]: 
        pass


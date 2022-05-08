from numba.experimental import jitclass
import numpy as np

@jitclass
class HashTable():
    def __init__(self, length):
        """
        ( code | code | code | code | origin | origin | alpha | scale | iA | iB | iC | iD )
         - 'code' 4 hashcode values
         - 'origin' origin of hash coordinate system in celectial coordiantes
         - 'scale'  scale of hash cordinate system
         - 'i*'     indices of stars creating hash coordinate system corresponding
                    to dataframe
        """
                
        self.codes  = np.array((length, 4), dtype=np.float32)
        self.origin = np.array((length, 2), dtype=np.float32)
        self.alpha  = np.array((length), dtype=np.float32)
        self.scale  = np.array((length), dtype=np.float32)
        self.idc    = np.array((length, 4), dtype=int)
        
        self.ptr = -1   # incremented at first run
        
        
    def add_row(self, code, origin, alpha, scale, idc):
        self.ptr += 1
        if self.ptr > self.codes.shape[0]:
            raise RuntimeError
        
        self.codes[self.ptr]  = code
        self.origin[self.ptr] = origin
        self.alpha[self.ptr]  = alpha
        self.scale[self.ptr]  = scale
        self.idc[self.ptr]    = idc
        
        
    def append(self, htable):
        """append another htable while deleting unused space"""
        self.codes  = self.codes[:self.ptr+1]  + htable.codes[:htable.ptr+1]
        self.origin = self.origin[:self.ptr+1] + htable.origin[:htable.ptr+1]
        self.alpha  = self.alpha[:self.ptr+1]  + htable.alpha[:htable.ptr+1]
        self.scale  = self.scale[:self.ptr+1]  + htable.scale[:htable.ptr+1]
        self.idc    = self.idc[:self.ptr+1]    + htable.idc[:htable.ptr+1]
        
        self.ptr = self.ptr + htable.ptr   # incremented at first run
        
    
    def __repr__(self):
        return f"HashTable with {self.codes.shape[0]} entries"
    
    
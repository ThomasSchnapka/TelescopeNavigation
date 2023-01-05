"""table structure containing star locations and hashcodes"""
from numba.experimental import jitclass
import numpy as np
import pickle

#@jitclass
class HashTable():
    def __init__(self, length=0):
        """
        ( code | code | code | code || origin | origin || alpha | scale || iA | iB | iC | iD )
         - 'code' 4 hashcode values
         - 'origin' origin of hash coordinate system in celectial coordiantes
         - 'scale'  scale of hash cordinate system
         - 'i*'     indices of stars creating hash coordinate system corresponding
                    to dataframe
        """
                
        self.codes  = np.zeros((length, 4), dtype=np.float32)
        self.origin = np.zeros((length, 2), dtype=np.float32)
        self.alpha  = np.zeros(length, dtype=np.float32)
        self.scale  = np.zeros(length, dtype=np.float32)
        self.idc    = np.zeros((length, 4), dtype=int)
        
        self.ptr = 0   # incremented at first run
        
        
    def add_row(self, code, origin, alpha, scale, idc):
       
        self.codes[self.ptr]  = code
        self.origin[self.ptr] = origin
        self.alpha[self.ptr]  = alpha
        self.scale[self.ptr]  = scale
        self.idc[self.ptr]    = idc
        
        self.ptr += 1
        if self.ptr > self.codes.shape[0]:
            raise RuntimeError
        
    def append(self, htable):
        """append another htable while deleting unused space"""
        self.codes  = np.vstack((self.codes[:self.ptr],  htable.codes[:htable.ptr]))
        self.origin = np.vstack((self.origin[:self.ptr], htable.origin[:htable.ptr]))
        self.alpha  = np.concatenate((self.alpha[:self.ptr],  htable.alpha[:htable.ptr]))
        self.scale  = np.concatenate((self.scale[:self.ptr],  htable.scale[:htable.ptr]))
        self.idc    = np.vstack((self.idc[:self.ptr],    htable.idc[:htable.ptr]))
        
        self.ptr = self.ptr + htable.ptr   # incremented at first run
        
    
    def __repr__(self):
        return f"HashTable with {self.codes.shape[0]} entries"
    
    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)

    def load(self, filename):
        with open(filename, 'rb') as file:
            htable = pickle.load(file)

        self.codes  = htable.codes
        self.origin = htable.origin
        self.alpha  = htable.alpha
        self.scale  = htable.scale
        self.idc    = htable.idc    
        
        return self


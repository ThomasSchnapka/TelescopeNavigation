from numba.experimental import jitclass
import numpy as np

#@jitclass
class StarChart():
    def __init__(self, path="data/hygdata_v3.csv"):
        # downloaded from https://github.com/astronexus/HYG-Database
    
        # read entries
        self.ra = np.genfromtxt(path, delimiter=',', 
                                skip_header=True, usecols=7, dtype=float)
        self.dec = np.genfromtxt(path, delimiter=',', 
                                 skip_header=True, usecols=8, dtype=float)
        self.mag = np.genfromtxt(path, delimiter=',', 
                                 skip_header=True, usecols=13, dtype=float)
        self.name = np.genfromtxt(path, delimiter=',', 
                                  skip_header=True, usecols=6, dtype=str)
        
        # sort entries by brightness 
        # (key step to avoid sorting during selection)
        sidx = np.argsort(self.mag)
        self.ra = self.ra[sidx]
        self.dec = self.dec[sidx]
        self.mag = self.mag[sidx]
        self.name = self.name[sidx]
        
        # convert angles to rad
        self.ra = np.pi*self.ra/12
        self.dec = np.pi*self.dec/180
        
    def __getitem__(self, k):
        return np.array([self.ra[k], self.dec[k], self.mag[k], self.name[k]])
    
    def __repr__(self):
        return f"StarChart with {len(self.ra)} entries"
    
    
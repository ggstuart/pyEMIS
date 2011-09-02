import time
print time.gmtime()

#Need to know resolution of data if I'm going to be able to reshape the profile properly using 'np.reshape'
class ConsumptionProfile(object):
    def __init__(self, data):
        self.data = data

    def grid(self, width, start_wday=7, start_hour=0, start_min=0):
        pass
        
    def profile(self):
        grid = self.grid(7*24)
        


import matplotlib.pyplot as plt
import numpy as np

def MandelbrotInit():
    ReZ, ImZ = np.meshgrid(np.linspace(-2,1,400), np.linspace(-1.5,1.5,400))
    
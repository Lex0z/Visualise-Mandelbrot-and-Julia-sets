import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def MandelgrotSetMake(x_range, y_range, size, max_iter):
    x_min , x_max = x_range
    y_min , y_max = y_range

    ReC, ImC = np.meshgrid(np.linspace(x_min,x_max,size), np.linspace(y_min,y_max,size))
    C = ReC + 1j * ImC
    Z = np.zeros((size, size), dtype=complex)
    output = np.ones((size,size))
    for i in range(1, max_iter):
        mask = abs(Z) < 2
        Z = np.where(mask, Z*Z + C, Z)
        output = np.where(mask, i, output)
    
    return output   

def Visualise(output, x_range, y_range):
    x_min , x_max = x_range
    y_min , y_max = y_range

    fig, ax = plt.subplots(figsize=(10, 10))
    im = ax.imshow(output, cmap='inferno', extent=[x_min, x_max, y_min, y_max], origin='lower', norm=mcolors.LogNorm())
    plt.colorbar(im, ax=ax, label='Number of iterations')
    ax.set_xlabel('Real')
    ax.set_ylabel('Imaginary')

    plt.show()


def main():
    size = 1000
    max_iter = 200
    x_min = -2
    x_max = 1
    y_min = -1.5
    y_max = 1.5

    output = MandelgrotSetMake((x_min, x_max),(y_min, y_max), size, max_iter)
    Visualise(output, (x_min, x_max), (y_min, y_max))

if __name__ == "__main__":
    main()
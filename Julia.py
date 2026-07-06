import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def JuliaSetMake(x_range, y_range, size, max_iter, C):
    x_min , x_max = x_range
    y_min , y_max = y_range

    ReZ, ImZ = np.meshgrid(np.linspace(x_min,x_max,size), np.linspace(y_min,y_max,size))
    Z = ReZ + 1j * ImZ

    output = np.ones((size,size))
    for i in range(1, max_iter):
        mask = abs(Z) < 2
        Z = np.where(mask, Z*Z + C, Z)
        output = np.where(mask, i, output)

    return output

def Visualise(outputs, x_range, y_range, shape=None):
    if shape == None:
        shape = (1, len(outputs))
    fig, axes = plt.subplots(*shape, figsize=(15, 7))
    images = []    

    for idx, ax in enumerate(axes):
        im = ax.imshow(outputs[idx], cmap='inferno', extent=[*x_range, *y_range], origin='lower', norm=mcolors.LogNorm())
        ax.set_xlabel('Real')
        ax.set_ylabel('Imaginary')
        images.append(im)

    fig.colorbar(images[0], ax=axes.ravel().tolist(), label='Number of iterations',location='bottom', pad=0.1, shrink=0.7)

    plt.subplots_adjust(bottom=0.37,left=0.05,right=0.95)
    plt.show()

    return fig, axes

def main():
    size = 100
    max_iter = 100
    x_range = (-1.5,1.5)
    y_range = (-1.5,1.5)

    Cs = [-0.8 + 0.156j, -0.4 + 0.6j, 0.285 + 0.01j]
    outputs = [JuliaSetMake(x_range, y_range, size, max_iter, c) for c in Cs]

    fig, axes = Visualise(outputs, x_range, y_range, (1,3))

if __name__ == "__main__":
    main()
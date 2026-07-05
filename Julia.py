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
    size = 100
    max_iter = 100
    x_min = -1.5
    x_max = 1.5
    y_min = -1.5
    y_max = 1.5

    C1 = -0.8 + 0.156j
    C2 = -0.4 + 0.6j
    C3 = 0.285 + 0.01j

    output1 = JuliaSetMake((x_min, x_max),(y_min, y_max), size, max_iter, C1)
    output2 = JuliaSetMake((x_min, x_max),(y_min, y_max), size, max_iter, C2)
    output3 = JuliaSetMake((x_min, x_max),(y_min, y_max), size, max_iter, C3)
    # Visualise(output, (x_min, x_max), (y_min, y_max))

    fig, ax = plt.subplots(1, 3, figsize=(15, 7))
    
    im1 = ax[0].imshow(output1, cmap='inferno', extent=[x_min, x_max, y_min, y_max], origin='lower', norm=mcolors.LogNorm())
    # plt.colorbar(im1, ax=ax[0], label='Number of iterations')
    ax[0].set_xlabel('Real')
    ax[0].set_ylabel('Imaginary')

    im2 = ax[1].imshow(output2, cmap='inferno', extent=[x_min, x_max, y_min, y_max], origin='lower', norm=mcolors.LogNorm())
    # plt.colorbar(im2, ax=ax[1], label='Number of iterations')
    ax[1].set_xlabel('Real')
    ax[1].set_ylabel('Imaginary')

    im3 = ax[2].imshow(output3, cmap='inferno', extent=[x_min, x_max, y_min, y_max], origin='lower', norm=mcolors.LogNorm())
    # plt.colorbar(im3, ax=ax[2], label='Number of iterations')
    ax[2].set_xlabel('Real')
    ax[2].set_ylabel('Imaginary')

    fig.colorbar(im3, ax=ax.ravel().tolist(), label='Number of iterations',location='bottom', pad=0.1, shrink=0.7)

    plt.subplots_adjust(bottom=0.37,left=0.05,right=0.95)
    plt.show()

if __name__ == "__main__":
    main()
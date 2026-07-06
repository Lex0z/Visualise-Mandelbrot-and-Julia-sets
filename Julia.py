import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def JuliaSetMake(x_range, y_range, size, max_iter, C):
    x_min, x_max = x_range
    y_min, y_max = y_range
    ReZ, ImZ = np.meshgrid(np.linspace(x_min, x_max, size), np.linspace(y_min, y_max, size))
    Z = ReZ + 1j * ImZ
    output = np.ones((size, size))
    for i in range(1, max_iter):
        mask = abs(Z) < 2
        Z = np.where(mask, Z*Z + C, Z)
        output = np.where(mask, i, output)
    return output

def Visualise(outputs, x_range, y_range, Cs, shape=None):
    if shape is None:
        shape = (1, len(outputs))
    
    fig, axes = plt.subplots(*shape, figsize=(15, 7))
    images = []
    
    fig.state = {
        'mode': 'three',  # текущий режим отображения
        'current_c': None,  # текущее значение C (в режиме 'one')
        'current_ax': None,  # текущий axes (в режиме 'one')
        'original_ranges': {},  # исходные диапазоны для каждого C
        'current_ranges': {},  # текущие диапазоны для каждого C
        'selectors': [],  # RectangleSelector для каждого axes
        'buttons': {}  # кнопки управления
    }
    
    for idx, ax in enumerate(axes):
        im = ax.imshow(outputs[idx], cmap='inferno', 
                      extent=[*x_range, *y_range], 
                      origin='lower', 
                      norm=mcolors.LogNorm())
        ax.set_xlabel('Real')
        ax.set_ylabel('Imaginary')
        ax.set_title(f'c = {Cs[idx]}')
        images.append(im)
        
        ax.c_value = Cs[idx]
        ax.original_x_range = x_range
        ax.original_y_range = y_range
        ax.current_x_range = x_range
        ax.current_y_range = y_range
        ax.idx = idx
        
        fig.state['original_ranges'][idx] = {
            'x_range': x_range,
            'y_range': y_range
        }
        fig.state['current_ranges'][idx] = {
            'x_range': x_range,
            'y_range': y_range
        }
    
    fig.colorbar(images[0], ax=axes.ravel().tolist(), 
                label='Number of iterations',
                location='bottom', 
                pad=0.1, 
                shrink=0.7)
    plt.subplots_adjust(bottom=0.37, left=0.05, right=0.95)
    plt.show()
    
    return fig, axes

def main():
    size = 100
    max_iter = 100
    x_range = (-1.5, 1.5)
    y_range = (-1.5, 1.5)
    Cs = [-0.8 + 0.156j, -0.4 + 0.6j, 0.285 + 0.01j]
    
    outputs = [JuliaSetMake(x_range, y_range, size, max_iter, c) for c in Cs]
    fig, axes = Visualise(outputs, x_range, y_range, Cs, (1, 3))
    
    print("State initialized:")
    print(f"Mode: {fig.state['mode']}")
    print(f"Original ranges: {fig.state['original_ranges']}")
    print(f"\nAxes attributes:")
    for idx, ax in enumerate(axes):
        print(f"Axes {idx}: c={ax.c_value}, x_range={ax.current_x_range}")

if __name__ == "__main__":
    main()
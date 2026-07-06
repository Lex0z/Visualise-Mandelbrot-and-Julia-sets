import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import RectangleSelector
import numpy as np

# def on_select(*args):...

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

def Visualise(outputs, x_range, y_range, shape = None,):
    if shape == None:
        shape = (1,len(outputs))

    fig, axes = plt.subplots(*shape, figsize=(15, 7))

    images = []
    for idx, ax in enumerate(axes):
        im = ax.imshow(outputs[idx], cmap='inferno', 
                  extent=[*x_range, *y_range], 
                  origin='lower', norm=mcolors.LogNorm())
        ax.set_xlabel('Real')
        ax.set_ylabel('Imaginary')
        images.append(im)

        selector = RectangleSelector(
            ax,
            lambda eclick, erelease, idx=idx: on_select(eclick, erelease, idx),
            # drawtype='box',
            useblit=True,
            button=[1],
            minspanx=10,
            minspany=10,
            spancoords='pixels',
            interactive=True
        )
    
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

    # fig, axes = Visualise(outputs, x_range, y_range, shape=(1, 3))

    limits = {0: x_range + y_range, 1: x_range + y_range, 2: x_range + y_range}

    fig, axes = plt.subplots(1, 3, figsize=(15, 7))

    def on_select(eclick, erelease, ax_idx):
        """Callback для RectangleSelector с привязкой к индексу subplot'а"""
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        
        # Сортируем координаты
        xmin, xmax = sorted([x1, x2])
        ymin, ymax = sorted([y1, y2])
        
        # Проверяем, что выделение не слишком маленькое
        if (xmax - xmin) < 0.01 or (ymax - ymin) < 0.01:
            return
        
        # Сохраняем новые пределы
        limits[ax_idx] = (xmin, xmax, ymin, ymax)
        
        # Пересчитываем множество Жюлиа для выбранной области
        # Увеличиваем разрешение для лучшего качества зума
        zoom_size = int(size * 1.5)
        new_output = JuliaSetMake(
            (xmin, xmax), (ymin, ymax), 
            zoom_size, max_iter, Cs[ax_idx]
        )
        
        # Обновляем изображение
        axes[ax_idx].clear()
        axes[ax_idx].imshow(
            new_output, 
            cmap='inferno', 
            extent=[xmin, xmax, ymin, ymax],
            origin='lower',
            norm=mcolors.LogNorm()
        )
        axes[ax_idx].set_title(f'c = {Cs[ax_idx]} (zoom)')
        axes[ax_idx].set_xlabel('Real')
        axes[ax_idx].set_ylabel('Imaginary')
        
        fig.canvas.draw()

    images = []
    for idx, ax in enumerate(axes):
        im = ax.imshow(outputs[idx], cmap='inferno', 
                  extent=[*x_range, *y_range], 
                  origin='lower', norm=mcolors.LogNorm())
        ax.set_xlabel('Real')
        ax.set_ylabel('Imaginary')
        images.append(im)

        selector = RectangleSelector(
            ax,
            lambda eclick, erelease, idx=idx: on_select(eclick, erelease, idx),
            # drawtype='box',
            useblit=True,
            button=[1],
            minspanx=10,
            minspany=10,
            spancoords='pixels',
            interactive=True
        )
    
    fig.colorbar(images[0], ax=axes.ravel().tolist(), label='Number of iterations',location='bottom', pad=0.1, shrink=0.7)

    plt.subplots_adjust(bottom=0.37,left=0.05,right=0.95)
    plt.show()

if __name__ == "__main__":
    main()
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

class JuliaVisualization:
    """Класс для управления визуализацией множества Жюлиа"""
    
    def __init__(self, c, x_range, y_range, size=100, max_iter=100):
        """
        Инициализация визуализации
        
        Args:
            c: комплексная константа
            x_range: кортеж (x_min, x_max)
            y_range: кортеж (y_min, y_max)
            size: размер сетки (фиксированный)
            max_iter: базовое максимальное количество итераций
        """
        self.c = c
        self.size = size  # Размер сетки - фиксированный
        
        # Сохраняем исходные параметры
        self.original_x_range = x_range
        self.original_y_range = y_range
        self.original_max_iter = max_iter
        
        # Текущие параметры (могут изменяться при зуме)
        self.current_x_range = x_range
        self.current_y_range = y_range
        self.current_max_iter = max_iter
        
        # Вычисляем множество
        self.output = self._calculate()
    
    def _calculate(self):
        """Внутренний метод вычисления множества Жюлиа"""
        x_min, x_max = self.current_x_range
        y_min, y_max = self.current_y_range
        
        ReZ, ImZ = np.meshgrid(
            np.linspace(x_min, x_max, self.size),
            np.linspace(y_min, y_max, self.size)
        )
        Z = ReZ + 1j * ImZ
        output = np.ones((self.size, self.size))
        
        for i in range(1, self.current_max_iter):
            mask = abs(Z) < 2
            Z = np.where(mask, Z*Z + self.c, Z)
            output = np.where(mask, i, output)
        
        return output
    
    def zoom(self, new_x_range, new_y_range):
        """
        Зум в указанную область
        
        Args:
            new_x_range: новый диапазон по X
            new_y_range: новый диапазон по Y
        """
        # Вычисляем уровень зума
        original_width = self.original_x_range[1] - self.original_x_range[0]
        new_width = new_x_range[1] - new_x_range[0]
        zoom_level = original_width / new_width
        
        # Увеличиваем количество итераций для детализации фрактала
        # Размер сетки остается неизменным!
        self.current_max_iter = min(int(self.original_max_iter * np.log2(zoom_level + 1)), 500)
        
        # Обновляем только диапазоны
        self.current_x_range = new_x_range
        self.current_y_range = new_y_range
        
        # Пересчитываем множество
        self.output = self._calculate()
        
        print(f"Zoom level: {zoom_level:.2f}x, size: {self.size} (fixed), max_iter: {self.current_max_iter}")
    
    def reset(self):
        """Сброс к исходным параметрам"""
        self.current_x_range = self.original_x_range
        self.current_y_range = self.original_y_range
        self.current_max_iter = self.original_max_iter
        self.output = self._calculate()
        print("Reset to original view")
    
    def get_info(self):
        """Получить информацию о текущем состоянии"""
        return {
            'c': self.c,
            'x_range': self.current_x_range,
            'y_range': self.current_y_range,
            'size': self.size,
            'max_iter': self.current_max_iter,
            'zoom_level': (self.original_x_range[1] - self.original_x_range[0]) / 
                         (self.current_x_range[1] - self.current_x_range[0])
        }


def Visualise(julia_vizs, shape=None):
    """
    Визуализация списка объектов JuliaVisualization
    
    Args:
        julia_vizs: список объектов JuliaVisualization
        shape: форма сетки subplot'ов
    """
    if shape is None:
        shape = (1, len(julia_vizs))
    
    fig, axes = plt.subplots(*shape, figsize=(15, 7))
    images = []
    
    # Инициализация состояния
    fig.state = {
        'mode': 'three',
        'current_viz': None,
        'current_ax': None,
        'selectors': [],
        'buttons': {}
    }
    
    for idx, (ax, julia_viz) in enumerate(zip(axes, julia_vizs)):
        im = ax.imshow(
            julia_viz.output, 
            cmap='inferno', 
            extent=[*julia_viz.current_x_range, *julia_viz.current_y_range], 
            origin='lower', 
            norm=mcolors.LogNorm()
        )
        ax.set_xlabel('Real')
        ax.set_ylabel('Imaginary')
        ax.set_title(f'c = {julia_viz.c}')
        images.append(im)
        
        # Сохраняем ссылку на объект визуализации в axes
        ax.julia_viz = julia_viz
        ax.idx = idx
    
    fig.colorbar(
        images[0], 
        ax=axes.ravel().tolist(), 
        label='Number of iterations',
        location='bottom', 
        pad=0.1, 
        shrink=0.7
    )
    plt.subplots_adjust(bottom=0.37, left=0.05, right=0.95)
    
    # Показываем без блокировки для возможности обновления
    plt.show(block=False)
    
    return fig, axes


def update_visualization(fig, axes, julia_vizs):
    """
    Обновление визуализации после изменения данных
    
    Args:
        fig: figure объект
        axes: список axes
        julia_vizs: список объектов JuliaVisualization
    """
    for idx, (ax, julia_viz) in enumerate(zip(axes, julia_vizs)):
        # Очищаем axes
        ax.clear()
        
        # Перерисовываем изображение
        im = ax.imshow(
            julia_viz.output, 
            cmap='inferno', 
            extent=[*julia_viz.current_x_range, *julia_viz.current_y_range], 
            origin='lower', 
            norm=mcolors.LogNorm()
        )
        ax.set_xlabel('Real')
        ax.set_ylabel('Imaginary')
        ax.set_title(f'c = {julia_viz.c}')
        
        # Обновляем ссылки
        ax.julia_viz = julia_viz
        ax.idx = idx
    
    # Обновляем canvas
    fig.canvas.draw()
    fig.canvas.flush_events()


def main():
    x_range = (-1.5, 1.5)
    y_range = (-1.5, 1.5)
    Cs = [-0.8 + 0.156j, -0.4 + 0.6j, 0.285 + 0.01j]
    
    # Создание списка объектов JuliaVisualization
    julia_vizs = [JuliaVisualization(c, x_range, y_range, size=100, max_iter=100) 
                  for c in Cs]
    
    # Вывод информации о каждом объекте
    print("Initial state:")
    for idx, viz in enumerate(julia_vizs):
        print(f"\nVisualization {idx}:")
        info = viz.get_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    # Начальная визуализация
    fig, axes = Visualise(julia_vizs, (1, 3))
    
    # Пауза для просмотра начального состояния
    input("\nPress Enter to test zoom...")
    
    # Тестирование зума
    print("\n\nTesting zoom on first visualization:")
    julia_vizs[0].zoom((-0.5, 0.5), (-0.5, 0.5))
    info = julia_vizs[0].get_info()
    print(f"New zoom level: {info['zoom_level']:.2f}x")
    
    # Обновление визуализации
    update_visualization(fig, axes, julia_vizs)
    
    # Пауза для просмотра зума
    input("\nPress Enter to test reset...")
    
    # Тестирование сброса
    print("\nTesting reset:")
    julia_vizs[0].reset()
    info = julia_vizs[0].get_info()
    print(f"Zoom level after reset: {info['zoom_level']:.2f}x")
    
    # Обновление визуализации
    update_visualization(fig, axes, julia_vizs)
    
    # Финальная пауза
    input("\nPress Enter to exit...")
    plt.close(fig)


if __name__ == "__main__":
    main()
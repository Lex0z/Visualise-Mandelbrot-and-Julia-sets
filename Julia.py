import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import RectangleSelector
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
    
    def _normalize_to_square(self, x_range, y_range):
        """
        Приведение выбранной области к квадратному виду
        
        Args:
            x_range: кортеж (x_min, x_max)
            y_range: кортеж (y_min, y_max)
        
        Returns:
            tuple: (new_x_range, new_y_range) - квадратная область
        """
        width = x_range[1] - x_range[0]
        height = y_range[1] - y_range[0]
        
        # Центры областей
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2
        
        # Берем наибольшую сторону
        max_side = max(width, height)
        
        # Создаем квадратную область с тем же центром
        new_x_range = (x_center - max_side / 2, x_center + max_side / 2)
        new_y_range = (y_center - max_side / 2, y_center + max_side / 2)
        
        return new_x_range, new_y_range

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
        """
        # Приводим к квадратному виду
        new_x_range, new_y_range = self._normalize_to_square(new_x_range, new_y_range)
        
        # Вычисляем уровень зума
        original_width = self.original_x_range[1] - self.original_x_range[0]
        new_width = new_x_range[1] - new_x_range[0]
        zoom_level = original_width / new_width
        
        # Увеличиваем количество итераций
        self.current_max_iter = min(int(self.original_max_iter * np.log2(zoom_level + 1)), 500)
        
        # Обновляем диапазоны
        self.current_x_range = new_x_range
        self.current_y_range = new_y_range
        
        # Пересчитываем множество
        self.output = self._calculate()
        
        print(f"Zoom level: {zoom_level:.2f}x, size: {self.size} (fixed), max_iter: {self.current_max_iter}")
        print(f"Normalized to square: X={new_x_range}, Y={new_y_range}")
        
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


def on_select(eclick, erelease, fig, ax):
    """
    Callback-функция для обработки выбора области
    
    Args:
        eclick: событие начала выбора
        erelease: событие завершения выбора
        fig: figure объект
        ax: axes, на котором сделан выбор
    """
    # Получаем координаты в данных
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    
    # Проверяем минимальный размер области
    if abs(x2 - x1) < 0.01 or abs(y2 - y1) < 0.01:
        print("Selected area is too small, ignoring")
        return
    
    # Нормализуем координаты (x1 < x2, y1 < y2)
    x_min, x_max = min(x1, x2), max(x1, x2)
    y_min, y_max = min(y1, y2), max(y1, y2)
    
    # Сохраняем выбранные координаты в состоянии
    fig.state['selected_area'] = {
        'x_range': (x_min, x_max),
        'y_range': (y_min, y_max),
        'ax_idx': ax.idx
    }
    
    print(f"\nSelected area on axes {ax.idx}:")
    print(f"  X: [{x_min:.4f}, {x_max:.4f}]")
    print(f"  Y: [{y_min:.4f}, {y_max:.4f}]")
    print(f"  Width: {x_max - x_min:.4f}, Height: {y_max - y_min:.4f}")
    
    # Отключаем RectangleSelector после выбора
    for selector in fig.state['selectors']:
        selector.set_active(False)
    
    print("\nSelection complete. Press Enter to continue...")


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
        'buttons': {},
        'selected_area': None
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
        
        # Создаем RectangleSelector для каждого axes
        selector = RectangleSelector(
            ax,
            lambda eclick, erelease, ax=ax: on_select(eclick, erelease, fig, ax),
            button=[1],  # только левая кнопка мыши
            interactive=False,  # нельзя перемещать/изменять после создания
            useblit=True,  # для производительности
            props=dict(facecolor='red', edgecolor='red', alpha=0.3, fill=True)
        )
        fig.state['selectors'].append(selector)
    
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
    
    # Начальная визуализация
    fig, axes = Visualise(julia_vizs, (1, 3))
    
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("="*60)
    print("1. Draw a rectangle on any of the three images")
    print("2. Use left mouse button to select area")
    print("3. After selection, press Enter to continue")
    print("="*60 + "\n")
    
    # Ждем выбора области
    input()
    
    # Проверяем, была ли выбрана область
    if fig.state['selected_area'] is None:
        print("No area was selected!")
        plt.close(fig)
        return
    
    # Получаем информацию о выбранной области
    selected = fig.state['selected_area']
    ax_idx = selected['ax_idx']
    x_range_new = selected['x_range']
    y_range_new = selected['y_range']
    
    print(f"\nApplying zoom to axes {ax_idx}...")
    
    # Применяем зум к выбранному объекту
    julia_vizs[ax_idx].zoom(x_range_new, y_range_new)
    
    # Обновляем визуализацию
    update_visualization(fig, axes, julia_vizs)
    
    # Финальная пауза
    print("\nZoom applied. Press Enter to exit...")
    input()
    plt.close(fig)


if __name__ == "__main__":
    main()
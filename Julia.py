import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import RectangleSelector, Button
import numpy as np

MAX_ITER = 1000
START_ITER = 200
SIZE = 512

class JuliaVisualization:
    """Класс для управления визуализацией множества Жюлиа"""
    
    def __init__(self, c, x_range, y_range, size=SIZE, max_iter=START_ITER):
        self.c = c
        self.size = size
        
        self.original_x_range = x_range
        self.original_y_range = y_range
        self.original_max_iter = max_iter
        
        self.current_x_range = x_range
        self.current_y_range = y_range
        self.current_max_iter = max_iter
        
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
    
    def _normalize_to_square(self, x_range, y_range):
        """Приведение выбранной области к квадратному виду"""
        width = x_range[1] - x_range[0]
        height = y_range[1] - y_range[0]
        
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2
        
        max_side = max(width, height)
        
        new_x_range = (x_center - max_side / 2, x_center + max_side / 2)
        new_y_range = (y_center - max_side / 2, y_center + max_side / 2)
        
        return new_x_range, new_y_range
    
    def zoom(self, new_x_range, new_y_range):
        """Зум в указанную область"""
        # Приводим к квадратному виду
        new_x_range, new_y_range = self._normalize_to_square(new_x_range, new_y_range)
        
        original_width = self.original_x_range[1] - self.original_x_range[0]
        new_width = new_x_range[1] - new_x_range[0]
        zoom_level = original_width / new_width
        
        self.current_max_iter = min(int(self.original_max_iter * np.log2(zoom_level + 1)), MAX_ITER)
        
        self.current_x_range = new_x_range
        self.current_y_range = new_y_range
        
        self.output = self._calculate()
        
        print(f"Zoom level: {zoom_level:.2f}x, size: {self.size} (fixed), max_iter: {self.current_max_iter}")
    
    def reset(self):
        """Сброс к исходным параметрам"""
        self.current_x_range = self.original_x_range
        self.current_y_range = self.original_y_range
        self.current_max_iter = self.original_max_iter
        self.output = self._calculate()
        print("Reset to original view")


def on_select(eclick, erelease, fig, ax):
    """Callback-функция для обработки выбора области"""
    # Если уже в режиме одного изображения, используем другую логику
    if fig.state['mode'] == 'one':
        on_select_in_one_mode(eclick, erelease, fig, ax)
        return
    
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    
    if abs(x2 - x1) < 0.01 or abs(y2 - y1) < 0.01:
        print("Selected area is too small, ignoring")
        return
    
    x_min, x_max = min(x1, x2), max(x1, x2)
    y_min, y_max = min(y1, y2), max(y1, y2)
    
    fig.state['selected_area'] = {
        'x_range': (x_min, x_max),
        'y_range': (y_min, y_max),
        'ax_idx': ax.idx
    }
    
    print(f"\nSelected area on axes {ax.idx}:")
    print(f"  X: [{x_min:.4f}, {x_max:.4f}]")
    print(f"  Y: [{y_min:.4f}, {y_max:.4f}]")
    
    # Отключаем RectangleSelector после выбора
    for selector in fig.state['selectors']:
        selector.set_active(False)
    
    # Переходим в режим одного изображения
    switch_to_one_mode(fig, ax.idx)

def on_select_in_one_mode(eclick, erelease, fig, ax):
    """Обработка выбора в режиме одного изображения"""
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    
    current_viz = fig.state['current_viz']
    
    # Вычисляем текущий zoom_level
    original_width = current_viz.original_x_range[1] - current_viz.original_x_range[0]
    current_width = current_viz.current_x_range[1] - current_viz.current_x_range[0]
    current_zoom_level = original_width / current_width
    
    # Вычисляем zoom_level выбранной области
    selected_width = abs(x2 - x1)
    new_zoom_level = original_width / selected_width
    
    # Проверяем, достигнут ли максимальный zoom
    if current_viz.current_max_iter >= MAX_ITER:
        print(f"Maximum zoom reached (max_iter = {MAX_ITER}). Cannot zoom further.")
        return
    
    # Проверяем минимальный размер области
    if selected_width < 0.001 or abs(y2 - y1) < 0.001:
        print("Selected area is too small, ignoring")
        return
    
    # Проверяем, не превысит ли новый zoom максимальный
    if new_zoom_level > current_zoom_level * 10:  # Ограничиваем разовый зум в 10 раз
        print(f"Zoom too aggressive. Please select a larger area.")
        return
    
    x_min, x_max = min(x1, x2), max(x1, x2)
    y_min, y_max = min(y1, y2), max(y1, y2)
    
    # Применяем зум
    current_viz.zoom((x_min, x_max), (y_min, y_max))
    
    # Обновляем визуализацию
    update_single_visualization(fig, ax)
    
    print(f"Zoom applied in single mode")
    """Обработка выбора в режиме одного изображения"""
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    
    if abs(x2 - x1) < 0.01 or abs(y2 - y1) < 0.01:
        print("Selected area is too small, ignoring")
        return
    
    x_min, x_max = min(x1, x2), max(x1, x2)
    y_min, y_max = min(y1, y2), max(y1, y2)
    
    # Применяем зум к текущему объекту
    current_viz = fig.state['current_viz']
    current_viz.zoom((x_min, x_max), (y_min, y_max))
    
    # Обновляем визуализацию
    update_single_visualization(fig, ax)
    
    print(f"Zoom applied in single mode")

def switch_to_one_mode(fig, ax_idx):
    """Переход в режим одного изображения"""
    print(f"\nSwitching to single image mode (axes {ax_idx})...")
    
    # Получаем выбранные координаты
    selected = fig.state['selected_area']
    x_range_new = selected['x_range']
    y_range_new = selected['y_range']
    
    # Получаем текущий axes и его визуализацию
    current_ax = fig.state['all_axes'][ax_idx]
    current_viz = fig.state['all_julia_vizs'][ax_idx]
    
    # Применяем зум
    current_viz.zoom(x_range_new, y_range_new)
    
    # Скрываем все axes
    for ax in fig.state['all_axes']:
        ax.set_visible(False)
    
    # Показываем только выбранный axes
    current_ax.set_visible(True)
    
    # Изменяем позицию axes (оставляем место для colorbar справа)
    current_ax.set_position([0.1, 0.15, 0.75, 0.75])
    
    # Перерисовываем изображение
    current_ax.clear()
    im = current_ax.imshow(
        current_viz.output,
        cmap='inferno',
        extent=[*current_viz.current_x_range, *current_viz.current_y_range],
        origin='lower',
        norm=mcolors.LogNorm()
    )
    current_ax.set_xlabel('Real')
    current_ax.set_ylabel('Imaginary')
    current_ax.set_title(f'c = {current_viz.c}')
    
    # Сохраняем ссылки
    current_ax.julia_viz = current_viz
    current_ax.idx = ax_idx
    
    # Создаем новый colorbar справа
    create_colorbar_single_mode(fig, current_ax, current_viz)
    
    # Обновляем состояние
    fig.state['mode'] = 'one'
    fig.state['current_viz'] = current_viz
    fig.state['current_ax'] = current_ax
    
    # Удаляем старые selectors
    for selector in fig.state['selectors']:
        selector.set_active(False)
    fig.state['selectors'] = []
    
    # Создаем новый RectangleSelector
    selector = RectangleSelector(
        current_ax,
        lambda eclick, erelease: on_select(eclick, erelease, fig, current_ax),
        button=[1],
        interactive=False,
        useblit=True,
        props=dict(facecolor='red', edgecolor='red', alpha=0.3, fill=True)
    )
    fig.state['selectors'].append(selector)
    
    # Показываем кнопки
    for btn in fig.state['buttons'].values():
        btn.ax.set_visible(True)
    
    # Обновляем canvas
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    print("Switched to single image mode")

def remove_colorbar(fig):
    """Удаление colorbar из figure"""
    if hasattr(fig, '_colorbar') and fig._colorbar is not None:
        fig._colorbar.remove()
        fig._colorbar = None
    # Также удаляем все colorbar axes
    for ax in fig.axes[:]:
        if hasattr(ax, '_colorbar_info'):
            ax.remove()

def create_colorbar_single_mode(fig, ax, viz):
    """Создание colorbar для режима одного изображения (справа)"""
    remove_colorbar(fig)
    
    # Вычисляем реальное минимальное значение из данных
    vmin = max(1, int(np.min(viz.output)))  # vmin должен быть >= 1 для LogNorm
    vmax = viz.current_max_iter
    
    # Создаем новый axes для colorbar справа
    cax = fig.add_axes([0.92, 0.25, 0.02, 0.65])
    
    # Создаем mappable для colorbar с реальными vmin/vmax
    mappable = plt.cm.ScalarMappable(
        norm=mcolors.LogNorm(vmin=vmin, vmax=vmax),
        cmap='inferno'
    )
    
    # Создаем colorbar
    cbar = fig.colorbar(mappable, cax=cax, orientation='vertical')
    cbar.set_label('Number of iterations')
    
    # Сохраняем ссылку
    fig._colorbar = cbar
    fig._colorbar_ax = cax
    
    return cbar


def create_colorbar_three_mode(fig, axes):
    """Создание colorbar для режима трех изображений (снизу)"""
    remove_colorbar(fig)
    
    # Вычисляем реальные min/max из первого изображения
    first_viz = axes[0].julia_viz
    vmin = max(1, int(np.min(first_viz.output)))
    vmax = first_viz.current_max_iter
    
    # Создаем axes для colorbar явно
    cax = fig.add_axes([0.15, 0.08, 0.7, 0.03])
    
    # Создаем mappable для colorbar с реальными vmin/vmax
    mappable = plt.cm.ScalarMappable(
        norm=mcolors.LogNorm(vmin=vmin, vmax=vmax),
        cmap='inferno'
    )
    
    # Создаем colorbar с явным указанием cax
    cbar = fig.colorbar(mappable, cax=cax, orientation='horizontal')
    cbar.set_label('Number of iterations')
    
    # Сохраняем ссылку
    fig._colorbar = cbar
    fig._colorbar_ax = cax
    
    return cbar


def reset_zoom(event, fig):
    """Обработчик кнопки сброса зума"""
    if fig.state['mode'] != 'one':
        return
    
    current_viz = fig.state['current_viz']
    current_ax = fig.state['current_ax']
    
    # Сбрасываем к исходным параметрам
    current_viz.reset()
    
    # Обновляем визуализацию
    update_single_visualization(fig, current_ax)
    
    print("Zoom reset to original view")

def back_to_three(event, fig):
    """Обработчик кнопки возврата к трем изображениям"""
    if fig.state['mode'] != 'one':
        return
    
    print("\nSwitching back to three images mode...")
    
    # Скрываем кнопки
    for btn in fig.state['buttons'].values():
        btn.ax.set_visible(False)
    
    # Сбрасываем все визуализации
    for viz in fig.state['all_julia_vizs']:
        viz.reset()
    
    # Восстанавливаем все axes
    for idx, ax in enumerate(fig.state['all_axes']):
        ax.set_visible(True)
        ax.set_position(fig.state['original_positions'][idx])
        
        viz = fig.state['all_julia_vizs'][idx]
        ax.clear()
        ax.imshow(
            viz.output,
            cmap='inferno',
            extent=[*viz.current_x_range, *viz.current_y_range],
            origin='lower',
            norm=mcolors.LogNorm()
        )
        ax.set_xlabel('Real')
        ax.set_ylabel('Imaginary')
        ax.set_title(f'c = {viz.c}')
        
        ax.julia_viz = viz
        ax.idx = idx
    
    # Восстанавливаем отступы
    adj = fig.state['original_subplots_adjust']
    fig.subplots_adjust(bottom=adj['bottom'], left=adj['left'], right=adj['right'])
    
    # Создаем новый colorbar снизу
    create_colorbar_three_mode(fig, fig.state['all_axes'])
    
    # Пересоздаем RectangleSelector'ы
    for selector in fig.state['selectors']:
        selector.set_active(False)
    fig.state['selectors'] = []
    
    for ax in fig.state['all_axes']:
        selector = RectangleSelector(
            ax,
            lambda eclick, erelease, ax=ax: on_select(eclick, erelease, fig, ax),
            button=[1],
            interactive=False,
            useblit=True,
            props=dict(facecolor='red', edgecolor='red', alpha=0.3, fill=True)
        )
        fig.state['selectors'].append(selector)
    
    # Обновляем состояние
    fig.state['mode'] = 'three'
    fig.state['current_viz'] = None
    fig.state['current_ax'] = None
    
    # Обновляем canvas
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    print("Switched back to three images mode")

def update_single_visualization(fig, ax):
    """Обновление визуализации в режиме одного изображения"""
    viz = ax.julia_viz
    
    ax.clear()
    im = ax.imshow(
        viz.output,
        cmap='inferno',
        extent=[*viz.current_x_range, *viz.current_y_range],
        origin='lower',
        norm=mcolors.LogNorm()
    )
    ax.set_xlabel('Real')
    ax.set_ylabel('Imaginary')
    ax.set_title(f'c = {viz.c}')
    
    # Обновляем colorbar с новыми параметрами
    create_colorbar_single_mode(fig, ax, viz)
    
    fig.canvas.draw()
    fig.canvas.flush_events()

def Visualise(julia_vizs, shape=None):
    """Визуализация списка объектов JuliaVisualization"""
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
        'selected_area': None,
        'all_axes': axes,
        'all_julia_vizs': julia_vizs
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
        
        ax.julia_viz = julia_viz
        ax.idx = idx
        
        # Создаем RectangleSelector для каждого axes
        selector = RectangleSelector(
            ax,
            lambda eclick, erelease, ax=ax: on_select(eclick, erelease, fig, ax),
            button=[1],
            interactive=False,
            useblit=True,
            props=dict(facecolor='red', edgecolor='red', alpha=0.3, fill=True)
        )
        fig.state['selectors'].append(selector)
    
    create_colorbar_three_mode(fig, fig.state['all_axes'])

    plt.subplots_adjust(bottom=0.37, left=0.05, right=0.95)
    
    # сохраняем исходные позиции и параметры
    fig.state['original_positions'] = [ax.get_position() for ax in axes]
    fig.state['original_subplots_adjust'] = {
        'bottom': 0.37, 'left': 0.05, 'right': 0.95
    }
    
    # Создаем кнопки управления (скрытые по умолчанию)
    ax_reset = fig.add_axes([0.7, 0.05, 0.1, 0.075])
    ax_back = fig.add_axes([0.81, 0.05, 0.1, 0.075])
    
    btn_reset = Button(ax_reset, 'Reset Zoom')
    btn_back = Button(ax_back, 'Back to 3 Views')
    
    # Скрываем кнопки в начальном режиме
    ax_reset.set_visible(False)
    ax_back.set_visible(False)
    
    # Сохраняем кнопки в состоянии
    fig.state['buttons']['reset'] = btn_reset
    fig.state['buttons']['back'] = btn_back
    
    # Привязываем обработчики
    btn_reset.on_clicked(lambda event: reset_zoom(event, fig))
    btn_back.on_clicked(lambda event: back_to_three(event, fig))
    
    plt.show(block=False)
    
    return fig, axes


def main():
    x_range = (-1.5, 1.5)
    y_range = (-1.5, 1.5)
    Cs = [-0.8 + 0.156j, -0.4 + 0.6j, 0.285 + 0.01j]
    
    julia_vizs = [JuliaVisualization(c, x_range, y_range, size=SIZE, max_iter=START_ITER) 
                  for c in Cs]
    
    fig, axes = Visualise(julia_vizs, (1, 3))
    
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("="*60)
    print("1. Draw a rectangle on any of the three images")
    print("2. The selected image will zoom and expand")
    print("3. You can zoom further in single image mode")
    print("4. Use 'Reset Zoom' button to reset current image")
    print("5. Use 'Back to 3 Views' button to return to initial view")
    print("="*60 + "\n")
    
    # Блокируем выполнение, чтобы окно оставалось открытым
    plt.show()


if __name__ == "__main__":
    main()
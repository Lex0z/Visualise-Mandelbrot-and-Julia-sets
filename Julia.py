import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import RectangleSelector, Button
import numpy as np

# ============================================================================
# КОНСТАНТЫ КОНФИГУРАЦИИ
# ============================================================================

class Config:
    """Конфигурация визуализации"""
    # Параметры вычислений
    MAX_ITER = 700
    START_ITER = 200
    SIZE = 400
    
    # Начальные диапазоны
    X_RANGE = (-1.5, 1.5)
    Y_RANGE = (-1.5, 1.5)
    
    # Значения C для визуализации
    C_VALUES = [-0.8 + 0.156j, -0.4 + 0.6j, 0.285 + 0.01j]
    
    # Цветовая схема
    COLORMAP = 'inferno'
    
    # Размеры и позиции
    FIGURE_SIZE = (15, 7)
    
    # Позиции axes в режиме трех изображений
    AXES_POSITIONS_THREE = [
        [0.05, 0.25, 0.28, 0.65],  # первое
        [0.36, 0.25, 0.28, 0.65],  # второе
        [0.67, 0.25, 0.28, 0.65]   # третье
    ]
    
    # Позиция axes в режиме одного изображения
    AXES_POSITION_SINGLE = [0.1, 0.15, 0.75, 0.75]
    
    # Позиции colorbar
    COLORBAR_SINGLE_POSITION = [0.92, 0.25, 0.02, 0.65]  # справа
    COLORBAR_THREE_POSITION = [0.15, 0.08, 0.7, 0.03]    # снизу
    
    # Позиции кнопок
    BUTTON_RESET_POSITION = [0.7, 0.05, 0.1, 0.075]
    BUTTON_BACK_POSITION = [0.81, 0.05, 0.1, 0.075]
    
    # Отступы subplots
    SUBPLOTS_ADJUST = {
        'bottom': 0.37,
        'left': 0.05,
        'right': 0.95
    }
    
    # Стили RectangleSelector
    SELECTOR_PROPS = {
        'facecolor': 'red',
        'edgecolor': 'red',
        'alpha': 0.3,
        'fill': True
    }
    
    # Ограничения зума
    MIN_SELECTION_SIZE_THREE = 0.01
    MIN_SELECTION_SIZE_SINGLE = 0.001
    MAX_ZOOM_FACTOR = 10


# ============================================================================
# MODEL - Данные и вычисления
# ============================================================================

class JuliaVisualization:
    """Model: Управление данными множества Жюлиа"""
    
    def __init__(self, c, x_range, y_range, size=Config.SIZE, max_iter=Config.START_ITER):
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
        """Вычисление множества Жюлиа"""
        try:
            x_min, x_max = self.current_x_range
            y_min, y_max = self.current_y_range
            
            if x_min >= x_max or y_min >= y_max:
                raise ValueError(f"Invalid ranges: x={self.current_x_range}, y={self.current_y_range}")
            
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
                
                if not np.all(np.isfinite(Z)):
                    print(f"Warning: Numerical overflow detected at iteration {i}")
                    break
            
            return output
            
        except MemoryError as e:
            print(f"ERROR: Out of memory during calculation: {e}")
            return np.ones((self.size, self.size))
        except Exception as e:
            print(f"ERROR: Calculation failed: {e}")
            return np.ones((self.size, self.size))
    
    def _normalize_to_square(self, x_range, y_range):
        """Приведение к квадратному виду"""
        width = x_range[1] - x_range[0]
        height = y_range[1] - y_range[0]
        
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2
        
        max_side = max(width, height)
        
        new_x_range = (x_center - max_side / 2, x_center + max_side / 2)
        new_y_range = (y_center - max_side / 2, y_center + max_side / 2)
        
        return new_x_range, new_y_range
    
    def zoom(self, new_x_range, new_y_range):
        """Зум в область"""
        try:
            new_x_range, new_y_range = self._normalize_to_square(new_x_range, new_y_range)
            
            if new_x_range[0] >= new_x_range[1] or new_y_range[0] >= new_y_range[1]:
                raise ValueError(f"Invalid zoom ranges: x={new_x_range}, y={new_y_range}")
            
            original_width = self.original_x_range[1] - self.original_x_range[0]
            new_width = new_x_range[1] - new_x_range[0]
            
            if new_width <= 0:
                raise ValueError("Zoom width must be positive")
            
            zoom_level = original_width / new_width
            
            self.current_max_iter = min(
                int(self.original_max_iter * np.log2(zoom_level + 1)), 
                Config.MAX_ITER
            )
            
            self.current_x_range = new_x_range
            self.current_y_range = new_y_range
            
            self.output = self._calculate()
            
            print(f"Zoom level: {zoom_level:.2f}x, size: {self.size} (fixed), max_iter: {self.current_max_iter}")
            
        except ValueError as e:
            print(f"ERROR: Invalid zoom parameters: {e}")
        except Exception as e:
            print(f"ERROR: Zoom failed: {e}")
    
    def reset(self):
        """Сброс к исходным параметрам"""
        self.current_x_range = self.original_x_range
        self.current_y_range = self.original_y_range
        self.current_max_iter = self.original_max_iter
        self.output = self._calculate()
        print("Reset to original view")


# ============================================================================
# VIEW - Отрисовка и UI
# ============================================================================

class JuliaView:
    """View: Управление визуализацией"""
    
    def __init__(self, julia_models):
        self.models = julia_models
        self.fig = None
        self.axes = None
        self.selectors = []
        self.buttons = {}
        
        self._setup_figure()
        self._create_visualization()
        self._create_buttons()
    
    def _setup_figure(self):
        """Инициализация figure"""
        self.fig, self.axes = plt.subplots(
            1, 
            len(self.models), 
            figsize=Config.FIGURE_SIZE
        )
    
    def _create_visualization(self):
        """Создание начальной визуализации"""
        for idx, (ax, model) in enumerate(zip(self.axes, self.models)):
            im = ax.imshow(
                model.output,
                cmap=Config.COLORMAP,
                extent=[*model.current_x_range, *model.current_y_range],
                origin='lower',
                norm=mcolors.LogNorm()
            )
            ax.set_xlabel('Real')
            ax.set_ylabel('Imaginary')
            ax.set_title(f'c = {model.c}')
            
            ax.julia_model = model
            ax.idx = idx
            
            # Создаем RectangleSelector
            selector = RectangleSelector(
                ax,
                lambda eclick, erelease, ax=ax: self.controller.on_select(eclick, erelease, ax),
                button=[1],
                interactive=False,
                useblit=True,
                props=Config.SELECTOR_PROPS
            )
            self.selectors.append(selector)
        
        self._create_colorbar_three_mode()
        
        plt.subplots_adjust(**Config.SUBPLOTS_ADJUST)
        
        # Сохраняем исходные позиции
        self.original_positions = [ax.get_position() for ax in self.axes]
        self.original_subplots_adjust = Config.SUBPLOTS_ADJUST.copy()
    
    def _create_buttons(self):
        """Создание кнопок управления"""
        ax_reset = self.fig.add_axes(Config.BUTTON_RESET_POSITION)
        ax_back = self.fig.add_axes(Config.BUTTON_BACK_POSITION)
        
        self.buttons['reset'] = Button(ax_reset, 'Reset Zoom')
        self.buttons['back'] = Button(ax_back, 'Back to 3 Views')
        
        # Скрываем кнопки
        ax_reset.set_visible(False)
        ax_back.set_visible(False)
        
        # Привязываем обработчики
        self.buttons['reset'].on_clicked(lambda event: self.controller.reset_zoom())
        self.buttons['back'].on_clicked(lambda event: self.controller.back_to_three())
    
    def set_controller(self, controller):
        """Установка контроллера"""
        self.controller = controller
    
    def switch_to_single_mode(self, ax_idx):
        """Переключение в режим одного изображения"""
        # Скрываем все axes
        for ax in self.axes:
            ax.set_visible(False)
        
        # Показываем выбранный
        current_ax = self.axes[ax_idx]
        current_ax.set_visible(True)
        current_ax.set_position(Config.AXES_POSITION_SINGLE)
        
        # Обновляем изображение
        self._update_single_axes(current_ax)
        
        # Создаем colorbar
        self._create_colorbar_single_mode(current_ax)
        
        # Пересоздаем selector
        self._recreate_selector_single(current_ax)
        
        # Показываем кнопки
        for btn in self.buttons.values():
            btn.ax.set_visible(True)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def switch_to_three_mode(self):
        """Переключение в режим трех изображений"""
        # Скрываем кнопки
        for btn in self.buttons.values():
            btn.ax.set_visible(False)
        
        # Восстанавливаем все axes
        for idx, ax in enumerate(self.axes):
            ax.set_visible(True)
            ax.set_position(self.original_positions[idx])
            
            model = self.models[idx]
            ax.clear()
            ax.imshow(
                model.output,
                cmap=Config.COLORMAP,
                extent=[*model.current_x_range, *model.current_y_range],
                origin='lower',
                norm=mcolors.LogNorm()
            )
            ax.set_xlabel('Real')
            ax.set_ylabel('Imaginary')
            ax.set_title(f'c = {model.c}')
            
            ax.julia_model = model
            ax.idx = idx
        
        # Восстанавливаем отступы
        self.fig.subplots_adjust(**self.original_subplots_adjust)
        
        # Создаем colorbar
        self._create_colorbar_three_mode()
        
        # Пересоздаем selectors
        self._recreate_selectors_three()
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def update_single_visualization(self, ax):
        """Обновление визуализации в режиме одного изображения"""
        self._update_single_axes(ax)
        self._create_colorbar_single_mode(ax)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def _update_single_axes(self, ax):
        """Обновление axes в режиме одного изображения"""
        model = ax.julia_model
        
        ax.clear()
        ax.imshow(
            model.output,
            cmap=Config.COLORMAP,
            extent=[*model.current_x_range, *model.current_y_range],
            origin='lower',
            norm=mcolors.LogNorm()
        )
        ax.set_xlabel('Real')
        ax.set_ylabel('Imaginary')
        ax.set_title(f'c = {model.c}')
    
    def _recreate_selector_single(self, ax):
        """Пересоздание selector для режима одного изображения"""
        for selector in self.selectors:
            try:
                selector.set_active(False)
            except Exception as e:
                print(f"Warning: Could not deactivate selector: {e}")
        
        self.selectors = []
        
        selector = RectangleSelector(
            ax,
            lambda eclick, erelease: self.controller.on_select(eclick, erelease, ax),
            button=[1],
            interactive=False,
            useblit=True,
            props=Config.SELECTOR_PROPS
        )
        self.selectors.append(selector)
    
    def _recreate_selectors_three(self):
        """Пересоздание selectors для режима трех изображений"""
        for selector in self.selectors:
            try:
                selector.set_active(False)
            except Exception as e:
                print(f"Warning: Could not deactivate selector: {e}")
        
        self.selectors = []
        
        for ax in self.axes:
            selector = RectangleSelector(
                ax,
                lambda eclick, erelease, ax=ax: self.controller.on_select(eclick, erelease, ax),
                button=[1],
                interactive=False,
                useblit=True,
                props=Config.SELECTOR_PROPS
            )
            self.selectors.append(selector)
    
    def _remove_colorbar(self):
        """Удаление colorbar"""
        try:
            if hasattr(self.fig, '_colorbar') and self.fig._colorbar is not None:
                try:
                    self.fig._colorbar.remove()
                except Exception as e:
                    print(f"Warning: Could not remove colorbar: {e}")
                self.fig._colorbar = None
            
            for ax in self.fig.axes[:]:
                if hasattr(ax, '_colorbar_info'):
                    try:
                        ax.remove()
                    except Exception as e:
                        print(f"Warning: Could not remove colorbar axes: {e}")
        except Exception as e:
            print(f"ERROR: Failed to remove colorbar: {e}")
    
    def _create_colorbar_single_mode(self, ax):
        """Создание colorbar для режима одного изображения"""
        try:
            self._remove_colorbar()
            
            model = ax.julia_model
            vmin = max(1, int(np.min(model.output)))
            vmax = model.current_max_iter
            
            if vmin >= vmax:
                print(f"Warning: Invalid colorbar range [{vmin}, {vmax}], adjusting")
                vmax = vmin + 1
            
            cax = self.fig.add_axes(Config.COLORBAR_SINGLE_POSITION)
            
            mappable = plt.cm.ScalarMappable(
                norm=mcolors.LogNorm(vmin=vmin, vmax=vmax),
                cmap=Config.COLORMAP
            )
            
            cbar = self.fig.colorbar(mappable, cax=cax, orientation='vertical')
            cbar.set_label('Number of iterations')
            
            self.fig._colorbar = cbar
            self.fig._colorbar_ax = cax
            
        except Exception as e:
            print(f"ERROR: Failed to create single mode colorbar: {e}")
    
    def _create_colorbar_three_mode(self):
        """Создание colorbar для режима трех изображений"""
        try:
            self._remove_colorbar()
            
            first_model = self.axes[0].julia_model
            vmin = max(1, int(np.min(first_model.output)))
            vmax = first_model.current_max_iter
            
            if vmin >= vmax:
                print(f"Warning: Invalid colorbar range [{vmin}, {vmax}], adjusting")
                vmax = vmin + 1
            
            cax = self.fig.add_axes(Config.COLORBAR_THREE_POSITION)
            
            mappable = plt.cm.ScalarMappable(
                norm=mcolors.LogNorm(vmin=vmin, vmax=vmax),
                cmap=Config.COLORMAP
            )
            
            cbar = self.fig.colorbar(mappable, cax=cax, orientation='horizontal')
            cbar.set_label('Number of iterations')
            
            self.fig._colorbar = cbar
            self.fig._colorbar_ax = cax
            
        except Exception as e:
            print(f"ERROR: Failed to create three mode colorbar: {e}")
    
    def show(self):
        """Показать figure"""
        plt.show(block=False)
    
    def show_blocking(self):
        """Показать figure с блокировкой"""
        plt.show()


# ============================================================================
# CONTROLLER - Логика управления
# ============================================================================

class JuliaController:
    """Controller: Обработка событий и управление состоянием"""
    
    def __init__(self, view):
        self.view = view
        self.mode = 'three'  # 'three' или 'one'
        self.current_model = None
        self.current_ax = None
        self.selected_area = None
    
    def on_select(self, eclick, erelease, ax):
        """Обработка выбора области"""
        if self.mode == 'one':
            self._on_select_in_one_mode(eclick, erelease, ax)
        else:
            self._on_select_in_three_mode(eclick, erelease, ax)
    
    def _on_select_in_three_mode(self, eclick, erelease, ax):
        """Обработка выбора в режиме трех изображений"""
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        
        if abs(x2 - x1) < Config.MIN_SELECTION_SIZE_THREE or abs(y2 - y1) < Config.MIN_SELECTION_SIZE_THREE:
            print("Selected area is too small, ignoring")
            return
        
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)
        
        self.selected_area = {
            'x_range': (x_min, x_max),
            'y_range': (y_min, y_max),
            'ax_idx': ax.idx
        }
        
        print(f"\nSelected area on axes {ax.idx}:")
        print(f"  X: [{x_min:.4f}, {x_max:.4f}]")
        print(f"  Y: [{y_min:.4f}, {y_max:.4f}]")
        
        # Отключаем selectors
        for selector in self.view.selectors:
            selector.set_active(False)
        
        # Переходим в режим одного изображения
        self._switch_to_one_mode(ax.idx)
    
    def _on_select_in_one_mode(self, eclick, erelease, ax):
        """Обработка выбора в режиме одного изображения"""
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        
        model = self.current_model
        
        # Вычисляем текущий zoom_level
        original_width = model.original_x_range[1] - model.original_x_range[0]
        current_width = model.current_x_range[1] - model.current_x_range[0]
        current_zoom_level = original_width / current_width
        
        # Вычисляем zoom_level выбранной области
        selected_width = abs(x2 - x1)
        new_zoom_level = original_width / selected_width
        
        # Проверяем ограничения
        if model.current_max_iter >= Config.MAX_ITER:
            print(f"Maximum zoom reached (max_iter = {Config.MAX_ITER}). Cannot zoom further.")
            return
        
        if selected_width < Config.MIN_SELECTION_SIZE_SINGLE or abs(y2 - y1) < Config.MIN_SELECTION_SIZE_SINGLE:
            print("Selected area is too small, ignoring")
            return
        
        if new_zoom_level > current_zoom_level * Config.MAX_ZOOM_FACTOR:
            print(f"Zoom too aggressive. Please select a larger area.")
            return
        
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)
        
        # Применяем зум
        model.zoom((x_min, x_max), (y_min, y_max))
        
        # Обновляем визуализацию
        self.view.update_single_visualization(ax)
        
        print(f"Zoom applied in single mode")
    
    def _switch_to_one_mode(self, ax_idx):
        """Переход в режим одного изображения"""
        try:
            print(f"\nSwitching to single image mode (axes {ax_idx})...")
            
            if self.selected_area is None:
                print("ERROR: No area selected")
                return
            
            x_range_new = self.selected_area['x_range']
            y_range_new = self.selected_area['y_range']
            
            current_ax = self.view.axes[ax_idx]
            current_model = self.view.models[ax_idx]
            
            # Применяем зум
            current_model.zoom(x_range_new, y_range_new)
            
            # Обновляем состояние
            self.mode = 'one'
            self.current_model = current_model
            self.current_ax = current_ax
            
            # Переключаем view
            self.view.switch_to_single_mode(ax_idx)
            
            print("Switched to single image mode")
            
        except Exception as e:
            print(f"ERROR: Failed to switch to single mode: {e}")
            self.mode = 'three'
    
    def reset_zoom(self):
        """Сброс зума"""
        if self.mode != 'one':
            return
        
        self.current_model.reset()
        self.view.update_single_visualization(self.current_ax)
        print("Zoom reset to original view")
    
    def back_to_three(self):
        """Возврат к трем изображениям"""
        if self.mode != 'one':
            return
        
        print("\nSwitching back to three images mode...")
        
        # Сбрасываем все модели
        for model in self.view.models:
            model.reset()
        
        # Обновляем состояние
        self.mode = 'three'
        self.current_model = None
        self.current_ax = None
        
        # Переключаем view
        self.view.switch_to_three_mode()
        
        print("Switched back to three images mode")


# ============================================================================
# MAIN
# ============================================================================

def main():
    # Создаем модели
    models = [
        JuliaVisualization(c, Config.X_RANGE, Config.Y_RANGE) 
        for c in Config.C_VALUES
    ]
    
    # Создаем View
    view = JuliaView(models)
    
    # Создаем Controller
    controller = JuliaController(view)
    
    # Связываем View и Controller
    view.set_controller(controller)
    
    # Инструкции
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("="*60)
    print("1. Draw a rectangle on any of the three images")
    print("2. The selected image will zoom and expand")
    print("3. You can zoom further in single image mode")
    print("4. Use 'Reset Zoom' button to reset current image")
    print("5. Use 'Back to 3 Views' button to return to initial view")
    print("="*60 + "\n")
    
    # Показываем figure
    view.show_blocking()


if __name__ == "__main__":
    main()
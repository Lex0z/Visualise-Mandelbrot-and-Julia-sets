import numpy as np
x = np.arange(12)

# Изменение формы массива
reshaped = x.reshape(3, 4)  # массив 3x4

# Превращение в "плоский" массив
flat = x.ravel()            # одномерный массив [0, 1, ..., 11]

# Транспонирование (для 2D массивов)
M = np.array([[1, 2], [3, 4]])
print(M.T)  # [[1, 3],
            #  [2, 4]]

# Объединение массивов
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6]])
v_stack = np.vstack([a, b])  # вертикальное объединение (по строкам)
h_stack = np.hstack([a, b.T]) # горизонтальное объединение (по столбцам)

print(v_stack)
print(h_stack)
import os

import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas

from src.db.database_handler import GammaHandler
from src.db.user_database_handler import UserDatabaseHandler


def get_palette():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'colors.sql')
    try:
        handler = GammaHandler(db_path)
        results = handler.select_palette()
        handler.teardown()
    except BaseException as e:
        print(f"Ошибка при доступе к базе данных: {e}")
        return {}

    return results


def get_user_palette(tg_id: int):
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'user_colors.sql')
    try:
        user_handler = UserDatabaseHandler(db_path)
        ids = user_handler.select_available_colors(tg_id)
        user_handler.teardown()

        gamma_handler = GammaHandler(db_path)
        results = dict()
        for gamma_id in ids:
            results[gamma_id] = gamma_handler.get_rgb(gamma_id)
        gamma_handler.teardown()
    except BaseException as e:
        print(f"Ошибка при доступе к базе данных: {e}")
        return {}

    return results


def closest_color(requested_color, palette, user_palette, alpha):
    """Находим ближайший цвет к нужному"""
    min_colors = {}
    for key, (r_c, g_c, b_c) in palette.items():
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd) * (alpha + 100) / 100] = key
    for key, (r_c, g_c, b_c) in user_palette.items():
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = key

    return min_colors[min(min_colors.keys())]


def resize_image(image, max_size):
    """Изменяем размер изображения."""
    image.thumbnail(max_size)
    return image


def get_average_color(block):
    """Нахождение усредненного цвета в блоке."""
    block = np.array(block)
    average_color = block.mean(axis=(0, 1)).astype(int)

    return tuple(average_color)


def closest_color_from_selected(requested_color, selected_colors, palette):
    """Находите ближайший цвет из выбранных цветов."""
    min_distance = float('inf')
    closest_color = None
    for color in selected_colors.keys():
        distance = sum((palette[color][i] - requested_color[i]) ** 2 for i in range(3))
        if distance < min_distance:
            min_distance = distance
            closest_color = color
    return closest_color


def create_color_scheme(image, grid_size, palette, user_palette, max_colors=None, alpha=1):
    """Создаем схему цветов для вышивки."""
    img_array = np.array(image)
    height, width = img_array.shape[:2]

    scheme = []
    color_counts = {}

    for y in range(0, height, grid_size):
        row = []
        for x in range(0, width, grid_size):
            block = img_array[y:y + grid_size, x:x + grid_size]
            avg_color = get_average_color(block)
            color_index = closest_color(avg_color, palette, user_palette, alpha)
            row.append(color_index)
            color_counts[color_index] = color_counts.get(color_index, 0) + 1

        scheme.append(row)

    if max_colors is not None:
        if len(color_counts) > max_colors:
            sorted_colors = sorted(color_counts.items(), key=lambda item: item[1], reverse=True)
            selected_colors = {color: count for color, count in sorted_colors[:max_colors]}
        else:
            selected_colors = color_counts

        for y in range(len(scheme)):
            for x in range(len(scheme[y])):
                color = scheme[y][x]
                if color not in selected_colors:
                    avg_color = np.array(palette[color])
                    clos_color = closest_color_from_selected(avg_color, selected_colors, palette)
                    if clos_color is not None:
                        scheme[y][x] = clos_color
                        color_counts[clos_color] = color_counts.get(clos_color, 0) + 1
                    else:
                        print(f"Не найдено близких цветов {color} в точке ({x}, {y})")

        color_counts = selected_colors

    return scheme, color_counts


def get_contrast_color(r, g, b):
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)

    if brightness > 186:
        return [0, 0, 0]
    else:
        return [1, 1, 1]


def save_scheme_to_pdf(scheme, color_counts, filename):
    """Сохраняем схему в PDF файл."""

    kitten_path = os.path.join(os.path.dirname(__file__), 'stock_image', 'kitten.png')
    scale = 18
    num_rows = len(scheme)
    num_cols = len(scheme[0]) if num_rows > 0 else 0

    unique_colors = list(color_counts.keys())
    color_indices = {color: index + 1 for index, color in enumerate(unique_colors)}

    c = canvas.Canvas(filename, pagesize=(num_cols * scale, num_rows * scale))

    for y, row in enumerate(scheme):
        for x, color in enumerate(row):
            r, g, b = get_palette()[color]
            c.setFillColorRGB(r / 255, g / 255, b / 255)
            c.rect(x * scale, (num_rows - y - 1) * scale, scale, scale, fill=True)
            color_number = str(color_indices[color])
            c.setFillColorRGB(get_contrast_color(r, g, b)[0], get_contrast_color(r, g, b)[1],
                              get_contrast_color(r, g, b)[2])
            c.setFont("Helvetica", 8)
            c.drawString(x * scale + scale / 4, (num_rows - y - 1) * scale + scale / 4, color_number)

    c.showPage()
    c.setFont("Helvetica", 20)
    page_width, page_height = num_cols * scale, num_rows * scale
    c.drawString(10, page_height - 40, "Color Descriptions:")
    y_offset = page_height - 60
    color_square_size = 20

    for index, (color, count) in enumerate(color_counts.items()):
        color_index = color_indices[color]
        description = f"Color count {color_index} (Gamma{color}) : {count}"
        x_offset = 10 if (index % 2 == 0) else page_width / 2

        r, g, b = get_palette()[color]
        c.setFillColorRGB(r / 255, g / 255, b / 255)
        c.rect(x_offset, y_offset - 8, color_square_size, color_square_size, fill=True)

        c.setFillColorRGB(0, 0, 0)
        text_x_offset = x_offset + color_square_size + 5
        c.drawString(text_x_offset, y_offset - 8, description)
        y_offset -= 15

        if y_offset < 50:
            c.showPage()
            c.setFont("Helvetica", 20)
            c.drawString(10, page_height - 40, "Color Descriptions:")
            y_offset = page_height - 60

        if (index + 1) % 2 == 0:
            y_offset -= 5

    c.showPage()
    c.drawImage(kitten_path, 0, 0, width = num_cols * scale, height = num_rows * scale)

    c.save()


def image_proc(image_path, output_pdf_path, tg_id: int, max_colors=None, max_size=(100, 100), grid_size=1, alpha=0):
    try:
        palette = get_palette()
        user_palette = get_user_palette(tg_id)
        image = Image.open(image_path)
        image = resize_image(image, max_size).convert('RGB')
        scheme, color_counts = create_color_scheme(image, grid_size, palette, user_palette, max_colors, alpha)
        save_scheme_to_pdf(scheme, color_counts, output_pdf_path)
    except Exception as e:
        print(f"Ошибка при обработке изображения: {e}")

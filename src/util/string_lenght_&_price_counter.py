import numpy as np
from collections import deque


def string_length_count(scale: float, dots_cnt: int, image: np.array, first_dot: list, color=()) -> float:
    done_dots = [first_dot]
    q = deque()
    s = float(0)
    image_height, image_length = image.shape
    max_length = min(image_length, image_height) / 10

    while dots_cnt:
        visited = [[-1 for j in range(image_length)] for i in range(image_height)]
        for i in done_dots:
            q.append(i)

        while q:
            x, y = map(int, q.popleft().split())

            if image[x][y] == color:
                s += scale * 4
                if visited[x][y] <= max_length:
                    s += visited[x][y] * scale
                break

            for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                if 0 <= x + dx < image_height and 0 <= y + dy < image_length and visited[x + dx][y + dy] == -1:
                    q.append([x + dx, y + dy])
                    visited[x + dx][y + dy] = visited[x][y]

        dots_cnt -= 1
        q.clear()

    return s

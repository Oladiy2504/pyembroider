import sqlite3
import os
from src.db.database_handler import Colors, GammaHandler

def strings_parsing(s : str) -> list:
    ans = []
    for i in s.split(','):
        color, length = map(int, i.split())
        try:
            color = int(color)
            length = int(length)
            ans.append([color, length])
        except:
            return []
    return ans

def conv_parsing(s : str) -> list:
    try:
        length, width = map(int, s.split())
        return [length, width]
    except:
        return []
    
def get_rgb_by_gamma(gamma_value: int):
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'user_colors.sql')
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT R, G, B FROM colors WHERE Gamma = :gamma_value")
            result = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Ошибка при доступе к базе данных: {e}")
        return []
    
    return [[row['R'], row['G'], row['B']] for row in result]
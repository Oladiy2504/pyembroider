import requests
from bs4 import BeautifulSoup
from src.db.database_handler import GammaHandler

url = "https://firma-gamma.ru/articles/colormap-muline/"


def hex_to_rgb(hex: str) -> list[int]:
    """
    Converts a hex value to RGB color.
    :param hex: string with hex value
    :return: list with RGB values
    """
    hex = hex.lstrip('#')
    return list(int(hex[i:i + 2], 16) for i in (0, 2, 4))


def parse_gamma_table(g_handler: GammaHandler) -> int:
    """
    Parse table of Gamma colors from firma-gamma.ru and insert values into database
    :param g_handler: handler for database
    :return: 0 in case of success, -1 in case of failure
    """
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")

    if table:
        rows = table.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            gamma_code = cols[1].text.strip()
            color = cols[4].get("style")
            if "background-color" not in color:
                return -1
            i = color.find("background-color:") + len("background-color:")
            color = color[i:i + 7]

            g_handler.insert(hex_to_rgb(color), gamma_code)
    else:
        return -1

    return 0


if __name__ == "__main__":
    handler = GammaHandler("../db/colors.sql")

    response = requests.get(url)
    if response.status_code == 200:
        parse_result = parse_gamma_table(handler)
        assert parse_result == 0, ValueError("Gamma parsing failed")
    else:
        print(f"Не удалось загрузить страницу. Код ошибки: {response.status_code}")

    handler.teardown()

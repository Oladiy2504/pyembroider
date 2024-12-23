from src.bot.telegram_bot import update_user_flag, check_user_flag
from src.parsing.parsing_data import strings_parsing, canvas_parsing


def test_flag_updates():
    user_flags = {}
    update_user_flag(123, 'changing_conv', True)
    update_user_flag(123, 'adding_string', True)
    assert check_user_flag(123, 'changing_conv') and check_user_flag(123, 'adding_string')

def test_diff_users_flag_updates():
    user_flags = {}
    update_user_flag(123, 'changing_conv', True)
    update_user_flag(321, 'adding_string', True)
    assert check_user_flag(123, 'changing_conv') and check_user_flag(321, 'adding_string')

def check_strings_parsing():
    strings = "GOIDA"
    assert strings_parsing(strings) == []

def check_normal_strings():
    strings = "#FF5733-10, #C70039-20, #900C3F-30"
    assert strings_parsing(strings) == [[16734003, 10], [13041721, 20], [9440319, 30]]

def check_conv_parsing():
    conv = "123 123"
    assert canvas_parsing(conv) == [123, 123]

    conv = "GOIDA"
    assert canvas_parsing(conv) == []

test_flag_updates()
test_diff_users_flag_updates()
check_strings_parsing()
check_normal_strings()
check_conv_parsing()
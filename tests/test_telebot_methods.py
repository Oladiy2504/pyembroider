from src.bot.telegram_bot import update_user_flag, check_user_flag
from src.bot.parsing_data import strings_parsing, conv_parsing


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
    assert not check_user_flag(321, 'changing_conv') and not check_user_flag(123, 'adding_string')

def check_strings_parsing():
    strings = "GOIDA"
    assert strings_parsing(strings) == []

    strings = "#FF5733-10, #C70039-20, #900C3F-30"
    assert strings_parsing(strings) == [[16734099, 10], [13158681, 20], [9430911, 30]]

def check_conv_parsing():
    conv = "123 123"
    assert conv_parsing(conv) == [123, 123]

    conv = "GOIDA"
    assert conv_parsing(conv) == []

import sqlite3

class UserSettingsDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_settings (user_id INTEGER PRIMARY KEY, user_settings INTEGER DEFAULT 0);''')
        connection.commit()
        connection.close()

    def update_user_settings(self, user_id, user_settings):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute('''SELECT user_settings FROM user_settings WHERE user_id = ?''', (user_id,))
        result = cursor.fetchone()
        if result:
            cursor.execute('''UPDATE user_settings SET user_settings = ? WHERE user_id = ?''', (user_settings, user_id))
        else:
            cursor.execute('''INSERT INTO user_settings (user_id, user_settings) VALUES (?, ?)''', (user_id, user_settings))
        connection.commit()
        connection.close()

    def get_user_settings(self, user_id):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute('''SELECT user_settings FROM user_settings WHERE user_id = ?''', (user_id,))
        result = cursor.fetchone()
        connection.close()
        if not result:
            self.update_user_settings(user_id, 0)
            return 0
        return result[0]

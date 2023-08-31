import sqlite3

def create_database():
    conn = sqlite3.connect('meal_log.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            user_id INTEGER,
            meal_type TEXT,
            meal_photo TEXT,
            meal_description TEXT
        )
    ''')

    conn.commit()
    conn.close()

def insert_meal(user_id, meal_type, meal_photo, meal_description):
    conn = sqlite3.connect('meal_log.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO meals (user_id, meal_type, meal_photo, meal_description) VALUES (?, ?, ?, ?)',
                   (user_id, meal_type, meal_photo, meal_description))

    conn.commit()
    conn.close()

def get_meal_logs():
    conn = sqlite3.connect('meal_log.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id, meal_type, meal_description FROM meals')
    meal_logs = cursor.fetchall()

    conn.close()
    return meal_logs

# Other backend functions

if __name__ == '__main__':
    create_database()

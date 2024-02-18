import sqlite3

#create database
def create_database():
    conn = sqlite3.connect('meal_log.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,       
            user_id INTEGER,
            username TEXT,
            meal_type TEXT,
            meal_photo TEXT,
            meal_description TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()

#insert meal by inserting a new line
def insert_meal(user_id, username, meal_type, meal_photo, meal_description, date):
    conn = sqlite3.connect('meal_log.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO meals (user_id, username, meal_type, meal_photo, meal_description, date) VALUES (?, ?, ?, ?, ?, ?)',
                   (user_id, username, meal_type, meal_photo, meal_description, date))

    conn.commit()
    conn.close()

def reset_logs():
    conn = sqlite3.connect('meal_log.db')
    cursor = conn.cursor()

    # Delete all records from the meals table
    cursor.execute('DELETE FROM meals')
    conn.commit()

    conn.close()

#retrieve meal logs
def get_meal_logs():
    conn = sqlite3.connect('meal_log.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id, username, meal_type, meal_description, meal_photo, date FROM meals ORDER BY date DESC')
    meal_logs = cursor.fetchall()

    conn.close()
    return meal_logs

def delete_meal(log_id):
    conn = sqlite3.connect('meal_log.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meals WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()

# Other backend functions
if __name__ == '__main__':
    create_database()

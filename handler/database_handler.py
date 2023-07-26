import mysql.connector


class DatabaseHandler():
    connection = None
    cursor = None
    config = {
        'user': 'asterisk',
        'password': 'Password@1#',
        'host': '192.168.1.32',
        'port': 3306,
        'database': 'asterisk',
    }

    def __init__(self):
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor()
        self.cursor.execute("use asterisk")

    def update_channel_status(self, queued: int, dialed: int, answered: int, completed: int, rejected: int, congestion: int, machine_number: str) -> bool:
        query = "UPDATE channel_status SET queued = %s, dialed = %s, answered = %s, completed = %s, rejected = %s, congestion = %s WHERE machine_number = %s"
        param = (queued, dialed, answered, completed,
                 rejected, congestion, machine_number)
        self.cursor.execute(query, param)
        self.connection.commit()
        return self.cursor.rowcount == 1

    def get_channel_status(self, machine_number: str):
        query = "select * from channel_status where machine_number = %s limit 1"
        param = (machine_number,)
        self.cursor.execute(query, param)
        result = self.cursor.fetchone()
        return result

    def close(self):
        self.connection.close()


def get_db() -> DatabaseHandler:
    db = DatabaseHandler()
    try:
        yield db
    except:
        db.close()

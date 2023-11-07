import sqlite3

# Database manager for SQLite operations
class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        self.conn   = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def fetch_patterns(self, offset = 0, limit = 20):
        self.connect()
        # query = '''
        # SELECT * FROM (
        #     SELECT *, COUNT(index_name) OVER (PARTITION BY country_a, country_b, pattern_length, start_year_a, start_year_b) as strength
        #     FROM patterns
        # ) WHERE strength > 1
        # ORDER BY pattern_length DESC, strength DESC
        # LIMIT ? OFFSET ?
        # '''
        query = '''
        SELECT p.*, sub.strength FROM patterns p
        INNER JOIN (
            SELECT country_a, country_b, pattern_length, start_year_a, start_year_b, COUNT(DISTINCT index_name) as strength
            FROM patterns
            GROUP BY country_a, country_b, pattern_length, start_year_a, start_year_b
            HAVING COUNT(DISTINCT index_name) > 1
        ) sub ON p.country_a = sub.country_a AND 
                p.country_b = sub.country_b AND 
                p.pattern_length = sub.pattern_length AND 
                p.start_year_a = sub.start_year_a AND 
                p.start_year_b = sub.start_year_b
        ORDER BY p.pattern_length DESC, sub.strength DESC
        LIMIT ? OFFSET ?
        '''
        self.cursor.execute(query, (limit, offset))
        rows = self.cursor.fetchall()
        #self.close()
        return rows

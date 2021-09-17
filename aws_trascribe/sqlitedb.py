import sqlite3
'''
    CREATE TABLE reports (
    file_name TEXT PRIMARY KEY,
    job_name TEXT NOT NULL,
    transcript TEXT,
    items TEXT)
'''
class Reports:
    con = sqlite3.connect('reports.db')
    def __init__(self) -> None:
        pass


    def collect(self):
        import pandas as pd 
        with self.con as conn:
            df = pd.read_sql_query("SELECT * from reports", conn)
            return df

    def insert(self, filename: str, jobname: str, transcript: str, items: str):
        def __create_report(conn, report):
            sql = ''' INSERT INTO reports (file_name,job_name,transcript,items) VALUES (?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, report)
            conn.commit()
            return cur.lastrowid

        with self.con as conn:
            report = (filename,jobname,transcript,items)
            return __create_report(conn,report)


    def __repr__(self) -> str:
        with self.con as conn:
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM reports')
            return cur.fetchone()


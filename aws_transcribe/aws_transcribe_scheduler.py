import pandas as pd
import time
import boto3
import sqlite3
from sqlite3 import IntegrityError
from botocore.exceptions import ClientError
import logging
import uuid
from aws_transcribe.data_uploader import S3_Uploader
import json

'''
    CREATE TABLE reports (
    file_name TEXT PRIMARY KEY,
    job_name TEXT NOT NULL,
    volume INT NOT NULL,
    lhs TEXT NOT NULL,
    rhs TEXT NOT NULL,
    base_sentence TEXT NOT NULL,
    transcript TEXT,
    items TEXT);
'''

class Reports:
    con = sqlite3.connect('reports.db')
    def __init__(self, lhs, rhs, base_sentence) -> None:
        self.lhs = lhs
        self.rhs = rhs
        self.base_sentence = base_sentence

    def collect(self):
        import pandas as pd 
        with self.con as conn:
            df = pd.read_sql_query(f"SELECT * from reports WHERE lhs == '{self.lhs}' AND rhs == '{self.rhs}' AND base_sentence == '{self.base_sentence}'", conn)
            return df
    
    def get(self, filename: str):
        def __check_report(conn, report):
            sql = ''' SELECT 1 FROM reports WHERE file_name == ? AND lhs == ? AND rhs == ? AND base_sentence == ? '''
            cur = conn.cursor()
            cur.execute(sql, report)
            conn.commit()
            return cur.fetchone()

        with self.con as conn:
            report = (filename, self.lhs, self.rhs, self.base_sentence)
            return __check_report(conn,report)

    def insert(self, filename: str, jobname: str, volume: str, transcript: str, items: str):
        def __create_report(conn, report):
            sql = ''' INSERT INTO reports (file_name,job_name,volume,lhs,rhs,base_sentence,transcript,items) VALUES (?,?,?,?,?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, report)
            conn.commit()
            return cur.lastrowid

        with self.con as conn:
            report = (filename,jobname,volume,self.lhs,self.rhs,self.base_sentence,transcript,items)
            return __create_report(conn,report)
        
    def update(self, jobname: str, transcript: str, items: str):
        def __create_report(conn, report):
            sql = ''' UPDATE reports SET transcript = ?, items = ?  WHERE job_name = ?'''
            cur = conn.cursor()
            cur.execute(sql, report)
            conn.commit()
            return cur.lastrowid

        with self.con as conn:
            report = (transcript,items,jobname)
            return __create_report(conn,report)
        
    def get_job_names(self):
        def __get_report(conn, report):
            sql = ''' SELECT job_name FROM reports WHERE lhs == ? AND rhs == ? AND base_sentence == ? '''
            cur = conn.cursor()
            cur.execute(sql, report)
            conn.commit()
            return cur.fetchall()

        with self.con as conn:
            report = (self.lhs,self.rhs,self.base_sentence)
            return [i[0] for i in __get_report(conn,report)]


    def __repr__(self) -> str:
        with self.con as conn:
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM reports')
            return "Database Connected" if cur.fetchone() else "Database Connect ERROR"
        
    def update_reports(self):
        transcribe = boto3.client('transcribe')
        count = 0
        for job_name in self.get_job_names():
            result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if result['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
                data = pd.read_json(result['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                transcript = data['results'][1][0]['transcript']
                detail = data['results'][0]
                try:
                    db_res = self.update(job_name, str(transcript), str(detail))
                    print(f'{db_res}')
                    count += 1
                except IntegrityError as e:
                    print('Report already recorded')
        print(count/len(list_of_jobnames) + 'updated')


def amazon_transcribe(audio_file_name, lhs, rhs, base_sentence):
    """ Transcribe ONE audio from from S3
    Args:
        audio_file_name (string): audio file name on S3

    Returns:
        string: A sentance of the transcribe
    """
    transcribe = boto3.client('transcribe')
    import re
    rec = re.compile(r"(?:-|\+).*")
    if not audio_file_name.endswith('.mp3'):
        return

    print(f"Transcribing {audio_file_name}")
    job_uri = "s3://favorite-place-audios/" +  base_sentence + '/' + audio_file_name  
    file_name = audio_file_name.split('.')[0]
    file_format = audio_file_name.split('.')[1]
    print(file_name)
    volume = rec.findall(file_name)[0]
    job_name = str(uuid.uuid4())
    
    # check if name is taken or not
    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat = file_format,
            LanguageCode='en-US')
        print(f'{job_name} does not exist scheduling a new job')
    except ClientError as e:
        logging.error(f'{job_name}, Error: {e}')

    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(15)
    if result['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
        data = pd.read_json(result['TranscriptionJob']['Transcript']['TranscriptFileUri'])
        transcript = data['results'][1][0]['transcript']
        detail = data['results'][0]
        reports = Reports(lhs, rhs, base_sentence)
        try:
            db_res = reports.insert(audio_file_name, job_name, str(volume), str(transcript), str(detail))
            print(f'row ID in DB is: {db_res}')
        except IntegrityError as e:
            print('Report already recorded')
    return transcript


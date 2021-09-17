import pandas as pd
import time
import boto3
from sqlitedb import Reports
from sqlite3 import IntegrityError
from botocore.exceptions import ClientError

class Transcribe_scheduler:
    transcribe = boto3.client('transcribe')

    def amazon_transcribe(self, audio_file_name):
        """ Transcribe ONE audio from from S3

        Args:
            audio_file_name (string): audio file name on S3

        Returns:
            string: A sentance of the transcribe
        """
        if audio_file_name.endswith('.pcm'):
            print('skipping pcm file')
            return

        job_uri = "s3://favorite-place-audios/" + audio_file_name  
        job_name = (audio_file_name.split('.')[0]).replace("+","").replace(" ", "")  
        file_format = audio_file_name.split('.')[1]
        
        # check if name is taken or not
        try:
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': job_uri},
                MediaFormat = file_format,
                LanguageCode='en-US')
            print(f'{job_name} does not exist scheduling a new job')
        except ClientError as e:
            print(f'{job_name}, Error: {e}')
        
        while True:
            result = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            time.sleep(15)
        if result['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
            data = pd.read_json(result['TranscriptionJob']['Transcript']['TranscriptFileUri'])
            transcript = data['results'][1][0]['transcript']
            detail = data['results'][0]
            reports = Reports()
            try:
                db_res = reports.insert(audio_file_name,job_name,str(transcript),str(detail))
                print(f'row ID in DB is: {db_res}')
            except IntegrityError as e:
                print('Report already recorded')
        return transcript


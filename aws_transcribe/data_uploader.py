import logging
import boto3
from botocore.exceptions import ClientError
import os


class S3_Uploader:
    s3 = boto3.client('s3')
    bucket = 'favorite-place-audios'
    
    def __init__(self, folder_name=None) -> None:
        self.folder_name = folder_name
        self.files = {'mp3': [i for i in os.listdir(self.folder_name) if i.endswith('.mp3')],
                      'pcm': [i for i in os.listdir(self.folder_name) if i.endswith('.pcm')]}
        self.convert_to_mp3()
        
                
    def upload_file(self,folder_name, file_name):
        file_path = os.path.join(self.folder_name, file_name)
        object_name = os.path.join(folder_name,file_name)        
        
        try:
            response = self.s3.upload_file(file_path, self.bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True
    
    def set_foldername(self, foldername):
        self.folder_name = foldername
        self.files = {'mp3': [i for i in os.listdir(self.folder_name) if i.endswith('.mp3')],
                      'pcm': [i for i in os.listdir(self.folder_name) if i.endswith('.pcm')]}
        return self

    def convert_to_mp3(self):
        if not self.folder_name:
            logging.error('Have not defined a folder yet, try set_foldername()')
            return 
        import subprocess
        for i in self.files['pcm']:
            file_basename = i.split('.')[0]
            if file_basename + '.mp3' not in self.files['mp3']:
                bashCommand = f'ffmpeg -f s16le -ar 16K -i {file_basename + ".pcm"} {file_basename + ".mp3"}'
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd=self.folder_name)
                output, error = process.communicate()
                if error: logging.error(error)
        return self
    
    def has_file_on_s3(self, folder_name, file_name):
        try:
            self.s3.get_object(Bucket=self.bucket, Key=os.path.join(folder_name, file_name))
            return True
        except ClientError as e:
            return False
            
    def upload(self):
        if not self.folder_name:
            logging.error('Have not defined a folder yet, try set_foldername()')
            return
        s3_audios = self.list_all_audios()
        for i in self.files['mp3']:
            if i not in s3_audios:
                response = self.upload_file(i)
                if not response: 
                    print('upload error')    
                    break
        print(f'Finish upload!')

    def list_all_audios(self, summerize=True):
        import re
        res =  self.s3.list_objects(Bucket = self.bucket)
        l = [i['Key'] for i in res['Contents']]
        if summerize:
            return list(set([re.split(r'\+|\-',f)[0] for f in l ]))
        else:
            return l
    
    def __repr__(self) -> str:
        return  f'files under {self.folder_name}: \n \
                   mp3: {len(self.files["mp3"])}  \n \
                   pcm: {len(self.files["pcm"])}'



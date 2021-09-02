import logging
import boto3
from botocore.exceptions import ClientError
import os


class S3_Uploader:
    def __init__(self, folder_name) -> None:
        self.s3 = boto3.client('s3')
        self.bucket = 'favorite-place-audios'
        self.folder_name = folder_name
        self.files = {'mp3': [i for i in os.listdir(self.folder_name) if i.endswith('.mp3')],
                      'pcm': [i for i in os.listdir(self.folder_name) if i.endswith('.pcm')]}

    def __upload_file(self, file_name):
            object_name = os.path.basename(file_name)

            s3_client = self.s3
            try:
                response = s3_client.upload_file(file_name, self.bucket, object_name)
            except ClientError as e:
                logging.error(e)
                return False
            return True

    def convert_to_mp3(self):
        import subprocess
        for i in self.files['pcm']:
            file_basename = i.split('.')[0]
            if file_basename + '.mp3' not in self.files['mp3']:
                bashCommand = f'ffmpeg -f s16le -ar 16K -i {file_basename + ".pcm"} {file_basename + ".mp3"}'
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd=self.folder_name)
                output, error = process.communicate()
                logging.error(error)
                print(output)
        print(self.__repr__())
            

    def upload(self):
        # check if there is already
        for i in self.files.mp3:
            if not self.__upload_file(os.path.join(self.folder_name, i)): break
        print(f'Finish upload!')
    
    def __repr__(self) -> str:
        return  f'files under {self.folder_name}: \n \
                   mp3: {len(self.files["mp3"])}  \n \
                   pcm: {len(self.files["pcm"])}'



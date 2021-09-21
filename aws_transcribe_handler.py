from configs import BOOTSTRAP_AUDIO_PATH, AUDIO_PATH
from audio_generation.audio_mixer import generate_mixed_audio
import os
from aws_transcribe.aws_transcribe_scheduler import amazon_transcribe, Reports
from aws_transcribe.data_uploader import S3_Uploader

class aws_transcribe_handler():
    def __init__(self, lhs, rhs, base_sentense):
        '''
        Args:
            lhs <str>, "male_garage"
            rhs <str>, "male_kitchen"
            base_sentense <str>, "my favorite place in the house is <x>"           
        '''
        self.lhs = lhs
        self.rhs = rhs
        self.base_sentense = base_sentense
        self.folder_path = generate_mixed_audio(lhs, rhs, base_sentense)
        self.s3 = S3_Uploader(self.folder_path)
 
    def reports(self):
        r = Reports(self.lhs, self.rhs, self.base_sentense)
        for file_name in [i for i in os.listdir(self.folder_path) if i.endswith('.mp3')]:
            if r.get(file_name):
                continue
            if not self.s3.has_file_on_s3(self.base_sentense,file_name):
                self.s3.upload_file(self.base_sentense,file_name)
            amazon_transcribe(file_name, self.lhs, self.rhs, self.base_sentense)
        return r.collect().sort_values('volume')
    
    def update_reports(self):
        r = Reports(self.lhs, self.rhs, self.base_sentense)
        r.update_reports()
        return r.collect()
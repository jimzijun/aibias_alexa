import os
from pydub import AudioSegment, effects
from pydub.playback import play
from configs import BOOTSTRAP_AUDIO_PATH, AUDIO_PATH
from shutil import rmtree

def load_audio(name):
   raw = AudioSegment.from_file(file=os.path.join(BOOTSTRAP_AUDIO_PATH, name+'.pcm'), format="pcm", frame_rate = 16000, channels = 1, sample_width = 2)
   n_raw = effects.normalize(raw)
   return n_raw

def mix_audio(au1,au2):
    if len(au1) > len(au2): 
        output = au1.overlay(au2)
    else:
        output = au2.overlay(au1)
    return output

def generate_mixed_audio(lhs,rhs):
    if os.getcwd() != '/home/zyi103/aibias_alexa':
        print('WRONG DIRECTORY')
        return None
    if not os.path.exists(os.path.join(AUDIO_PATH,f'{lhs}_{rhs}')):
        os.mkdir(os.path.join(AUDIO_PATH,f'{lhs}_{rhs}'))
    root_path = os.path.join(AUDIO_PATH,f'{lhs}_{rhs}')

    lhs_audio,rhs_audio = load_audio(lhs),load_audio(rhs)

    for i in range(-24,25,3):
        if i < 0:
            mixed_audio = mix_audio(lhs_audio,rhs_audio+i)
            mixed_audio.export(os.path.join(root_path,f"{lhs}_{rhs}{i:03d}.pcm"),format="s16le")
        else:
            mixed_audio = mix_audio(lhs_audio-i,rhs_audio)
            mixed_audio.export(os.path.join(root_path,f"{lhs}_{rhs}{i:+03d}.pcm"),format="s16le")    

def delete_mixed_audio(lhs,rhs):
    folder_path = os.path.join(AUDIO_PATH,f'{lhs}_{rhs}')
    if os.path.isdir(folder_path):
        rmtree(folder_path)
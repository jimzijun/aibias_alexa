import os
from pydub import AudioSegment, effects
from pydub.playback import play
from configs import BOOTSTRAP_AUDIO_PATH, AUDIO_PATH
from shutil import rmtree
from audio_generation.polly_audio_generator import generate_audio

def load_audio(name,base_sentence):
    bootstrap_audio_file_path = os.path.join(BOOTSTRAP_AUDIO_PATH, base_sentence, name+'.pcm')
    if not os.path.exists(bootstrap_audio_file_path):
        gender = name.split('_')[0]
        phase = name.split('_')[1]
        generate_audio(base_sentence, phase, gender, name+'.pcm')
    raw = AudioSegment.from_file(file=os.path.join(bootstrap_audio_file_path), format="pcm", frame_rate = 16000, channels = 1, sample_width = 2)
    n_raw = effects.normalize(raw)
    return n_raw

def mix_audio(au1,au2):
    if len(au1) > len(au2): 
        output = au1.overlay(au2)
    else:
        output = au2.overlay(au1)
    return output

def generate_mixed_audio(lhs,rhs,base_sentence):
    if os.getcwd() != '/home/zyi103/aibias_alexa':
        print('WRONG DIRECTORY')
        return None
    audio_folder_path = os.path.join(AUDIO_PATH,base_sentence,f'{lhs}_{rhs}')
    bootstrap_audio_folder_path = os.path.join(BOOTSTRAP_AUDIO_PATH,base_sentence)
    if not os.path.exists(audio_folder_path) or not os.path.exists(bootstrap_audio_folder_path): 
        os.makedirs(audio_folder_path, exist_ok=True) 
        os.makedirs(bootstrap_audio_folder_path, exist_ok=True) 
    
    lhs_audio,rhs_audio = load_audio(lhs,base_sentence),load_audio(rhs,base_sentence)

    for i in range(-24,25,3):
        if i < 0:
            mixed_audio = mix_audio(lhs_audio,rhs_audio+i)
            mixed_audio.export(os.path.join(audio_folder_path,f"{lhs}_{rhs}{i:03d}.pcm"),format="s16le")
        else:
            mixed_audio = mix_audio(lhs_audio-i,rhs_audio)
            mixed_audio.export(os.path.join(audio_folder_path,f"{lhs}_{rhs}{i:+03d}.pcm"),format="s16le")    
    return audio_folder_path

def delete_mixed_audio(lhs,rhs,base_sentence):
    folder_path = os.path.join(BOOTSTRAP_AUDIO_PATH,base_sentence,f'{lhs}_{rhs}')
    if os.path.isdir(folder_path):
        rmtree(folder_path)
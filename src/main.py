from itertools import combinations, product
from configs import OCCUPATION_LIST, REPORTS_PATH, AUDIO_PATH, FEMALE_VOICE_ID, MALE_VOICE_ID, BOOTSTRAP_AUDIO_PATH
from preprocessing import generate_mixed_audio, delete_mixed_audio
import os
from lex_request import test_phrase
from polly_audio_generator import generate_audio
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename='logs/occupation_request.log', filemode='w')

for occupation in OCCUPATION_LIST:
    male_file_name = 'male_'+occupation+'.pcm'
    female_file_name = 'female_'+occupation+'.pcm'
    if (male_file_name not in os.listdir(BOOTSTRAP_AUDIO_PATH)):
        generate_audio(f"my occupation is {occupation}", MALE_VOICE_ID, male_file_name)
        logging.info(f"generated {male_file_name}")
    else:
        logging.info(f"{male_file_name} exists, did not request")
    if (female_file_name not in os.listdir(BOOTSTRAP_AUDIO_PATH)):
        generate_audio(f"my occupation is {occupation}", FEMALE_VOICE_ID, female_file_name)
        logging.info(f"generated {female_file_name}")
    else:
        logging.info(f"{female_file_name} exists, did not request")
logging.info("Polly generation done")

count = 0
occupation_combinations = list(combinations(OCCUPATION_LIST, 2))

for occupation1,occupation2 in occupation_combinations:
    occupation1_list = [f"male_{occupation1}", f"female_{occupation1}"]
    occupation2_list = [f"male_{occupation2}", f"female_{occupation2}"]
    for occupation_with_gender1, occupation_with_gender2 in list(product(occupation1_list,occupation2_list)):
        logging.info(f"Generating report for {occupation_with_gender1}_{occupation_with_gender2}")
        if f"{occupation_with_gender1}_{occupation_with_gender2}" not in os.listdir(REPORTS_PATH):
            logging.info(f"Mixing {occupation_with_gender1} || {occupation_with_gender2} audios ")
            generate_mixed_audio(occupation_with_gender1,occupation_with_gender2)
            logging.info(f"Creating reports {occupation_with_gender1} || {occupation_with_gender2} ")
            test_phrase(occupation_with_gender1, occupation_with_gender2)
            logging.info(f"REPORT CREATED || {occupation_with_gender1}_{occupation_with_gender2}")
            logging.info(f"Deleting {occupation_with_gender1} || {occupation_with_gender2} audios ")
            delete_mixed_audio(occupation_with_gender1,occupation_with_gender2)
        else:
            logging.info(f"Report {occupation_with_gender1} || {occupation_with_gender2} exists, did not request ")

    logging.info(f'===== {count}/{len(occupation_combinations)} finished =====')
    count += 1

logging.info(f'task finished')

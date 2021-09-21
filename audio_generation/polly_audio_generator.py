from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
from configs import BOOTSTRAP_AUDIO_PATH, AUDIO_PATH
import os
import sys

# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session()
polly = session.client("polly")

VOICE_ID = {
    "male": "Joey",
    "female": "Salli"
}


def generate_audio(base_sentence, phase, gender, filename):
    sentence = base_sentence.replace('<x>', phase)
    try:
        # Request speech synthesis
        response = polly.synthesize_speech(Text=sentence, OutputFormat="pcm",
                                            VoiceId=VOICE_ID[gender])
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            output = os.path.join(BOOTSTRAP_AUDIO_PATH, base_sentence, filename)

            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)



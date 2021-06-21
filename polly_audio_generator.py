from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess

# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="aibias_alexa")
polly = session.client("polly")

garage_text = "My favorite place is the garage"
kitchen_text = "My favorite place is the kitchen"
male_voice_id = "Joey"
female_voice_id = "Salli"

text = garage_text
voice_id = female_voice_id
filename = "female_garage.pcm"

try:
    # Request speech synthesis
    response = polly.synthesize_speech(Text=text, OutputFormat="pcm",
                                        VoiceId=voice_id, SampleRate = '16000')
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
        output = os.path.join(os.getcwd(),"audios/bootstrap", filename)

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

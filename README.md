# aibias_alexa

* play pcm commend:
`ffplay -f s16le -sample_rate 16000 {file_name}`

* conversion
`ffmpeg -i {input_file} -f s16le -ar 16K {output_file}`
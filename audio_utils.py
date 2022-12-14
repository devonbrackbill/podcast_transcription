from pydub import AudioSegment
import soundfile as sf
import json

def convert_m4a_to_wav(m4a_file, wav_file) -> None:
    '''Converts m4a to wav'''
    # Load m4a file
    sound = AudioSegment.from_file(m4a_file, format="m4a")
    # Export to wav
    sound.export(wav_file, format="wav")

def convert_mp3_to_wav(mp3_file, wav_file) -> None:
    '''Converts mp3 to wav'''
    # Load mp3 file
    sound = AudioSegment.from_file(mp3_file, format="mp3")
    # Export to wav
    sound.export(wav_file, format="wav")

def calculate_audio_length(audio_path) -> None:
    '''Calculates audio length in seconds'''
    f = sf.SoundFile(audio_path)
    print('samples = {}'.format(f.frames))
    print('sample rate = {}'.format(f.samplerate))
    print('seconds = {}'.format(f.frames / f.samplerate))
    print('minutes = {}'.format(f.frames / f.samplerate / 60.0))

def save_whisper_output(outfile, output) -> None:
    # save output dictionary to file as json
    with open(outfile, 'w') as f:
        json.dump(output, f)

def read_whisper_json(whisper_output) -> dict:
    '''Reads whisper output file and returns dictionary'''
    with open(whisper_output, 'r') as f:
        output = json.load(f)
    return(output)
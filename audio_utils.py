from pydub import AudioSegment
import soundfile as sf
import json
import feedparser
import subprocess
import replicate
import os

def convert_m4a_to_wav(m4a_file: str, wav_file: str) -> None:
    '''Converts m4a to wav'''
    # Load m4a file
    sound = AudioSegment.from_file(m4a_file, format="m4a")
    # Export to wav
    sound.export(wav_file, format="wav")

def convert_m4a_to_mp3(m4a_file: str, mp3_file: str) -> None:
    '''Converts m4a to mp3'''
    # Load m4a file
    sound = AudioSegment.from_file(m4a_file, format="m4a")
    # Export to mp3
    sound.export(mp3_file, format="mp3")

def convert_mp3_to_wav(mp3_file: str, wav_file: str) -> None:
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

def save_whisper_output(outfile: str, output: dict) -> None:
    # save output dictionary to file as json
    with open(outfile, 'w') as f:
        json.dump(output, f)

def read_whisper_json(whisper_output: str) -> dict:
    '''Reads whisper output file and returns dictionary'''
    with open(whisper_output, 'r') as f:
        output = json.load(f)
    return(output)

def podcast_to_transcript(
    rss_feed: str,
    podcast_title: str,
    outfile: str,
    model_version: str="23241e5731b44fcb5de68da8ebddae1ad97c5094d24f94ccb11f7c1d33d661e2",
    model_str: str="base") -> str:
    '''Converts a podcast from an rss feed to a transcript.
    Inputs:
        rss_feed: rss feed url
        podcast_title: title of podcast to convert
        outfile: name of output file
        model_version: version of whisper model to use
        model_str: model to use (base or large)
    Returns:
        name of output file; can be read with read_whisper_json()
    '''
    # get rss feed
    feed = feedparser.parse(rss_feed)
    # get the podcast url for this podcast_title
    for entry in feed['entries']:
        if podcast_title in entry['title']:
            podcast_url = entry['enclosures'][0]['href']
            break
    
    if podcast_url == None:
        print('Podcast not found')
        return(False)
    else:
        print('Podcast found: {}'.format(podcast_url))
    
    # make /res directory if it doesn't exist
    os.makedirs('res/', exist_ok=True)
    
    print('Downloading podcast...')
    if 'mp3' in podcast_url:
        # download podcast (and suppress output)
        subprocess.call(['wget', podcast_url, '--directory-prefix', 'res/',
                         '--output-document', '{}.mp3'.format(outfile),
                         '>/dev/null', '2>&1'])
        # open mp3 file
        audio_obj = open('{}.mp3'.format(outfile), 'rb')
    elif 'm4a' in podcast_url:
        # download podcast (and suppress output)
        subprocess.call(['wget', podcast_url, '--directory-prefix', 'res/',
                         '--output-document', '{}.m4a'.format(outfile),
                         '>/dev/null', '2>&1'])
        # convert m4a to mp3
        convert_m4a_to_mp3('{}.m4a'.format(outfile), '{}.mp3'.format(outfile))
        # open mp3 file
        audio_obj = open('{}.mp3'.format(outfile), 'rb')
    else:
        print('Podcast format not supported')
        return(False)

    # check if we already made a transcript for this podcast
    try:
        with open('{}.json'.format(outfile), 'r') as f:
            print('Transcript already exists')
            return('{}.json'.format(outfile))
    except:
        pass

    # run whisper model
    model = replicate.models.get('openai/whisper')
    version = model.versions.get(model_version)
    print('Converting podcast to transcript...')
    output = version.predict(audio=audio_obj, model=model_str)

    # save output
    save_whisper_output('{}.json'.format(outfile), output)
    print('Transcript saved to {}.json'.format(outfile))

    return('{}.json'.format(outfile))
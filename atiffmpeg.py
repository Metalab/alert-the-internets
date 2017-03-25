# ffmpeg wrapper library. May raise exceptions™
import subprocess, json

def talk_to_process(cmd):
    """Wrapper around subprocess.call for synchronous, input-less command execution"""
    sub = subprocess.Popen(cmd,
                           stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL)
    out, err = sub.communicate()
    return out

def probe(filename, ffprobe_path="ffprobe"):
    """Call an ffprobe binary and load the resulting json"""
    return json.loads(talk_to_process(
        [ffprobe_path, filename, "-print_format", "json", "-show_streams"]
    ))

def ffprobe(filename, ffprobe_path="ffprobe"):
    """returns audio and video streams separately"""
    p = probe(filename, ffprobe_path)['streams']
    return [ v for v in p if v['codec_type'] == 'audio' ],\
           [ v for v in p if v['codec_type'] == 'video' ]

# ffmpeg wrapper library. May raise exceptions™
import subprocess, json

FFPROBE_PATH = "ffprobe"
YOUTUBE_UPLOAD_PATH = "youtube-upload"

class Miscommunication(Exception):
    pass

def talk_to_process(cmd):
    """Wrapper around subprocess.call for synchronous, input-less command execution"""
    sub = subprocess.Popen(cmd,
                           stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL)
    out, err = sub.communicate()
    if sub.returncode == 0:
        return out
    else:
        raise Miscommunication("You know, everybody always just talks past each other. :(")

def probe(filename):
    """Call an ffprobe binary and load the resulting json"""
    # Raises an exception in case of invalid JSON or miscommunication.
    return json.loads(talk_to_process(
        [FFPROBE_PATH, filename, "-print_format", "json", "-show_streams"]
    ))

def ffprobe(filename):
    """returns audio and video streams separately"""
    p = probe(filename, ffprobe_path)['streams']
    return [ v for v in p if v['codec_type'] == 'audio' ],\
           [ v for v in p if v['codec_type'] == 'video' ]

def ffmerge(file1, file2):
    """merges two files via ffmpeg into one"""
    pass

def youtube_upload(videopath, title, public=False):
    privacy = 'public' if public else 'unlisted'
    return talk_to_process([YOUTUBE_UPLOAD_PATH, "--title", title, '--privacy', privacy, videopath])

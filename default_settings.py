MAX_CONTENT_LENGTH = 256 * 1024 * 1024 # default: 256M max upload to avoid filling the disk
VIDEO_CONTENT_TYPES = ["video/mp4","video/webm","video/x-matroska"]

# these paths are relative to the instance directory
SQLITE_DATABASE = "ati.db"
TITLE_VIDEO = "title.mp4"

# relative to project root directory
VIDEO_UPLOAD_DIR = "media/original"
TEMP_DIR = "media/tmp"

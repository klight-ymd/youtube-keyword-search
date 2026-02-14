
from youtube_transcript_api import YouTubeTranscriptApi
import inspect

print("Attributes of YouTubeTranscriptApi:")
print(dir(YouTubeTranscriptApi))

try:
    print("\nSource file:", inspect.getfile(YouTubeTranscriptApi))
except:
    pass

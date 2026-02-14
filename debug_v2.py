
from youtube_transcript_api import YouTubeTranscriptApi

video_id = 'j9YpkSX7NNM'
video_id2 = 'kqtD5dpn9C8'
urls = [video_id, video_id2]
keywords = ['Python', 'faster']

print(f"Testing V2 Logic...")

for vid in urls:
    print(f"\n--- Testing video: {vid} ---")
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(vid)
        try:
            transcript = transcript_list.find_transcript(['ja', 'en', 'en-US'])
        except Exception as e:
            print(f"First try failed: {e}")
            print("Fallback to ['ja', 'en']")
            transcript = transcript_list.find_transcript(['ja', 'en'])

        print(f"Transcript found: {transcript.language} ({transcript.language_code})")
        data = transcript.fetch()
        print(f"First entry: {data[0]}")
        
        found_count = 0
        for entry in data:
            text = entry['text']
            matched = [k for k in keywords if k.lower() in text.lower()]
            if matched:
                if found_count < 3:
                     print(f"  Match at {entry['start']}: {matched} in '{text}'")
                found_count += 1
                
        print(f"Total matches found: {found_count}")
            
    except Exception as e:
        print(f"Error processing {vid}: {e}")
        import traceback
        traceback.print_exc()

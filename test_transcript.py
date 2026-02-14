
from youtube_transcript_api import YouTubeTranscriptApi

# テスト用動画ID
video_id = 'j9YpkSX7NNM'

try:
    print(f"Fetching transcript for video ID: {video_id}...")
    
    # APIインスタンスを作成
    api = YouTubeTranscriptApi()
    
    # 字幕リストを取得
    # list() メソッドを使用
    transcript_list = api.list(video_id)
    
    print("Transcript list fetched.")
    
    # 日本語か英語の字幕を探す
    transcript = transcript_list.find_transcript(['ja', 'en'])
    
    print(f"Transcript found: {transcript.language} ({transcript.language_code})")
    
    # 字幕データを取得
    data = transcript.fetch()
    
    print("First 5 lines:")
    for entry in data[:5]:
        print(entry)
        
except Exception as e:
    import traceback
    traceback.print_exc()

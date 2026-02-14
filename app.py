
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import datetime
import pandas as pd
import time

# --- 関数定義 ---
def extract_video_id(url):
    """
    YouTubeのURLから動画IDを抽出する関数
    """
    if not url:
        return None
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                p = parse_qs(parsed_url.query)
                return p['v'][0] if 'v' in p else None
            elif parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
            elif parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/')[2]
        return None
    except:
        return None

def format_timestamp(seconds):
    """秒数を HH:MM:SS 形式に変換する"""
    return str(datetime.timedelta(seconds=int(seconds)))

def search_transcript(transcript_data, keywords):
    """
    字幕データからキーワードを検索し、結果リストを返す
    """
    results = []
    for entry in transcript_data:
        text = entry['text']
        start_time = entry['start']
        
        # 複数キーワードのいずれかが含まれるか？ (OR検索)
        hit_keywords = []
        for k in keywords:
            if k.lower() in text.lower():
                hit_keywords.append(k)
        
        if hit_keywords:
            results.append({
                "seconds": start_time,
                "text": text,
                "keywords": hit_keywords
            })
    return results

# --- ページ設定 ---
st.set_page_config(
    page_title="YouTube Keyword Search V2",
    page_icon="🔍",
    layout="wide"
)

# --- UI実装 ---
st.title("📺 YouTube字幕検索アプリ V2")
st.write("複数の動画から、複数のキーワードをまとめて検索できます。")

# サイドバー
with st.sidebar:
    st.header("使い方")
    st.markdown("""
    1. **動画URL**: 1行に1つずつ入力してください。
    2. **キーワード**: カンマ(,)またはスペースで区切って入力してください。
    3. **検索**: ボタンを押すと結果が表示されます。
    4. **保存**: 結果をCSVでダウンロードできます。
    """)
    st.info("※ 字幕がない動画や、無効なURLはスキップされます。")

# メイン入力エリア（2カラム）
col1, col2 = st.columns(2)

with col1:
    url_input_raw = st.text_area(
        "YouTube動画のURL（複数可・改行区切り）",
        value="https://www.youtube.com/watch?v=j9YpkSX7NNM",
        placeholder="https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=...",
        height=200
    )

with col2:
    keyword_input_raw = st.text_input(
        "検索キーワード（複数可・カンマ/スペース区切り）",
        value="Python, AI",
        placeholder="例: AI, Python, 機械学習"
    )

# 検索ボタン
if st.button("検索開始 🚀", type="primary", use_container_width=True):
    # 1. 入力データの整形
    urls = [line.strip() for line in url_input_raw.split('\n') if line.strip()]
    
    # キーワード分割（カンマをスペースに置換 -> split）
    keywords_raw = keyword_input_raw.replace('、', ' ').replace(',', ' ')
    keywords = [k.strip() for k in keywords_raw.split() if k.strip()]

    # 2. バリデーション
    if not urls:
        st.error("⚠️ YouTubeのURLを入力してください。")
    elif not keywords:
        st.error("⚠️ 検索キーワードを入力してください。")
    else:
        # 3. 検索処理実行
        results_data = [] # 最終的な表示用データ
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        api = YouTubeTranscriptApi()
        total_urls = len(urls)
        
        for i, url in enumerate(urls):
            current_progress = (i) / total_urls
            progress_bar.progress(current_progress)
            
            video_id = extract_video_id(url)
            
            if not video_id:
                st.toast(f"スキップ (無効なURL): {url}", icon="⏭️")
                continue
            
            status_text.text(f"検索中 ({i+1}/{total_urls}): {video_id}")
            
            try:
                # 字幕取得
                transcript_list = api.list(video_id)
                try:
                     transcript = transcript_list.find_transcript(['ja', 'en', 'en-US'])
                except:
                     transcript = transcript_list.find_transcript(['ja', 'en']) 

                transcript_data = transcript.fetch()
                
                # ★ここで検索ロジック関数を呼び出し★
                found_entries = search_transcript(transcript_data, keywords)
                
                # 結果を整形して追加
                for res in found_entries:
                    start_time = res['seconds']
                    text = res['text']
                    hit_keywords = res['keywords']
                    
                    formatted_time = format_timestamp(start_time)
                    link_url = f"https://youtu.be/{video_id}?t={int(start_time)}"
                    
                    results_data.append({
                        "Video ID": video_id,
                        "Original URL": url,
                        "Keyword": ", ".join(hit_keywords),
                        "Time": formatted_time,
                        "Text": text,
                        "Link": link_url,
                        "Seconds": start_time
                    })
                        
            except Exception as e:
                st.error(f"⚠️ エラー ({video_id}): 字幕を取得できませんでした。\n理由: {e}")
        
        # 完了処理
        progress_bar.progress(1.0)
        status_text.text("完了！")
        time.sleep(0.5)
        status_text.empty()
        progress_bar.empty()
        
        # 4. 結果表示
        if results_data:
            df = pd.DataFrame(results_data)
            
            st.success(f"🎉 検索完了: 合計 {len(df)} 件 ヒットしました！")
            
            tab1, tab2 = st.tabs(["📋 リスト表示", "📊 データテーブル"])
            
            with tab1:
                for index, row in df.iterrows():
                    with st.container():
                        st.markdown(f"### {row['Time']} (Keyword: {row['Keyword']})")
                        st.markdown(f"[{row['Text']}]({row['Link']})")
                        st.divider()

            with tab2:
                st.dataframe(
                    df[['Keyword', 'Time', 'Text', 'Link', 'Original URL']],
                    column_config={
                        "Link": st.column_config.LinkColumn("再生リンク", display_text="再生 ▶️"),
                        "Original URL": st.column_config.LinkColumn("動画URL")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📥 CSVをダウンロード",
                data=csv_data,
                file_name=f"youtube_search_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                type="primary"
            )
            
        else:
            st.warning("指定したキーワードは見つかりませんでした。")

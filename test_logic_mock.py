
import sys
import os

# app.pyから関数をインポートするためにパスを通す
sys.path.append(os.getcwd())

from app import search_transcript

def test_search_logic():
    print("--- Testing search_transcript logic ---")
    
    # モックデータ
    mock_transcript = [
        {'text': "Hello everyone, welcome to the channel.", 'start': 0.0, 'duration': 5.0},
        {'text': "Today we are going to talk about Python programming.", 'start': 5.0, 'duration': 5.0},
        {'text': "It is a great language for data science.", 'start': 10.0, 'duration': 5.0},
        {'text': "And it is getting faster with every release.", 'start': 15.0, 'duration': 5.0},
        {'text': "So let's dive in.", 'start': 20.0, 'duration': 5.0},
    ]
    
    # ケース1: 単一キーワードヒット
    keywords1 = ["Python"]
    results1 = search_transcript(mock_transcript, keywords1)
    print(f"Keywords: {keywords1}")
    print(f"Results: {len(results1)} entries found.")
    for res in results1:
        print(f" - Found at {res['seconds']}s: '{res['text']}' (Matches: {res['keywords']})")
    
    assert len(results1) == 1
    assert results1[0]['text'] == "Today we are going to talk about Python programming."
    print("✅ Case 1 Passed")
    
    # ケース2: 複数キーワードヒット (OR検索)
    keywords2 = ["python", "faster"]
    results2 = search_transcript(mock_transcript, keywords2)
    print(f"\nKeywords: {keywords2}")
    print(f"Results: {len(results2)} entries found.")
    for res in results2:
        print(f" - Found at {res['seconds']}s: '{res['text']}' (Matches: {res['keywords']})")
        
    assert len(results2) == 2
    assert "Python" in results2[0]['keywords'][0] or "python" in results2[0]['keywords'][0] # Case insensitive check logic depends on implementation
    assert "faster" in results2[1]['keywords']
    print("✅ Case 2 Passed")
    
    # ケース3: ヒットなし
    keywords3 = ["Ruby"]
    results3 = search_transcript(mock_transcript, keywords3)
    print(f"\nKeywords: {keywords3}")
    print(f"Results: {len(results3)} entries found.")
    
    assert len(results3) == 0
    print("✅ Case 3 Passed")

    print("\n🎉 All mock tests passed!")

if __name__ == "__main__":
    test_search_logic()

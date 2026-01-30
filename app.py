import streamlit as st
import google.generativeai as genai
import os

# 画面設定
st.set_page_config(page_title="介護報告支援")
st.title("🛡️ 介護報告書支援ツール")

# Secretsからキーを取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Secretsに 'GEMINI_API_KEY' が設定されていません。")
else:
    # APIの設定
    genai.configure(api_key=api_key)
    
    # 【ここが重要】利用可能なモデルを自動チェックして一番良いものを選ぶ
    try:
        # 最も広くサポートされている安定版の指定
model = genai.GenerativeModel('gemini-pro')
        
        # 入力フォーム
        status = st.selectbox("身体状況", ["全介助", "一部介助", "自立"])
        side = st.selectbox("部位", ["健側", "患側", "該当なし"])
        raw_text = st.text_area("状況メモ")

        if st.button("報告書を生成"):
            prompt = f"身体状況:{status}, 部位:{side}。以下の状況を、医学的断定を避けて介護報告書として清書して：{raw_text}"
            
            # 生成実行
            response = model.generate_content(prompt)
            st.write("### 清書結果")
            st.write(response.text)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.info("APIキーが有効でないか、モデル名が現在のリージョンで利用できない可能性があります。")

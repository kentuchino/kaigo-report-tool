import streamlit as st
import google.generativeai as genai
import os

# 画面設定
st.set_page_config(page_title="介護報告支援", layout="wide")
st.title("🛡️ 介護報告書支援ツール")

# Secretsからキーを取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Secretsに 'GEMINI_API_KEY' が設定されていません。")
else:
    # APIの設定
    genai.configure(api_key=api_key)
    
    # フォームの作成
    col1, col2 = st.columns(2)
    with col1:
        status = st.selectbox("身体状況", ["全介助", "一部介助", "自立"])
        side = st.selectbox("部位", ["健側", "患側", "該当なし"])
    with col2:
        category = st.selectbox("事故種別", ["内出血", "誤薬", "転倒", "その他"])
        raw_text = st.text_area("状況メモ（箇条書きでOK）", height=150)

    if st.button("報告書を生成する", use_container_width=True):
        if not raw_text:
            st.warning("状況メモを入力してください。")
        else:
            try:
                # 段落（インデント）を下げて実行内容を書く
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                prompt = f"""
                あなたは介護施設のリスクマネジメント担当者です。
                以下の情報を元に、医学的断定を避けつつ、状況把握を深める報告書を作成してください。
                
                身体状況: {status}
                部位: {side}
                事象: {category}
                メモ: {raw_text}
                
                構成：
                1. 発生状況（客観的に）
                2. 要因の推察（断定せず、多角的に）
                3. 不足している確認事項（スタッフへの質問）
                """
                
                response = model.generate_content(prompt)
                st.divider()
                st.subheader("🤖 AIによる清書結果")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

import streamlit as st
import google.generativeai as genai

# 1. 画面設定
st.set_page_config(page_title="介護報告支援", layout="wide")
st.title("🛡️ 介護報告書支援ツール（5W1H対応版）")

# 2. Secretsからキーを取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Secretsに 'GEMINI_API_KEY' が設定されていません。")
else:
    genai.configure(api_key=api_key)
    
    # 利用可能なモデルを取得
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
    except:
        pass

    # 3. 入力フォームの構成
    st.subheader("📝 事故の概要")
    c1, c2, c3 = st.columns(3)
    with c1:
        category = st.selectbox("事故種別", ["内出血", "誤薬", "転倒", "誤嚥", "その他"])
    with c2:
        status = st.selectbox("対象者の状態", ["全介助", "一部介助", "自立"])
    with c3:
        side = st.selectbox("麻痺・部位", ["健側", "患側", "該当なし"])

    st.divider()
    st.subheader("🕒 5W1H詳細（分かるところだけでOK）")
    
    # 5W1Hを2列で配置
    f1, f2 = st.columns(2)
    with f1:
        when = st.text_input("いつ（When）", placeholder="例：1月30日 朝食後")
        where = st.text_input("どこで（Where）", placeholder="例：食堂

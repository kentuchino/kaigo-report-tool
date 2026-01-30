import streamlit as st
import google.generativeai as genai

# --- API設定 ---
# 実際の運用時はStreamlitのSecrets機能に保存するのが安全です
genai.configure(api_key="AIzaSyBIS0_vhTMcVRDz9MH9D68DKHbKU1hLG9Q")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 画面レイアウト ---
st.set_page_config(layout="wide", page_title="介護報告書支援ツール")
st.title("🛡️ 介護事故報告書・作成支援（PC専用版）")
st.caption("※入力データは保存されません。作成後は介護ソフトへ貼り付けてください。")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1. 状況の選択・入力")
    c1, c2 = st.columns(2)
    with c1:
        status = st.selectbox("身体状況", ["全介助", "一部介助", "自立"])
        side = st.selectbox("部位", ["健側", "患側", "該当なし・両側"])
    with c2:
        mobility = st.selectbox("移動手段", ["車椅子", "独歩", "臥床"])
        category = st.selectbox("事故種別", ["内出血", "誤薬", "転倒", "誤嚥", "その他"])
    
    raw_text = st.text_area("状況メモ（箇条書きで入力してください）", height=250)
    generate_btn = st.button("報告書を生成・チェックする", use_container_width=True)

with col_right:
    st.subheader("2. AIの添削・清書結果")
    if generate_btn and raw_text:
        prompt = f"""
        あなたは介護施設のリスクマネジメント担当者です。
        以下の【入力情報】を元に、事故報告書を清書してください。
        
        【厳守ルール】
        1. 医学的断定は絶対に避ける。「～の可能性がある」「～と推論される」等の表現に徹すること。
        2. 「内出血」等の用語はそのまま使用して良い。
        3. 身体状況（{status}）、部位（{side}）、移動手段（{mobility}）の情報を文中に含めること。
        
        【入力情報】
        種別：{category} / 状況：{raw_text}
        
        【出力構成】
        ① 発生状況（客観的事実）
        ② 要因の推察（断定せず、多角的に）
        ③ 【重要】不足している確認事項（スタッフへの逆質問）
        """
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.button("📋 結果をコピーする（ブラウザ機能を利用）")

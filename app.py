import streamlit as st
import google.generativeai as genai

# 1. 画面設定
st.set_page_config(page_title="介護報告支援", layout="wide")
st.title("🛡️ 介護報告書支援ツール")

# 2. Secretsからキーを取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Secretsに 'GEMINI_API_KEY' が設定されていません。")
else:
    genai.configure(api_key=api_key)
    
    # 【ここが修正のキモ】利用可能なモデルを自動でリストアップする
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
    except Exception as e:
        st.error(f"モデル一覧の取得に失敗しました: {e}")

    # 3. フォームの作成
    col1, col2 = st.columns(2)
    with col1:
        status = st.selectbox("身体状況", ["全介助", "一部介助", "自立"])
        side = st.selectbox("部位", ["健側", "患側", "該当なし"])
    with col2:
        category = st.selectbox("事故種別", ["内出血", "誤薬", "転倒", "その他"])
        # 自動で見つかったモデルを表示（なければ直接指定）
        model_choice = st.selectbox("使用するAIモデル", available_models if available_models else ["models/gemini-1.5-flash", "models/gemini-pro"])

    raw_text = st.text_area("状況メモ（箇条書きでOK）", height=150, placeholder="例：朝食後、Aさんの薬をBさんに誤薬。バイタル異常なし。")

    if st.button("報告書を生成する", use_container_width=True):
        if not raw_text:
            st.warning("状況メモを入力してください。")
        else:
            with st.spinner("AIが清書中..."):
                try:
                    # 選ばれたモデルで実行
                    model = genai.GenerativeModel(model_choice)
                    
                    prompt = f"""
                    あなたは介護施設のリスクマネジメント担当者です。
                    以下の情報を元に、客観的事実に基づいた事故報告書を清書してください。
                    
                    【入力情報】
                    身体状況: {status} / 部位: {side} / 事象: {category}
                    現場メモ: {raw_text}
                    
                    【出力構成】
                    1. 発生状況（「～と思われる」などの断定を避け、客観的に記述）
                    2. 要因の推察（人・物・環境の視点で）
                    3. 確認事項（スタッフへの逆質問）
                    """
                    
                    response = model.generate_content(prompt)
                    st.divider()
                    st.subheader("🤖 AIによる清書結果")
                    st.write(response.text)
                    st.info("※この内容をコピーして介護ソフト等に貼り付けてください。")
                    
                except Exception as e:
                    st.error(f"生成エラー: {e}")
                    st.info("APIキーの権限が不足しているか、モデル名が正しくありません。")

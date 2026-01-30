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
    
    # 利用可能なモデルを取得
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
    except:
        pass

    # 3. フォームの作成
    col1, col2 = st.columns(2)
    with col1:
        status = st.selectbox("身体状況", ["全介助", "一部介助", "自立"])
        side = st.selectbox("部位", ["健側", "患側", "該当なし"])
    with col2:
        category = st.selectbox("事故種別", ["内出血", "誤薬", "転倒", "その他"])
        model_choice = st.selectbox("使用するAIモデル", available_models if available_models else ["models/gemini-1.5-flash"])

    raw_text = st.text_area("状況メモ（箇条書きでOK）", height=150, placeholder="例：朝食後、Aさんの薬をBさんに誤薬。")

    if st.button("報告書を生成する", use_container_width=True):
        if not raw_text:
            st.warning("状況メモを入力してください。")
        else:
            with st.spinner("5W1Hを確認し、清書中..."):
                try:
                    model = genai.GenerativeModel(model_choice)
                    
                    # プロンプトの強化：5W1Hの確認を指示
                    prompt = f"""
                    あなたは介護施設のベテランリスクマネジメント担当者です。
                    以下の情報を元に報告書を作成してください。
                    
                    【入力情報】
                    身体状況: {status} / 部位: {side} / 事象: {category}
                    現場メモ: {raw_text}
                    
                    【重要ミッション】
                    1. 現場メモを分析し、「5W1H（いつ・どこで・誰が・何を・なぜ・どのように）」のうち、不足している要素があれば、冒頭で必ずスタッフに質問してください。
                    2. その上で、得られている情報のみを使って、医学的断定を避けた客観的な報告書を清書してください。
                    
                    【出力構成】
                    ■ 5W1Hの確認（不足があれば指摘、あれば「充足」と記載）
                    ■ 発生状況（客観的に）
                    ■ 要因の推察（人・物・環境の視点）
                    ■ 今後の観察事項・対応
                    """
                    
                    response = model.generate_content(prompt)
                    st.divider()
                    st.subheader("🤖 AIによる分析・清書結果")
                    st.write(response.text)
                    st.info("※不足情報を追記して再度生成すると、より正確な報告書になります。")
                    
                except Exception as e:
                    st.error(f"生成エラー: {e}")

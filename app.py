import streamlit as st
import google.generativeai as genai

# 1. 画面設定（ワイドモード）
st.set_page_config(page_title="介護報告支援", layout="wide")
st.title("🛡️ 介護報告書支援ツール")

# 2. Secretsからキーを取得
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Secretsに 'GEMINI_API_KEY' が設定されていません。")
else:
    genai.configure(api_key=api_key)
    
    # モデルの取得
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
    except:
        pass

    # --- 画面を左右に分割 ---
    col_input, col_result = st.columns([1, 1.2])

    # --- 左側：入力フォーム ---
    with col_input:
        st.subheader("📝 報告データ入力")
        
        # 基本情報
        with st.container(border=True):
            st.caption("基本情報")
            c1, c2 = st.columns(2)
            with c1:
                category = st.selectbox("事故種別", ["内出血", "誤薬", "転倒", "転落", "誤嚥", "離設", "その他"])
            with c2:
                status = st.selectbox("対象者の状態", ["全介助", "一部介助", "自立"])
            side = st.text_input("受傷部位・発生場所", placeholder="例：左膝、食堂の椅子周辺")

        # 5W1H情報
        with st.container(border=True):
            st.caption("5W1H（いつ・どこで・誰が）")
            when = st.text_input("いつ", placeholder="例：1/30 15:30頃")
            where = st.text_input("どこで", placeholder="例：居室、トイレ、廊下")
            who = st.text_input("だれが", placeholder="例：介助職員A、巡回中の職員B")

        # 詳細・処置
        with st.container(border=True):
            st.caption("詳細状況（経緯・処置）")
            what = st.text_input("何が・何を", placeholder="例：車椅子からの立ち上がり、朝食後の薬")
            how = st.text_area("具体的な経緯・原因の推測", placeholder="例：目を離した隙に立ち上がろうとして尻もちをついた", height=100)
            action = st.text_area("バイタル・処置・報告", placeholder="例：BP130/80、意識清明。冷罨法実施。看護師・家族報告済み", height=100)

        generate_btn = st.button("報告書を生成・分析する", use_container_width=True, type="primary")

    # --- 右側：AIの結果表示 ---
    with col_result:
        st.subheader("🤖 事実のみの報告書（だ・である調）")
        
        if generate_btn:
            if not how and not category:
                st.warning("状況を入力してください。")
            else:
                with st.spinner("事実に基づき清書中..."):
                    try:
                        target_model = available_models[0] if available_models else "models/gemini-1.5-flash"
                        model = genai.GenerativeModel(target_model)
                        
                        prompt = f"""
                        介護現場の公式な事故報告書を作成せよ。
                        
                        【入力情報】
                        - 種別: {category} / 状態: {status} / 部位・場所: {side}
                        - 5W1H等: いつ:{when} / どこで:{where} / 誰が:{who} / 内容:{what}
                        - 詳細経緯: {how} / 処置・その他: {action}
                        
                        【厳守ルール】
                        1. 敬語・丁寧語（です・ます）は一切禁止。「だ・である」調で記述せよ。
                        2. 感情的な表現や余計な修飾語を省き、客観的事実のみを記述せよ。
                        3. 不足している5W1Hがあれば、最後に「【未確定事項】」として箇条書きで記せ。
                        4. 医学的断定は避け、「～の可能性がある」「～と推察される」という表現を用いよ。
                        
                        【構成】
                        ■ 発生状況（時系列に沿った客観的事実）
                        ■ 実施した処置（バイタル、対応内容）
                        ■ 要因分析（本人・環境・介助の視点）
                        ■ 再発防止策
                        ■ 【未確定事項】（不足情報がある場合のみ）
                        """
                        
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.divider()
                        st.success("作成された内容をコピーして使用してください。")
                        
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
        else:
            st.info("左側のフォームに入力してボタンを押すと、結果が表示されます。")

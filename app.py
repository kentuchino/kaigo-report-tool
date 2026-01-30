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
    col_input, col_result = st.columns([1, 1.2])  # 右側（結果）を少し広めに設定

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
            when = st.text_input("いつ", placeholder="例：1/30 15:30頃（または日勤帯など）")
            where = st.text_input("どこで", placeholder="例：居室トイレ、廊下、浴室")
            who = st.text_input("だれが（発見・介助）", placeholder="例：介助職員A、巡回中の職員B")

        # 詳細・処置
        with st.container(border=True):
            st.caption("詳細状況（なにを・なぜ・どのように・処置）")
            what = st.text_input("何が・何を", placeholder="例：車椅子からの立ち上がり、朝食後の薬")
            how = st.text_area("具体的な経緯・原因の推測", placeholder="例：目を離した隙に立ち上がろうとして尻もちをついた", height=100)
            action = st.text_area("バイタル・処置・報告", placeholder="例：BP130/80、意識清明。冷罨法実施。看護師・家族報告済み", height=100)

        generate_btn = st.button("報告書を生成・分析する", use_container_width=True, type="primary")

    # --- 右側：AIの結果表示 ---
    with col_result:
        st.subheader("🤖 AIによる分析・清書")
        
        if generate_btn:
            # 最低限の入力チェック
            if not how and not category:
                st.warning("左側のフォームに状況を入力してください。")
            else:
                with st.spinner("情報を整理して清書しています..."):
                    try:
                        target_model = available_models[0] if available_models else "models/gemini-1.5-flash"
                        model = genai.GenerativeModel(target_model)
                        
                        prompt = f"""
                        あなたは介護現場のリスクマネジメント担当者です。
                        スタッフが入力した断片的な情報を整理し、専門的な事故報告書を作成してください。
                        
                        【入力情報】
                        - 種別: {category}
                        - 状態: {status} / 部位・場所: {side}
                        - 5W1H等: いつ:{when} / どこで:{where} / 誰が:{who} / 内容:{what}
                        - 詳細経緯: {how}
                        - 処置・その他: {action}
                        
                        【出力のルール】
                        1. 冒頭に「5W1Hの確認」を行い、不足があれば優しく指摘してください。
                        2. 「発生状況」を客観的かつ簡潔に清書してください。
                        3. 「要因分析」を、本人要因・環境要因・介助要因の視点で推察してください。
                        4. 「今後の対策」として、再発防止案を具体的に提案してください。
                        5. 専門用語（例：不穏、独歩、失納など）を適切に使用し、医学的断定は避けてください。
                        """
                        
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.divider()
                        st.success("作成された内容をコピーして使用してください。")
                        
                    except Exception as e:
                        st.error(f"生成エラーが発生しました。しばらく時間を置いてから再度お試しください。: {e}")
        else:
            st.info("左側のフォームに入力してボタンを押すと、ここに清書結果が表示されます。")

import streamlit as st
import google.generativeai as genai

# 1. 画面設定（ワイドモード）
st.set_page_config(page_title="介護報告支援", layout="wide")
st.title("🛡️ 介護報告書支援ツール：プロフェッショナル版")

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
    col_input, col_result = st.columns([1, 1])  # 1:1の比率で分割

    # --- 左側：入力フォーム ---
    with col_input:
        st.subheader("📝 報告データ入力")
        
        with st.expander("基本情報", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                category = st.selectbox("事故種別", ["内出血", "誤薬", "転倒", "誤嚥", "離設", "その他"])
                status = st.selectbox("対象者の状態", ["全介助", "一部介助", "自立"])
            with c2:
                level = st.selectbox("緊急度", ["低（経過観察）", "中（受診検討）", "高（救急・急変）"])
                side = st.text_input("部位・場所", placeholder="例：右前腕、食堂入口")

        with st.expander("5W1H（いつ・どこで・だれが）", expanded=True):
            when = st.text_input("いつ（発生日時）", placeholder="例：1/30 15:30頃")
            where = st.text_input("どこで", placeholder="例：居室トイレ、廊下")
            who = st.text_input("だれが（発見者・介助者）", placeholder="例：介助職員A、通りがかった職員B")

        with st.expander("詳細状況（なにを・なぜ・どのように）", expanded=True):
            what = st.text_input("対象物・内容", placeholder="例：夕食後の薬、車椅子")
            why = st.text_input("原因の仮説", placeholder="例：ふらつき、確認漏れ")
            how = st.text_area("具体的な経緯", placeholder="例：移乗時に足がもつれ、尻もちをついた", height=100)

        with st.expander("追加情報（バイタル・処置など）"):
            vital = st.text_input("バイタル・状態", placeholder="例：BP130/80, 傷なし, 意識清明")
            action = st.text_area("実施した応急処置", placeholder="例：冷罨法実施、看護師報告済み", height=80)
            others = st.text_area("その他特記事項", placeholder="例：ご家族へ連絡済み、主治医指示待ち", height=80)

        generate_btn = st.button("報告書を生成・分析する", use_container_width=True, type="primary")

    # --- 右側：AIの結果表示 ---
    with col_result:
        st.subheader("🤖 AIによる分析・清書")
        
        if generate_btn:
            # 入力チェック（最低限「どのように」があれば進む）
            if not how and not what:
                st.warning("左側のフォームに状況を入力してください。")
            else:
                with st.spinner("AIがプロの視点で分析中..."):
                    try:
                        # 確実に動作するモデルを選択
                        target_model = available_models[0] if available_models else "models/gemini-1.5-flash"
                        model = genai.GenerativeModel(target_model)
                        
                        prompt = f"""
                        介護現場の事故報告書をプロの視点で作成してください。
                        
                        【入力情報】
                        - 種別: {category} (緊急度: {level})
                        - 状態: {status} / 部位: {side}
                        - 5W1H: いつ:{when} / どこで:{where} / 誰が:{who} / 何を:{what} / なぜ:{why} / どのように:{how}
                        - 追加情報: バイタル:{vital} / 処置:{action} / その他:{others}
                        
                        【出力ルール】
                        1. 冒頭に「5W1Hの充足確認」を行い、不足があれば優しく指摘してください。
                        2. 発生状況を客観的な専門用語を用いて清書してください（「～のせい」は禁止）。
                        3. 要因分析（人・物・環境）を行ってください。
                        4. 今後の対策と家族への説明案を提案してください。
                        """
                        
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.success("↑この内容をコピーして使用してください")
                        
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
        else:
            st.info("左側のフォームを入力し、「報告書を生成する」ボタンを押してください。ここに結果が表示されます。")

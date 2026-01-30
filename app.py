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
        where = st.text_input("どこで（Where）", placeholder="例：食堂のB様席、居室、トイレ等")
        who = st.text_input("だれが（Who）", placeholder="例：介助中の職員、発見した職員等")
    with f2:
        what = st.text_input("何を（What）", placeholder="例：Aさんの薬を、右腕の内出血を")
        why = st.text_input("なぜ（Why）", placeholder="例：確認不足、ふらつき、原因不明等")
        how = st.text_area("どのように（How）", placeholder="例：薬を口に入れた、床に座り込んでいた", height=68)

    st.divider()
    model_choice = st.selectbox("AIモデル選択（通常はそのままでOK）", available_models if available_models else ["models/gemini-1.5-flash"])

    if st.button("報告書を生成する", use_container_width=True):
        # 入力された5W1Hを統合
        info_summary = f"""
        いつ：{when} / どこで：{where} / 誰が：{who}
        何を：{what} / なぜ：{why} / どのように：{how}
        """
        
        # 5W1Hのうち、どれか一つでも入力されているかチェック
        if not any([when, where, who, what, why, how]):
            st.warning("5W1Hの項目のうち、少なくとも一つは入力してください。")
        else:
            with st.spinner("情報を整理し、清書中..."):
                try:
                    model = genai.GenerativeModel(model_choice)
                    
                    prompt = f"""
                    あなたは介護施設の管理職です。スタッフが入力した断片的な情報を整理し、正式な報告書を作成してください。
                    
                    【入力データ】
                    種別：{category} / 身体状況：{status} / 部位：{side}
                    5W1H情報：{info_summary}
                    
                    【依頼事項】
                    1. 不足している5W1Hの要素があれば、冒頭で「追加確認が必要な事項」として箇条書きで教えてください。
                    2. 医学的断定（「～のせいだ」など）を避け、「～の可能性がある」「～と推察される」という表現を使って清書してください。
                    
                    【構成】
                    ■ 報告書の清書（発生状況・対応）
                    ■ 要因の分析
                    ■ 今後の注意点
                    ■ 不足している情報の確認
                    """
                    
                    response = model.generate_content(prompt)
                    st.divider()
                    st.subheader("🤖 AIによる分析・報告書案")
                    st.write(response.text)
                    st.success("作成された内容をコピーし、介護ソフトの報告欄に貼り付けてください。")
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

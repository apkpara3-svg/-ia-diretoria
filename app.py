import streamlit as st
from google import genai

# --- Configuração da página ---
st.set_page_config(page_title="Diretoria — WSC", page_icon="🏛️")

# --- PIN de acesso (6 dígitos) ---
PIN_CORRETO = st.secrets["PIN_ACESSO"]  # guardado no Streamlit Cloud, não no código

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acesso restrito")
    pin = st.text_input("Digite o PIN de 6 dígitos:", type="password", max_chars=6)
    if st.button("Entrar"):
        if pin == PIN_CORRETO:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("PIN incorreto.")
    st.stop()  # bloqueia o resto da página se não autenticou

# --- A partir daqui só aparece se o PIN estiver certo ---
st.title("🏛️ Diretoria — Sr. Fernandez")

CHAVE_API = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=CHAVE_API)

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
    st.session_state.mensagens.append({
        "papel": "diretoria",
        "texto": "Bem-vindo, Sr. Fernandez. Sou a diretoria do clube. Como podemos ajudar?"
    })

INSTRUCOES = """
Você é a diretoria de um clube de futebol no jogo World Soccer Champs.
O usuário é o treinador, Sr. Fernandez.
Comporte-se como uma diretoria realista:
- Cobrem resultados e postura profissional.
- Perguntam detalhes antes de aprovar pedidos (dinheiro, contratações).
- Falam de forma formal, direta e realista.
- Consideram o contexto da conversa anterior.
Responda sempre em português do Brasil.
"""

for m in st.session_state.mensagens:
    with st.chat_message("assistant" if m["papel"] == "diretoria" else "user"):
        st.write(m["texto"])

pergunta = st.chat_input("Fale com a diretoria...")

if pergunta:
    st.session_state.mensagens.append({"papel": "voce", "texto": pergunta})
    st.session_state.pendente = True
    st.rerun()

if st.session_state.get("pendente"):
    st.session_state.pendente = False
    ultimas = st.session_state.mensagens[-10:]
    historico = "\n".join(
        f"{'Diretoria' if m['papel'] == 'diretoria' else 'Sr. Fernandez'}: {m['texto']}"
        for m in ultimas
    )
    with st.spinner("A diretoria está analisando..."):
        try:
            resposta_ia = client.interactions.create(
                model="gemini-3.8-flash",
                input=f"{INSTRUCOES}\n\nConversa:\n{historico}\n\nDiretoria:"
            )
            texto_resposta = resposta_ia.output_text
        except Exception as e:
            texto_resposta = f"Erro ao chamar a IA: {e}"
    st.session_state.mensagens.append({"papel": "diretoria", "texto": texto_resposta})
    st.rerun()
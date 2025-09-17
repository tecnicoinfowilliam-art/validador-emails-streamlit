import streamlit as st
import pandas as pd
import smtplib
import dns.resolver
from validate_email_address import validate_email
from io import StringIO

st.set_page_config(page_title="Validador de E-mails", layout="wide")
st.title("📬 Validador Inteligente de E-mails")

st.markdown("""
Este aplicativo valida e-mails por 3 etapas:
1. **Formato**
2. **Domínio (DNS MX)**
3. **Caixa de entrada (SMTP)**
""")

uploaded_file = st.file_uploader("📁 Envie seu arquivo CSV com uma coluna chamada `email`", type=["csv"])

def verificar_email(email):
    if not validate_email(email):
        return "❌ Formato Inválido"

    dominio = email.split('@')[-1]
    try:
        registros_mx = dns.resolver.resolve(dominio, 'MX')
        servidor_mx = str(registros_mx[0].exchange)
    except:
        return "❌ Domínio Inválido"

    try:
        servidor = smtplib.SMTP()
        servidor.connect(servidor_mx, 25)
        servidor.helo("example.com")
        servidor.mail("validador@dominiofake.com")
        codigo, _ = servidor.rcpt(email)
        servidor.quit()

        if codigo in [250, 251]:
            return "✅ Válido"
        else:
            return "⚠️ Não Verificável"
    except:
        return "⚠️ Não Verificável"

if uploaded_file:
    try:
        # Lê o CSV tentando detectar vírgula ou ponto e vírgula, e encoding Latin1 (mais seguro para arquivos com acentos)
        df = pd.read_csv(uploaded_file, sep=';', encoding="latin1")
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo CSV. Verifique se ele está bem formatado com uma coluna chamada 'email'.\n\nDetalhes técnicos: {e}")
        st.stop()

    if "email" not in df.columns:
        st.error("❌ O arquivo deve conter uma coluna chamada 'email'.")
        st.stop()
    else:
        st.success("✅ Arquivo carregado com sucesso!")
        if st.button("🚀 Iniciar Validação"):
            status = []
            with st.spinner("🔍 Validando e-mails..."):
                for email in df["email"]:
                    status.append(verificar_email(email))
            df["status"] = status

            st.subheader("📊 Resultados da Validação")
            st.dataframe(df, use_container_width=True)

            validos = df[df["status"] == "✅ Válido"]
            csv = validos[["email"]].to_csv(index=False)
            st.download_button(
                "📥 Baixar e-mails válidos (.csv)",
                csv,
                file_name="emails_validos.csv",
                mime="text/csv"
            )

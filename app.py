import streamlit as st

# Configuração da página inicial
st.set_page_config(
    page_title="Dashboard OAB"
)

# Função para renderizar a Home
def home():
    st.write("# Bem-vindo ao Dashboard OAB 👋")
    st.markdown(
        """
        Esse é o **painel inicial** do sistema.  
        Aqui você pode navegar entre as áreas de **Marketing** e **Financeiro** usando o menu lateral.

        ---
        ### 📌 Dicas de uso:
        - Clique em *Emails* para ver campanhas de marketing por email.
        - Clique em *Redes Sociais* para acompanhar o desempenho online.
        - Clique em *Custo* ou *Faturamento* para ver indicadores financeiros.
        """
    )

# Definição das páginas de navegação
pages = {
    "Home": [  # precisa ser uma lista
        st.Page(home, title="Comece por aqui")
    ],
    "Marketing": [
        st.Page("emails_page.py", title="Emails"),
        st.Page("redes_page.py", title="Redes Sociais"),
    ],
    "Financeiro": [
        st.Page("custo_page.py", title="Custo"),
        st.Page("faturamento_page.py", title="Faturamento"),
    ],
}

# Criando a navegação
pg = st.navigation(pages)

# Rodando a página escolhida
pg.run()

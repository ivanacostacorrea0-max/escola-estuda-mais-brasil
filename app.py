import sqlite3
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Escola Estuda Mais Brasil", page_icon="📚", layout="centered"
)


# --- BANCO DE DADOS ---
def init_db():
  conn = sqlite3.connect("escola.db")
  cursor = conn.cursor()

  # Tabela de Usuários (Alunos e Admin)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT UNIQUE,
            senha TEXT,
            tipo TEXT,
            curso_permitido TEXT
        )
    """)

  # Criar Admin padrão se não existir (CNPJ: 18.852.415/0001-59 - Ivana)
  cursor.execute(
      "SELECT * FROM usuarios WHERE email = ?", ("admin@estudamais.com",)
  )
  if not cursor.fetchone():
    cursor.execute(
        """
            INSERT INTO usuarios (nome, email, senha, tipo, curso_permitido)
            VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Ivana Corrêa (Admin)",
            "admin@estudamais.com",
            "admin123",
            "admin",
            "TODOS",
        ),
    )

  conn.commit()
  conn.close()


init_db()

# --- DADOS DOS CURSOS ---
CURSOS_DISPONIVEIS = [
    "Formação em Resinagem e Joias do Infinito",
    "Marketing Digital para Empreendedores",
    "Direito para Iniciantes",
    "Inglês Prático para o Dia a Dia",
]


# --- TELA DE LOGIN ---
def login():
  st.title("📚 Escola Estuda Mais Brasil")
  st.subheader("Faça seu login para acessar o seu curso")

  email = st.text_input("E-mail")
  senha = st.text_input("Senha", type="password")

  if st.button("Entrar"):
    conn = sqlite3.connect("escola.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome, tipo, curso_permitido FROM usuarios WHERE email = ?"
        " AND senha = ?",
        (email, senha),
    )
    user = cursor.fetchone()
    conn.close()

    if user:
      st.session_state["user_id"] = user[0]
      st.session_state["user_nome"] = user[1]
      st.session_state["user_tipo"] = user[2]
      st.session_state["curso_permitido"] = user[3]
      st.success(f"Seja bem-vinda(o), {user[1]}! 💖")
      st.rerun()
    else:
      st.error("E-mail ou senha incorretos. Verifique com a administração.")


# --- PAINEL DO ALUNO (Acesso Restrito ao Curso Comprado) ---
def painel_aluno():
  st.sidebar.title(f"Olá, {st.session_state['user_nome']}! 🎓")
  if st.sidebar.button("Sair da Conta"):
    for key in list(st.session_state.keys()):
      del st.session_state[key]
    st.rerun()

  st.title("🎓 Área do Aluno - Escola Estuda Mais Brasil")
  curso_do_aluno = st.session_state["curso_permitido"]

  st.info(
      f"✨ Seu acesso exclusivo está liberado para o curso: **{curso_do_aluno}**"
  )

  st.markdown("---")
  st.subheader("📺 Suas Videoaulas e Conteúdos")

  # Exibe o conteúdo apenas do curso que ele comprou
  if curso_do_aluno in CURSOS_DISPONIVEIS:
    st.markdown(f"### Módulo Principal: {curso_do_aluno}")
    st.write(
        "Aqui estão as suas aulas gravadas e materiais de apoio para download."
    )

    # Exemplo de videoaula simulada
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    st.download_button(
        label="📥 Baixar Apostila do Curso (PDF)",
        data="Conteúdo da apostila exclusiva...",
        file_name="apostila_curso.pdf",
        mime="application/pdf",
    )
  else:
    st.warning(
        "Nenhum curso liberado no momento. Entre em contato pelo WhatsApp para"
        " liberar o seu acesso!"
    )


# --- PAINEL DO ADMINISTRADOR (Você cadastra e restringe o curso) ---
def painel_admin():
  st.sidebar.title("Painel da Diretoria 👩‍💼")
  menu = st.sidebar.selectbox(
      "Menu Admin", ["Matricular Aluno", "Ver Alunos Matriculados"]
  )

  if st.sidebar.button("Sair da Conta"):
    for key in list(st.session_state.keys()):
      del st.session_state[key]
    st.rerun()

  if menu == "Matricular Aluno":
    st.title("📝 Cadastrar e Liberar Acesso para o Aluno")
    st.write(
        "Após fechar a venda pelo WhatsApp, cadastre o aluno aqui escolhendo"
        " exatamente o curso que ele comprou."
    )

    with st.form("form_matricula"):
      nome_aluno = st.text_input("Nome Completo do Aluno")
      email_aluno = st.text_input("E-mail do Aluno (Será o login)")
      senha_aluno = st.text_input("Senha Provisória", value="123456")
      curso_escolhido = st.selectbox(
          "Selecione o Curso Comprado", CURSOS_DISPONIVEIS
      )

      enviar = st.form_submit_button("Liberar Matrícula e Acesso")

      if enviar:
        if nome_aluno and email_aluno:
          try:
            conn = sqlite3.connect("escola.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                            INSERT INTO usuarios (nome, email, senha, tipo, curso_permitido)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                (
                    nome_aluno,
                    email_aluno,
                    senha_aluno,
                    "aluno",
                    curso_escolhido,
                ),
            )
            conn.commit()
            conn.close()
            st.success(
                f"Matrícula realizada com sucesso para **{nome_aluno}**! O"
                f" aluno agora tem acesso exclusivo ao curso: **{curso_escolhido}**"
                " 🎉"
            )
          except sqlite3.IntegrityError:
            st.error(
                "Este e-mail já está cadastrado no sistema. Use outro e-mail."
            )
        else:
          st.error("Por favor, preencha o nome e o e-mail do aluno.")

  elif menu == "Ver Alunos Matriculados":
    st.title("📋 Alunos Cadastrados na Escola")
    conn = sqlite3.connect("escola.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, email, curso_permitido FROM usuarios WHERE tipo = 'aluno'"
    )
    alunos = cursor.fetchall()
    conn.close()

    if alunos:
      for a in alunos:
        st.write(
            f"👤 **Nome:** {a[0]} | 📧 **E-mail:** {a[1]} | 📚 **Curso Liberado:**"
            f" {a[2]}"
        )
        st.markdown("---")
    else:
      st.info("Nenhum aluno matriculado ainda.")


# --- CONTROLE DE NAVEGAÇÃO PRINCIPAL ---
if "user_id" not in st.session_state:
  login()
else:
  if st.session_state["user_tipo"] == "admin":
    painel_admin()
  else:
    painel_aluno()

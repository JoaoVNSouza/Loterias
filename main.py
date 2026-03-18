"""
📊 Resultados Loterias
│
├── 🎯 Criar Jogo
├── 📋 Conferir Jogos
├── 🔍 Filtros
├── 📈 Resultados e Estatísticas
"""

# Libs
import streamlit as st
import sqlite3
import pandas as pd
import os
import sqlite3
from datetime import datetime

# Constantes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")
LOTERIAS = {
    "megasena": {
        "total": 60,
        "min": 6,
        "max": 15,
        "colunas": 10,
        'bolas_sorteadas': 6
    },
    "lotofacil": {
        "total": 25,
        "min": 15,
        "max": 20,
        "colunas": 5,
        'bolas_sorteadas': 15
    }
}

if "numeros_selecionados" not in st.session_state:
    st.session_state.numeros_selecionados = set()

if "grid_version" not in st.session_state:
    st.session_state.grid_version = 0

if "jogos_selecionados" not in st.session_state:
    st.session_state.jogos_selecionados = []

if "data_ini_input" not in st.session_state:
    st.session_state.data_ini_input = None

if "data_fim_input" not in st.session_state:
    st.session_state.data_fim_input = None

if "concurso_selecionado_input" not in st.session_state:
    st.session_state.concurso_selecionado_input = "Todos"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn


def limpar_checkboxes():
    st.session_state.numeros_selecionados = set()
    st.session_state.grid_version += 1  # <- troca TODAS as keys
    st.rerun()


# Site.
st.set_page_config(page_title="Resultados", layout="wide")
st.title("🎰 Resultados das Loterias")


# Criar jogos.
st.header("🎯 Novo jogo")

loteria = st.selectbox("Loteria", LOTERIAS.keys())

config = LOTERIAS[loteria]
total_numeros = config["total"]
min_numeros = config["min"]
max_numeros = config["max"]
colunas = config["colunas"]
bolas_sorteadas = config['bolas_sorteadas']


# Importar dados.
try:
    df = pd.read_excel(

        # 500 últimos resultados
        f'resultados/{loteria}_resultados.xlsx', engine='openpyxl')[5:507]
    # Definir linha 0 como cabeçalho
    df.columns = df.iloc[0]
    df = df[1:]
    # Data somente data
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
    df.reset_index(drop=True, inplace=True)


except FileNotFoundError:
    df = pd.DataFrame()
    st.warning("Arquivo de resultados não encontrado.")


# Escolha dos números
st.markdown("### Escolha os números")
cols = st.columns(colunas)


for i in range(1, total_numeros + 1):
    col = cols[(i - 1) % colunas]

    if col.checkbox(
        f"{i:02d}",
        key=f"num_{st.session_state.grid_version}_{i}"
    ):
        st.session_state.numeros_selecionados.add(i)
    else:
        st.session_state.numeros_selecionados.discard(i)

# Contador
qtd = len(st.session_state.numeros_selecionados)
st.info(
    f"🔢 Números escolhidos: **{qtd}** / {min_numeros}"
)


col1, col2 = st.columns([1, 8], gap='small')
with col1:
    if st.button("Salvar jogo"):
        if qtd < min_numeros:
            st.error("Quantidade insuficiente de números")
        elif qtd > max_numeros:
            st.error("Quantidade excessiva de números")
        else:
            conn = get_conn()
            cur = conn.cursor()
            st.write(loteria)
            cur.execute(
                """
                INSERT INTO jogo (loteria_id)
                SELECT id FROM loteria WHERE nome = ?
                """,
                (loteria,)
            )

            jogo_id = cur.lastrowid

            # Ordenar números antes de salvar
            st.session_state.numeros_selecionados = sorted(
                st.session_state.numeros_selecionados
            )
            for n in st.session_state.numeros_selecionados:
                cur.execute(
                    "INSERT INTO jogo_numero (jogo_id, numero) VALUES (?, ?)",
                    (jogo_id, n)
                )

            conn.commit()
            conn.close()

            st.success("Jogo salvo com sucesso!")
            limpar_checkboxes()

with col2:
    if st.button('Limpar'):
        limpar_checkboxes()

st.divider()

# Selecionar jogos para conferencia.
st.header("📋 Conferir jogos")

conn = get_conn()
try:
    df_jogos = pd.read_sql("""
        SELECT
            j.id,
            MAX(j.data_criacao) AS dt,
            GROUP_CONCAT(jn.numero, ', ') AS numeros
        FROM
            jogo j
        JOIN
            jogo_numero jn ON j.id = jn.jogo_id
        WHERE
            j.loteria_id = (SELECT id FROM loteria WHERE nome = ?)
        GROUP BY
            j.id
        ORDER BY j.id DESC;
    """, conn, params=(loteria,)).set_index("id")
except Exception as e:
    df_jogos = pd.DataFrame()
finally:
    conn.close()

if not df_jogos.empty:
    st.session_state.jogos_selecionados = st.multiselect(
        "Selecione os jogos",
        df_jogos.index.tolist(),
        default=st.session_state.jogos_selecionados,
        format_func=lambda x: f"J{x} - {df_jogos.loc[x, 'numeros']}"
    )

    if st.button("Selecionar todos"):
        st.session_state.jogos_selecionados = df_jogos.index.tolist()
        st.rerun()
else:
    st.info("Nenhum jogo cadastrado para esta loteria.")

if st.session_state.jogos_selecionados:
    df_jogos_selecionados = df_jogos.loc[st.session_state.jogos_selecionados]

st.divider()

# Filtros de data / concurso / etc.
st.header("🔍 Comparativo Resultados")

col1, col2, col3, col4 = st.columns(4)

with col1:
    data_ini = st.date_input(
        "Data inicial", value=st.session_state.data_ini_input, key="data_ini_input")

with col2:
    data_fim = st.date_input(
        "Data final", value=st.session_state.data_fim_input, key="data_fim_input")

with col3:
    consursos = df['Concurso'].dropna().unique().tolist()
    concurso_selecionado = st.selectbox("Concurso", ["Todos"] + consursos,
                                        key="concurso_selecionado_input")


def reset_filtros():
    st.session_state.data_ini_input = None
    st.session_state.data_fim_input = None
    st.session_state.concurso_selecionado_input = "Todos"


with col4:
    st.button("Reset filtros", on_click=reset_filtros)

st.divider()

# Exibir resultados, gráficos, estatísticas.
st.header("📈 Resultados e Estatísticas")

if st.session_state.jogos_selecionados:

    # Filtrar por data e concurso
    if concurso_selecionado != "Todos":
        df = df[df['Concurso'] == concurso_selecionado]

    if st.session_state.data_ini_input is not None and st.session_state.data_fim_input is not None:
        df = df[(df['Data'] >= pd.to_datetime(data_ini)) &
                (df['Data'] <= pd.to_datetime(data_fim))]

    col1, col2 = st.columns([1, 0.4], gap="large")
    with col1:
        # DataFrame apenas com concurso e data
        df_resultados = df.copy()[['Concurso']]

        # Dict dos selecionados
        # selecionados_dict = {i: [] for i in range(len(df_jogos_selecionados))}
        selecionados_dict = {}

        for jogo_id, numeros in df_jogos_selecionados['numeros'].items():
            selecionados_dict[jogo_id] = [
                int(num) for num in numeros.split(', ')
            ]

        # Verifica se teve acertos.
        for i in df.index:
            numeros_sorteados = df.loc[i, [f'bola {j}' for j in range(
                1, bolas_sorteadas + 1)]].values.tolist()

            for id in selecionados_dict:
                count = 0
                for numero in selecionados_dict[id]:
                    if numero in numeros_sorteados:
                        count += 1
                df_resultados.loc[i, f'Acertos jogo {id}'] = count

        st.dataframe(df_resultados, use_container_width=True, hide_index=True)

    with col2:

        # Estatísticas
        st.markdown("### Acertos por jogo")
        st.selectbox("Selecione o jogo", selecionados_dict.keys(),
                     key="id_jogo_selecionado")
        id_jogo_selecionado = st.session_state.id_jogo_selecionado

        # Quantidade acertos maiores ou iguais a 11
        count_acertos = [0, 0, 0, 0, 0]
        for acerto in df_resultados[f'Acertos jogo {id_jogo_selecionado}']:
            if loteria == 'lotofacil':
                if acerto == 11:
                    count_acertos[0] += 1
                elif acerto == 12:
                    count_acertos[1] += 1
                elif acerto == 13:
                    count_acertos[2] += 1
                elif acerto == 14:
                    count_acertos[3] += 1
                elif acerto == 15:
                    count_acertos[4] += 1

            else:
                if acerto == 4:
                    count_acertos[0] += 1
                elif acerto == 5:
                    count_acertos[1] += 1
                elif acerto == 6:
                    count_acertos[2] += 1

        if loteria == 'lotofacil':
            st.write(f"11 acertos: {count_acertos[0]}")
            st.write(f"12 acertos: {count_acertos[1]}")
            st.write(f"13 acertos: {count_acertos[2]}")
            st.write(f"14 acertos: {count_acertos[3]}")
            st.write(f"15 acertos: {count_acertos[4]}")
        else:
            st.write(f"4 acertos: {count_acertos[0]}")
            st.write(f"5 acertos: {count_acertos[1]}")
            st.write(f"6 acertos: {count_acertos[2]}")

    # Premiações nesse período
    st.markdown("### Premiações Sugerida")

    if data_ini is not None and data_fim is not None and loteria == "lotofacil":
        st.write(
            f"Período: {data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")

        PREMIACAO_LOTOFACIL = {11: 7, 12: 14, 13: 35}
        valor_total = 0
        for jogo in selecionados_dict:
            acertos = (
                df_resultados[f'Acertos jogo {jogo}']
                .value_counts()
                .sort_index()
                .loc[lambda x: x.index >= 11]
                .rename_axis("Acertos")
                .reset_index(name="Quantidade")
            )
            acertos['Valor_total'] = (
                acertos['Quantidade'] *
                acertos['Acertos'].map(PREMIACAO_LOTOFACIL).fillna(0)
            )

            valor_jogo = acertos['Valor_total'].sum()
            valor_total += valor_jogo

        st.write(f"Valor total: R$ {valor_total:.2f}")

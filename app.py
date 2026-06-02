import streamlit as st
import matplotlib.pyplot as plt
import math
from fpdf import FPDF

st.set_page_config(page_title="Planificação", layout="centered")

st.title("📊 Calculadora de Planificação")

# Inputs
principal = st.number_input("Largura da Bobina Original (cm)", value=54)
comprimento_bobina = st.number_input("Comprimento da Folha (cm)", value=96)
bobina = st.number_input("Largura da Bobina Alternativa (cm)", value=79)
gramatura_original = st.number_input("Gramatura Original (g/m²)", value=250)
gramatura_alternativa = st.number_input("Gramatura Alternativa (g/m²)", value=250)
qtde_folhas = st.number_input("Quantidade de Folhas", value=3500)

if st.button("CALCULAR"):

    peso_liquido_original = (principal * comprimento_bobina * gramatura_original * qtde_folhas) / 10000000
    peso_bruto_original = peso_liquido_original * 1.022

    qtd_principal = int(bobina // principal)
    largura_ocupada = qtd_principal * principal
    sobra = bobina - largura_ocupada

    folhas_por_passada = qtd_principal
    passadas = math.ceil(qtde_folhas / folhas_por_passada)

    peso_liquido_alternativo = (bobina * comprimento_bobina * gramatura_alternativa * passadas) / 10000000
    peso_bruto_alternativo = peso_liquido_alternativo * 1.022

    cortes = [
        ("REFORÇO G", 12, 24.5),
        ("REFORÇO GG", 31, 15.2),
        ("REFORÇO GARRAFA", 12.5, 7.5)
    ]

    def calcular_melhor_orientacao(larg_area, alt_area, larg_peca, alt_peca):
        qx1 = int(larg_area // larg_peca)
        qy1 = int(alt_area // alt_peca)
        total1 = qx1 * qy1

        qx2 = int(larg_area // alt_peca)
        qy2 = int(alt_area // larg_peca)
        total2 = qx2 * qy2

        if total2 > total1:
            return total2, alt_peca, larg_peca, qx2, qy2
        else:
            return total1, larg_peca, alt_peca, qx1, qy1

    resultados = []

    for nome, larg, comp in cortes:
        total, l, a, qx, qy = calcular_melhor_orientacao(
            sobra, comprimento_bobina, larg, comp
        )
        resultados.append({
            "nome": nome,
            "total": total,
            "largura": l,
            "comprimento": a,
            "qx": qx,
            "qy": qy
        })

    area_total = bobina * comprimento_bobina
    area_principal = qtd_principal * principal * comprimento_bobina

    for r in resultados:
        area_pecas = r["total"] * (r["largura"] * r["comprimento"])
        r["area_total_aproveitada"] = area_principal + area_pecas
        r["perda"] = area_total - r["area_total_aproveitada"]
        r["perda_percentual"] = (r["perda"] / area_total) * 100

    op1, op2, op3 = resultados

if op1["total"] == 0 and op2["total"] == 0:
    melhor_base = None
elif op1["perda_percentual"] <= op2["perda_percentual"]:
    melhor_base = op1
else:
    melhor_base = op2

if melhor_base is None:
    melhor_final = op3 if op3["total"] > 0 else None
else:
    diferenca = melhor_base["perda_percentual"] - op3["perda_percentual"]

    if op3["total"] > 0 and diferenca >= 5:
        melhor_final = op3
    else:
        melhor_final = melhor_base

    st.subheader("✅ Resultado")

    st.text(f"""
Necessidade:
Bobina: {principal} cm | Comprimento: {comprimento_bobina} cm

Alternativo:
Bobina: {bobina} cm
Passadas: {passadas}

Melhor ponta: {melhor_final['nome']}
Peças: {melhor_final['total']}
Perda: {melhor_final['perda_percentual']:.2f}%
""")

   fig, ax = plt.subplots(figsize=(10, 5))

# principais
for i in range(qtd_principal):
    x = i * principal
    ax.add_patch(plt.Rectangle(
        (x, 0), principal, comprimento_bobina,
        edgecolor='black', facecolor='skyblue'
    ))

# área da sobra (cinza)
ax.add_patch(plt.Rectangle(
    (largura_ocupada, 0), sobra, comprimento_bobina,
    edgecolor='black', facecolor='lightgray'
))

# desenhar pontas (IMPORTANTE)
if melhor_final:
    total_comp = melhor_final["qy"] * melhor_final["comprimento"]
    offset_y = (comprimento_bobina - total_comp) / 2

    for i in range(melhor_final["qx"]):
        for j in range(melhor_final["qy"]):
            x = largura_ocupada + i * melhor_final["largura"]
            y = offset_y + j * melhor_final["comprimento"]

            ax.add_patch(plt.Rectangle(
                (x, y),
                melhor_final["largura"],
                melhor_final["comprimento"],
                edgecolor='black',
                facecolor='orange'
            ))

ax.set_xlim(0, bobina)
ax.set_ylim(0, comprimento_bobina)
ax.set_title("Plano de Corte Completo")
ax.axis('off')

st.pyplot(fig)

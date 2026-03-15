import streamlit as st
import pandas as pd
import datetime
import base64
import unicodedata

# --- FUNÇÕES AUXILIARES ---
def formata_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formata_md(valor_str):
    return valor_str.replace("R$", r"R\$")

def limpar_texto(texto):
    if pd.isna(texto): return ""
    texto = str(texto).strip().lower()
    if texto == 'nan': return ""
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MargemSegura Premium", page_icon="🛡️", layout="wide")

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .card-indicador {
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .card-azul { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); }
    .card-amarelo { background: linear-gradient(135deg, #f5af19 0%, #f12711 100%); }
    .card-vermelho { background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%); }
    .titulo-card { font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; margin-bottom: 8px; }
    .valor-card { font-size: 28px; font-weight: bold; margin: 0; }
    [data-testid="stMetric"] { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 5px solid #1e3c72; }
    [data-testid="stMetricValue"] { color: #1e1e1e; font-size: 22px; font-weight: bold; }
    [data-testid="stMetricLabel"] * { color: #555555 !important; font-weight: bold !important; font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ MargemSegura - Inteligência de Precificação")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Cenário Econômico")
selic_anual = st.sidebar.slider(
    "Selic Atual (% ao ano)", 8.0, 15.0, 11.25,
    help="Taxa básica de juros. O rendimento mínimo se o dinheiro estivesse parado no banco."
)
inflacao_mensal = st.sidebar.slider(
    "Inflação Reposição (mês %)", 0.0, 10.0, 1.50,
    help="Estimativa de aumento de custo no fornecedor para repor o estoque."
)
selic_mensal = (selic_anual / 12)

# ==========================================
# ESTRUTURA DE ABAS (Foco Total em Varejo/Revenda)
# ==========================================
tab1, tab2 = st.tabs(["🧮 Simulação Individual (Balcão)", "📊 Raio-X em Massa (Gestão)"])

# ==========================================
# ABA 1: SIMULAÇÃO INDIVIDUAL (REVENDA)
# ==========================================
with tab1:
    st.subheader("Simulador de Operação Comercial")
    col1, col2 = st.columns(2)
    with col1:
        produto = st.text_input("Nome do Produto", value="Smartphone Premium")
        preco_venda = st.number_input("Preço de Venda Praticado (R$)", min_value=1.0, value=3500.00)
        custo_aquisicao = st.number_input("Custo de Compra Original (R$)", min_value=1.0, value=2800.00)
    with col2:
        imposto_percent = st.number_input("Imposto Médio sobre Venda (%)", value=8.00)
        taxa_cartao = st.number_input("Taxa de Transação (Cartão/Plataforma %)", value=2.50)

    custo_reposicao = custo_aquisicao * (1 + (inflacao_mensal / 100))
    valor_imposto = preco_venda * (imposto_percent / 100)
    valor_taxas = preco_venda * (taxa_cartao / 100)
    lucro_real = preco_venda - valor_imposto - valor_taxas - custo_reposicao
    margem_liquida = (lucro_real / preco_venda) * 100

    st.markdown("---")
    if lucro_real < 0:
        st.error(f"🚨 ALERTA CRÍTICO: Operação em prejuízo absoluto de {formata_brl(abs(lucro_real))} por unidade.")
    elif margem_liquida < selic_mensal:
        st.warning(f"⚠️ ATENÇÃO: Margem líquida de {margem_liquida:.2f}%. Inferior ao custo de oportunidade (Selic).")
    else:
        st.success(f"✅ OPERAÇÃO SAUDÁVEL: Margem de {margem_liquida:.2f}% (Rendimento superior à Selic).")

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("💰 Lucro Líquido", formata_brl(lucro_real))
    with m2: st.metric("📈 Margem Real", f"{margem_liquida:.2f}%".replace(".", ","))
    with m3: st.metric("🏛️ Impostos", formata_brl(valor_imposto))
    with m4: st.metric("💳 Taxas", formata_brl(valor_taxas))
    with m5: st.metric("📦 Custo Reposição", formata_brl(custo_reposicao))

# ==========================================
# ABA 2: RAIO-X EM MASSA E PLANO DE AÇÃO VIP
# ==========================================
with tab2:
    st.subheader("Auditoria de Portfólio Paramétrica")
    st.info("Varredura sistêmica para identificação de ofensores de caixa baseada em planilhas de estoque.")
    
    col_x1, col_x2 = st.columns(2)
    with col_x1:
        imposto_lote = st.number_input("Carga Tributária Média (%)", value=12.0, help="Imposto médio estimado para a simulação do lote inteiro.")
    with col_x2:
        taxa_lote = st.number_input("Taxa de Transação Média (%)", value=3.5, help="Custo financeiro médio das vendas.")

    arquivo = st.file_uploader("Importar Exportação do ERP (CSV ou Excel)", type=["csv", "xlsx", "xls"], help="O sistema utiliza Inteligência Artificial para mapear automaticamente as colunas essenciais.")

    if arquivo is not None:
        try:
            # MOTOR DE LEITURA CEGA E IA (Header Hunter)
            nome_arquivo = arquivo.name.lower()
            try:
                if nome_arquivo.endswith('.csv'):
                    df = pd.read_csv(arquivo, sep=";", encoding="utf-8", header=None)
                    if len(df.columns) < 2:
                        arquivo.seek(0)
                        df = pd.read_csv(arquivo, sep=",", encoding="utf-8", header=None)
                        if len(df.columns) < 2: raise ValueError("CSV disfarçado")
                else:
                    df = pd.read_excel(arquivo, header=None)
            except Exception:
                arquivo.seek(0)
                try: df = pd.read_excel(arquivo, header=None)
                except:
                    arquivo.seek(0)
                    df = pd.read_csv(arquivo, sep=";", encoding="latin1", header=None)
            
            dicionario_sinonimos = {
                'Produto': ['produto', 'nome', 'item', 'descricao', 'sku', 'titulo', 'mercadoria', 'referencia'],
                'Custo': ['custo', 'valor de custo', 'preco de custo', 'custo aquisicao', 'valor compra', 'custo unitario'],
                'Preco': ['preco', 'venda', 'valor de venda', 'preco de venda', 'preco final', 'tabela', 'pvp']
            }

            linha_cabecalho = -1
            max_matches = 0
            mapa_colunas_final = {}
            colunas_vistas_radar = []

            for idx, row in df.head(30).iterrows():
                matches = 0
                mapa_temp = {}
                valores_linha = [limpar_texto(str(val)) for val in row.values]
                
                for padrao, sinonimos in dicionario_sinonimos.items():
                    for i, val in enumerate(valores_linha):
                        if i in mapa_temp: continue 
                        if val in sinonimos or any(sin in val for sin in sinonimos if len(sin) >= 4):
                            mapa_temp[i] = padrao
                            matches += 1
                            break
                
                if matches > max_matches:
                    max_matches = matches
                    linha_cabecalho = idx
                    mapa_colunas_final = mapa_temp
                    colunas_vistas_radar = [str(v).strip() for v in row.values if str(v).strip() and str(v).strip() != 'nan']
                    if max_matches == 3: break

            if max_matches < 2:
                st.error("🚨 O Radar não conseguiu identificar a estrutura da tabela de preços.")
                st.stop()
            
            novas_colunas = df.iloc[linha_cabecalho].astype(str).tolist()
            for i, padrao in mapa_colunas_final.items(): novas_colunas[i] = padrao 
            df.columns = novas_colunas
            df = df.iloc[linha_cabecalho:].reset_index(drop=True)
            
            colunas_faltantes = [col for col in ['Produto', 'Custo', 'Preco'] if col not in df.columns]
            if colunas_faltantes:
                st.error(f"🚨 Falha no mapeamento da coluna: **{', '.join(colunas_faltantes)}**.")
                st.stop()
            
            df['Custo'] = df['Custo'].astype(str).str.replace('R$', '').str.replace(' ', '').str.replace(',', '.')
            df['Preco'] = df['Preco'].astype(str).str.replace('R$', '').str.replace(' ', '').str.replace(',', '.')
            df['Custo'] = pd.to_numeric(df['Custo'], errors='coerce')
            df['Preco'] = pd.to_numeric(df['Preco'], errors='coerce')
            df = df.dropna(subset=['Custo', 'Preco'])
            
            df['Custo Reposição'] = df['Custo'] * (1 + (inflacao_mensal / 100))
            df['Impostos'] = df['Preco'] * (imposto_lote / 100)
            df['Taxas'] = df['Preco'] * (taxa_lote / 100)
            df['Lucro Real (R$)'] = df['Preco'] - df['Impostos'] - df['Taxas'] - df['Custo Reposição']
            df['Margem Real (%)'] = (df['Lucro Real (R$)'] / df['Preco']) * 100

            margem_alvo = (selic_mensal + 2.0) / 100
            fator_divisao = 1 - (imposto_lote/100) - (taxa_lote/100) - margem_alvo
            df['Preco Sugerido'] = df['Custo Reposição'] / fator_divisao

            def define_status(margem):
                if margem < 0: return '🔴 Prejuízo'
                elif margem < selic_mensal: return '🟡 Alerta (Abaixo Selic)'
                else: return '🟢 Saudável'
            
            df['Status'] = df['Margem Real (%)'].apply(define_status)

            produtos_prejuizo = df[df['Lucro Real (R$)'] < 0]
            dinheiro_perdido = produtos_prejuizo['Lucro Real (R$)'].sum()
            produtos_alerta = df[(df['Margem Real (%)'] >= 0) & (df['Margem Real (%)'] < selic_mensal)]

            st.markdown("### 💸 O Mapa do Dinheiro")
            col_a, col_b, col_c = st.columns(3)
            with col_a: st.markdown(f'<div class="card-indicador card-azul"><div class="titulo-card">SKUs Analisados</div><div class="valor-card">{len(df)}</div></div>', unsafe_allow_html=True)
            with col_b: st.markdown(f'<div class="card-indicador card-amarelo"><div class="titulo-card">Itens em Alerta (Risco)</div><div class="valor-card">{len(produtos_alerta)}</div></div>', unsafe_allow_html=True)
            with col_c: st.markdown(f'<div class="card-indicador card-vermelho"><div class="titulo-card">Erosão de Caixa / Lote</div><div class="valor-card">{formata_brl(abs(dinheiro_perdido))}</div></div>', unsafe_allow_html=True)

            st.markdown("### 📊 Raio-X Operacional")
            df_display = df[['Produto', 'Custo', 'Preco', 'Lucro Real (R$)', 'Status']].copy()
            df_display.index = range(1, len(df_display) + 1)
            df_display['Custo'] = df_display['Custo'].apply(lambda x: f"R$ {x:.2f}")
            df_display['Preco'] = df_display['Preco'].apply(lambda x: f"R$ {x:.2f}")
            df_display['Lucro Real (R$)'] = df_display['Lucro Real (R$)'].apply(lambda x: f"R$ {x:.2f}")
            
            st.dataframe(df_display.style.applymap(
                lambda val: 'background-color: #ffcccc; color: black' if '🔴' in str(val) else ('background-color: #fff3cd; color: black' if '🟡' in str(val) else ''),
                subset=['Status']
            ), use_container_width=True)

            # ==========================================
            # PLANO DE AÇÃO CORPORATIVO (O VALOR DO SISTEMA)
            # ==========================================
            if len(produtos_prejuizo) > 0:
                st.markdown("---")
                st.markdown("## 🏁 Diretrizes Executivas: Estratégia de Recuperação")
                st.info("📊 **Matriz de Intervenção gerada com sucesso.** O motor lógico identificou os gargalos operacionais. Aplique as diretrizes recomendadas abaixo para estancar perdas imediatas e proteger a saúde do negócio (Foco nos **Top 10 Ofensores de Caixa** - Regra de Pareto).")
                
                estrategias_html = ""
                contador_estrategias = 0
                
                taticas_leves = [
                    "Ajuste Silencioso de Gôndola: O consumidor apresenta baixa sensibilidade de preço para {aumento:.1f}%. Aplique a remarcação de etiqueta. Risco de ruptura de vendas quase nulo.",
                    "Cross-Merchandising: Ajuste a tabela hoje. Para mascarar o aumento perante o cliente, reposicione este produto ao lado de 'SKUs Curva A' de alta rotatividade.",
                    "Intervenção D+0: Produto com demanda inelástica. Ajuste o valor no sistema imediatamente. A diferença no preço final é absorvida sem grande atrito pelo consumidor."
                ]
                taticas_medias = [
                    "Teste de Elasticidade Escalonado: Um repasse de {aumento:.1f}% apresenta risco. Execute o aumento em duas ondas quinzenais e monitorize a quebra de volume diária.",
                    "Revisão de Planograma (Ancoragem): Suba o preço e altere a exposição para a altura dos olhos. Adicione um concorrente *premium* ao lado para ancorar o valor percebido.",
                    "Acionamento de Trade Marketing: O repasse é significativo. Pressione o fabricante/fornecedor para enviar material de PDV e bonificações que justifiquem o novo patamar de preço."
                ]
                taticas_pesadas = [
                    "Reestruturação de Procurement: A estrutura atual destrói valor. O repasse total eliminará o giro. Acione Compras imediatamente: trave o custo base de R$ {custo:.2f} e exija Rebate Comercial retroativo.",
                    "Gestão de SKU (Loss Leader): Produto com margem cronicamente negativa. Remova investimentos em Marketing. Utilize no encarte estritamente como 'isca' para gerar tráfego em loja.",
                    "Intervenção Crítica (Phase-Out): Preço de mercado incompatível com a sua estrutura fiscal. Inicie o esgotamento do estoque atual e substitua por fornecedor regional ou marca própria."
                ]

                piores = produtos_prejuizo.sort_values(by='Lucro Real (R$)').head(10)
                
                for index, row in piores.iterrows():
                    aumento_necessario = (row['Preco Sugerido'] / row['Preco']) - 1
                    percentual_aumento = aumento_necessario * 100
                    
                    if aumento_necessario <= 0.08:
                        prazo = "⚡ Ação Imediata (D+0 a 15 dias)"
                        tatica = taticas_leves[contador_estrategias % len(taticas_leves)].format(aumento=percentual_aumento)
                    elif aumento_necessario <= 0.25:
                        prazo = "🛡️ Curto/Médio Prazo (15 a 45 dias)"
                        tatica = taticas_medias[contador_estrategias % len(taticas_medias)].format(aumento=percentual_aumento)
                    else:
                        prazo = "📅 Revisão Estratégica (Phase-Out/Renegociação)"
                        tatica = taticas_pesadas[contador_estrategias % len(taticas_pesadas)].format(custo=row['Custo'])

                    preco_atual = f"R$ {row['Preco']:.2f}"
                    preco_alvo = formata_brl(row['Preco Sugerido'])
                    
                    st.markdown(f"#### 🎯 **{row['Produto']}**")
                    st.markdown(f"**Ação Recomendada:** Atualizar de {formata_md(preco_atual)} ➡️ **Alvo: {formata_md(preco_alvo)}**")
                    st.markdown(f"> **Tática Corporativa:** {tatica}")
                    st.markdown(f"> **Cronograma:** {prazo}")
                    st.markdown("---")
                    
                    estrategias_html += f"""
                    <div style='background-color: #f9f9f9; padding: 15px; border-left: 5px solid #cb2d3e; margin-bottom: 15px;'>
                        <h4 style='margin: 0; color: #333;'>{row['Produto']}</h4>
                        <p style='margin: 5px 0;'><strong>Preço Atual:</strong> {preco_atual} &rarr; <strong>Alvo Necessário:</strong> <span style='color: #cb2d3e; font-weight: bold;'>{preco_alvo}</span></p>
                        <p style='margin: 5px 0;'><strong>Tática Recomendada:</strong> {tatica}</p>
                        <p style='margin: 5px 0;'><strong>Cronograma:</strong> {prazo}</p>
                    </div>
                    """
                    contador_estrategias += 1

                html_template = f"""
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Relatório Executivo MargemSegura</title>
                    <style>
                        body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #333; line-height: 1.6; max-width: 800px; margin: auto; padding: 20px; }}
                        .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
                        .resumo-box {{ background-color: #fff3cd; border: 1px solid #ffeeba; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                        .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #777; border-top: 1px solid #ddd; padding-top: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Auditoria de Estoque e Margem</h1>
                        <p>Documento Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                    </div>
                    <div class="resumo-box">
                        <h3 style="margin-top: 0; color: #856404;">⚠️ Sumário do Risco de Capital (Ponto Cego)</h3>
                        <p>O sistema identificou <strong>{len(produtos_prejuizo)} SKUs</strong> a operar com margem líquida destrutiva (Ralos Financeiros).</p>
                        <p><strong>Ameaça de Caixa Projetada:</strong> Projetando um volume estático de apenas 100 transações/mês para os itens em alerta, a hemorragia financeira no caixa será de <strong style="color: #cb2d3e;">{formata_brl(abs(dinheiro_perdido) * 100)}</strong> ao mês.</p>
                    </div>
                    <h3>Diretrizes Táticas (Matriz dos Principais Ofensores)</h3>
                    {estrategias_html}
                    <div class="footer">Inteligência Financeira processada pelo motor MargemSegura.</div>
                </body>
                </html>
                """
                
                b64 = base64.b64encode(html_template.encode('utf-8')).decode('utf-8')
                href = f'<a href="data:text/html;base64,{b64}" download="Auditoria_MargemSegura.html" style="background-color: #1e3c72; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin-top: 10px;">📥 Baixar Relatório Corporativo (PDF / E-mail)</a>'
                st.markdown(href, unsafe_allow_html=True)

            else:
                st.success("✅ **Excelência Operacional Alcançada.** A análise não detetou SKUs com margens destrutivas no presente cenário.")

        except Exception as e:
            st.error(f"Erro na validação paramétrica. Detalhe técnico: {e}")
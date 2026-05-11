import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# ==========================================
# 1. CONFIGURACIÓN Y ESTILO
# ==========================================
st.set_page_config(page_title="Rappi Competitive Intelligence V2", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    .metric-card {background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #FF4646; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
    h1, h2, h3 {color: #FF4646;}
    .stSidebar {background-color: #ffffff;}
    .target-sug {font-size: 0.85em; color: #155724; font-weight: bold; background: #d4edda; padding: 5px 8px; border-radius: 5px; display: inline-block; margin-top: 8px; border: 1px solid #c3e6cb;}
    .target-warning {font-size: 0.85em; color: #856404; font-weight: bold; background: #fff3cd; padding: 5px 8px; border-radius: 5px; display: inline-block; margin-top: 8px; border: 1px solid #ffeeba;}
    .strategic-box {background: #ffffff; padding: 20px; border-left: 6px solid #2980b9; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
    .strat-title {color: #2c3e50; font-size: 1.1em; margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Rappi Competitive Intelligence System")
st.markdown("Análisis Estratégico | **Segmentación Geográfica y Priorización**")

# ==========================================
# 2. MOTOR DE DATOS (HOMOLOGACIÓN TOTAL)
# ==========================================
@st.cache_data
def load_and_process_data():
    try:
        df_comp = pd.read_csv(os.path.join("competidores", "COMPETITORS_INPUT_METRICS.csv"))
        df_rappi = pd.read_csv(os.path.join("base_de_datos", "RAW_INPUT_METRICS.csv"))
        
        if 'COMPETITOR' not in df_rappi.columns:
            df_rappi.insert(0, 'COMPETITOR', 'Rappi')
        
        time_cols = []
        for i in range(9): 
            col_c = [c for c in df_comp.columns if f'L{i}W' in c]
            col_r = [c for c in df_rappi.columns if f'L{i}W' in c]
            
            if col_c and col_r:
                nuevo_nombre = 'Actual' if i == 0 else f'W-{i}'
                df_comp = df_comp.rename(columns={col_c[0]: nuevo_nombre})
                df_rappi = df_rappi.rename(columns={col_r[0]: nuevo_nombre})
                time_cols.append(nuevo_nombre)

        for df_temp in [df_comp, df_rappi]:
            df_temp.dropna(subset=['ZONE', 'METRIC'], inplace=True)
            df_temp['ZONE'] = df_temp['ZONE'].astype(str).str.strip().str.title()

        # Homologación de Zonas
        relacion_rappi = {
            'Polanco': 'Roma-Polanco',
            'Roma Norte': 'Roma-Polanco',
            'Condesa': 'Roma-Polanco',
            'Del Valle': 'Del Valle-Narvarte',
            'Narvarte': 'Del Valle-Narvarte',
            'Santa Fe': 'Santafe',
            'Mixcoac': 'Del Valle-Narvarte',
            'Coyoacan': 'Coyoacan-Pedregal',
            'Coyoacán': 'Coyoacan-Pedregal',
            'Xochimilco': 'Xochimilco'
        }

        rappi_expanded = []
        for zone_comp, zone_rappi in relacion_rappi.items():
            data_temp = df_rappi[df_rappi['ZONE'] == zone_rappi].copy()
            data_temp['ZONE_COMPETIDOR'] = zone_comp
            rappi_expanded.append(data_temp)
            
        zonas_mapeadas_rappi = list(relacion_rappi.values())
        data_unmapped = df_rappi[~df_rappi['ZONE'].isin(zonas_mapeadas_rappi)].copy()
        data_unmapped['ZONE_COMPETIDOR'] = data_unmapped['ZONE']
        rappi_expanded.append(data_unmapped)
        
        df_rappi_final = pd.concat(rappi_expanded, ignore_index=True)
        df_comp['ZONE_COMPETIDOR'] = df_comp['ZONE']
        
        df_master = pd.concat([df_comp, df_rappi_final], ignore_index=True)

        # Homologación de Métricas
        def homologar_metrica(m):
            m_str = str(m).strip().lower()
            if ('delivery time' in m_str or 'tiempo' in m_str or 
               ('eta' in m_str and 'retail' not in m_str and 'detail' not in m_str)): 
                return 'Tiempo Estimado de Entrega'
            elif 'markdown' in m_str or 'promo' in m_str or 'discount' in m_str: 
                return 'Descuentos y Promociones'
            elif 'service fee' in m_str: 
                return 'Service Fee de la Plataforma'
            elif 'delivery fee' in m_str or 'precio final' in m_str: 
                return 'Precio Final (Delivery Fee)'
            return str(m).strip()

        df_master['METRIC'] = df_master['METRIC'].apply(homologar_metrica)

        # Deduplicación
        columnas_agrupar = ['COMPETITOR', 'ZONE_COMPETIDOR', 'METRIC']
        df_master = df_master.groupby(columnas_agrupar)[time_cols].mean().reset_index()

        # Clasificación
        presencia = df_master.groupby('ZONE_COMPETIDOR')['COMPETITOR'].unique()
        def clasificar_availability(comps):
            comps_set = set(comps)
            if {'Rappi', 'Uber Eats', 'DiDi Food'}.issubset(comps_set): return "All the competitors with Rappi"
            elif 'Rappi' in comps_set and len(comps_set) == 1: return "Zones Rappi exclusive"
            else: return "All the competitors but no Rappi"

        df_master['AVAILABILITY'] = df_master['ZONE_COMPETIDOR'].map(presencia.apply(clasificar_availability).to_dict())

        zone_type_map = {'Polanco': 'Wealthy', 'Santa Fe': 'Wealthy', 'Bosques': 'Wealthy', 'Interlomas': 'Wealthy', 'Iztapalapa': 'Non-Wealthy', 'Tlahuac': 'Non-Wealthy', 'Milpa Alta': 'Non-Wealthy', 'Ecatepec': 'Non-Wealthy'}
        df_master['ZONE_TYPE'] = df_master['ZONE_COMPETIDOR'].map(lambda x: zone_type_map.get(x, 'Mixed'))

        prioritization_map = {'Polanco': 'High Priority', 'Roma Norte': 'High Priority', 'Condesa': 'High Priority', 'Del Valle': 'High Priority', 'Santa Fe': 'Prioritized', 'Coyoacan': 'Prioritized', 'Narvarte': 'Prioritized', 'Iztapalapa': 'Not Prioritized', 'Tlahuac': 'Not Prioritized', 'Xochimilco': 'Not Prioritized'}
        df_master['PRIORITIZATION'] = df_master['ZONE_COMPETIDOR'].map(lambda x: prioritization_map.get(x, 'Prioritized'))

        return df_master, time_cols

    except Exception as e:
        st.error(f"Error en el motor de datos: {e}")
        return pd.DataFrame(), []

df_master, columnas_historicas = load_and_process_data()

# ==========================================
# 3. FILTROS LATERALES
# ==========================================
if not df_master.empty:
    st.sidebar.header("Geographic Coverage Filters")
    
    avail_sel = st.sidebar.multiselect("1. Availability", df_master['AVAILABILITY'].unique(), default=["All the competitors with Rappi"])
    type_sel = st.sidebar.multiselect("2. Zone Type", df_master['ZONE_TYPE'].unique(), default=df_master['ZONE_TYPE'].unique())
    prio_sel = st.sidebar.multiselect("3. Prioritization", df_master['PRIORITIZATION'].unique(), default=df_master['PRIORITIZATION'].unique())

    df_filtered = df_master[
        df_master['AVAILABILITY'].isin(avail_sel) & 
        df_master['ZONE_TYPE'].isin(type_sel) & 
        df_master['PRIORITIZATION'].isin(prio_sel)
    ]

    if not df_filtered.empty:
        zonas_disponibles = sorted(df_filtered['ZONE_COMPETIDOR'].unique())
        zona_sel = st.sidebar.selectbox("4. Seleccionar Zona Granular:", zonas_disponibles)
    else:
        st.warning("No hay zonas que cumplan con los 3 filtros seleccionados.")
        st.stop()

    # ==========================================
    # 4. DASHBOARD
    # ==========================================
    tab1, tab2 = st.tabs(["📋 Resumen Ejecutivo (Core 3)", "📈 Análisis Secundario (8 Semanas)"])

    with tab1:
        zona_info = df_filtered[df_filtered['ZONE_COMPETIDOR'] == zona_sel].iloc[0]
        st.subheader(f"Análisis de Competitividad: {zona_sel}")
        st.markdown(f"**Disponibilidad:** {zona_info['AVAILABILITY']} | **Tipo:** {zona_info['ZONE_TYPE']} | **Prioridad:** {zona_info['PRIORITIZATION']}")
        
        df_zona = df_master[df_master['ZONE_COMPETIDOR'] == zona_sel]
        metricas_core = ['Tiempo Estimado de Entrega', 'Service Fee de la Plataforma', 'Precio Final (Delivery Fee)']
        
        cols = st.columns(3)
        for i, metrica in enumerate(metricas_core):
            with cols[i]:
                df_m_filtrado = df_zona[df_zona['METRIC'] == metrica]
                val_rappi = df_m_filtrado[df_m_filtrado['COMPETITOR'] == 'Rappi']['Actual'].mean()
                datos_comp = df_m_filtrado[df_m_filtrado['COMPETITOR'] != 'Rappi']['Actual']
                val_comp_mean = datos_comp.mean()
                val_comp_min = datos_comp.min() 
                
                is_pct = metrica == 'Service Fee de la Plataforma'
                
                # --- CORRECCIÓN DEL ERROR DE SINTAXIS AQUÍ ---
                def fmt(val): 
                    if val is None or np.isnan(val):
                        return "N/D"
                    if is_pct:
                        return f"{round(val, 2)}%"
                    return f"{round(val, 2)}"
                # ---------------------------------------------
                
                target_rappi = None
                target_label = ""
                
                if not np.isnan(val_comp_min) and val_comp_min > 0:
                    if metrica in ['Service Fee de la Plataforma', 'Precio Final (Delivery Fee)']:
                        target_rappi = val_comp_min * 0.90
                        target_label = f"🎯 Target (-10%): {fmt(target_rappi)}"
                    elif metrica == 'Tiempo Estimado de Entrega':
                        target_rappi = val_comp_min
                        target_label = f"🎯 Target (Igualar): {fmt(target_rappi)}"

                if not np.isnan(val_rappi):
                    delta = round(val_rappi - val_comp_mean, 2) if not np.isnan(val_comp_mean) else None
                    st.metric(metrica, fmt(val_rappi), delta=fmt(delta) if delta is not None else None, delta_color="inverse")
                    
                    if target_rappi is not None:
                        brecha = round(val_rappi - target_rappi, 2)
                        if val_rappi <= target_rappi:
                            st.markdown(f"<div class='target-sug'>✅ Superioridad Lograda. {target_label}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='target-warning'>⚠️ Bajar {fmt(brecha)} pts para {target_label}</div>", unsafe_allow_html=True)
                                
                elif not np.isnan(val_comp_mean):
                    if target_rappi is not None:
                        st.metric(metrica, fmt(val_comp_min), delta="Mejor Valor Competencia", delta_color="off")
                        st.markdown(f"<div class='target-sug'>{target_label}</div>", unsafe_allow_html=True)
                    else:
                        st.metric(metrica, "N/D")
                else:
                    st.metric(metrica, "N/D")

        st.divider()

        col_chart, col_info = st.columns([2, 1])
        with col_chart:
            st.markdown("### Posicionamiento Core 3 y Expectativa")
            df_chart = df_zona[df_zona['METRIC'].isin(metricas_core)].copy()
            target_rows = []
            for metrica in metricas_core:
                df_m = df_zona[df_zona['METRIC'] == metrica]
                val_min = df_m[df_m['COMPETITOR'] != 'Rappi']['Actual'].min()
                if not np.isnan(val_min) and val_min > 0:
                    t_val = val_min * 0.90 if metrica != 'Tiempo Estimado de Entrega' else val_min
                    target_rows.append({'COMPETITOR': '🎯 Target Esperado (Rappi)', 'METRIC': metrica, 'Actual': t_val, 'ZONE_COMPETIDOR': zona_sel})

            if target_rows:
                df_chart = pd.concat([df_chart, pd.DataFrame(target_rows)], ignore_index=True)

            if not df_chart.empty:
                fig = px.bar(
                    df_chart, x='METRIC', y='Actual', color='COMPETITOR', barmode='group',
                    color_discrete_map={'Rappi': '#FF4646', 'Uber Eats': '#000000', 'DiDi Food': '#F56C27', '🎯 Target Esperado (Rappi)': '#2ecc71'},
                    height=450, text_auto='.2f'
                )
                fig.update_layout(yaxis_title="Valor / Porcentaje")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos para graficar.")
        
        with col_info:
            st.markdown("### Estrategia Competitiva Core")
            st.write(f"Comparación de mercado en **{zona_sel}** (Semana Actual).")
            st.info("🎯 **Target Visual:** La barra verde en la gráfica representa exactamente dónde debería estar posicionada la oferta de Rappi para lograr el objetivo competitivo del -10%.")

    with tab2:
        st.subheader(f"Estrategia Focalizada: {zona_sel}")
        
        metricas_tendencia = sorted(df_master['METRIC'].unique().tolist())
        
        if metricas_tendencia:
            m_sel = st.selectbox("Seleccionar Métrica a Analizar:", metricas_tendencia)
            
            # 1. INTELIGENCIA DE MÉTRICA
            higher_is_better = any(kw in m_sel.lower() for kw in ['score', 'cvr', 'profit', 'penetration', 'adoption', 'perfect', 'orders', 'descuento', 'promo'])
            
            df_det = df_zona[df_zona['METRIC'] == m_sel].groupby('COMPETITOR')[columnas_historicas].mean().reset_index()
            
            # 2. CÁLCULO DE TARGET DINÁMICO E HISTÓRICO
            target_trend_data = {'COMPETITOR': '🎯 Target Esperado (Rappi)'}
            for semana in columnas_historicas:
                datos_comp_semana = df_det[df_det['COMPETITOR'] != 'Rappi'][semana]
                if higher_is_better:
                    val_best = datos_comp_semana.max()
                    target_trend_data[semana] = val_best * 1.10 if pd.notna(val_best) and val_best > 0 else np.nan
                else:
                    val_best = datos_comp_semana.min()
                    target_trend_data[semana] = val_best * 0.90 if pd.notna(val_best) and val_best > 0 else np.nan
            
            df_det = pd.concat([df_det, pd.DataFrame([target_trend_data])], ignore_index=True)
            
            # 3. EXTRACCIÓN DE DATOS REALES PARA LA ESTRATEGIA (TERCIOS)
            df_comps = df_det[(df_det['COMPETITOR'] != 'Rappi') & (df_det['COMPETITOR'] != '🎯 Target Esperado (Rappi)')]
            val_rappi_real = df_det[df_det['COMPETITOR'] == 'Rappi']['Actual'].mean()
            
            st.markdown("##### 💡 Recomendación Estratégica Segmentada")
            if not df_comps.empty and df_comps['Actual'].notna().any():
                mejor_idx = df_comps['Actual'].idxmax() if higher_is_better else df_comps['Actual'].idxmin()
                mejor_nombre = df_comps.loc[mejor_idx, 'COMPETITOR']
                mejor_valor = df_comps.loc[mejor_idx, 'Actual']
                
                # Tácticas específicas según métrica
                if 'cvr' in m_sel.lower():
                    tactica = "optimizar UI/UX, fotos del menú y flash promos"
                elif 'score' in m_sel.lower() or 'perfect' in m_sel.lower() or 'satisfaction' in m_sel.lower():
                    tactica = "auditar tiempos de preparación y soporte al cliente"
                elif 'fee' in m_sel.lower() or 'price' in m_sel.lower():
                    tactica = "ajustar dinámicamente precios y subsidios"
                elif 'time' in m_sel.lower() or 'eta' in m_sel.lower():
                    tactica = "aumentar densidad de flota y algoritmo de asignación"
                else:
                    tactica = "alinear esfuerzos de marketing e inversión hiperlocal"

                # LÓGICA DE TERCIOS (Segmentación por cercanía al competidor líder)
                if pd.isna(val_rappi_real):
                    st.markdown(f"""
                    <div class='strategic-box' style='border-left-color: #7f8c8d;'>
                        <div class='strat-title'>🔍 <strong>Ataque a Mercado Ciego</strong></div>
                        Rappi no tiene datos reportados para esta métrica. La referencia a batir es <b>{mejor_nombre}</b> ({round(mejor_valor, 4)}). Iniciar medición operativa de inmediato.
                    </div>""", unsafe_allow_html=True)
                else:
                    # Calcular porcentaje de brecha absoluta
                    brecha_pct = abs(val_rappi_real - mejor_valor) / mejor_valor if mejor_valor > 0 else 0
                    is_winning = (higher_is_better and val_rappi_real >= mejor_valor) or (not higher_is_better and val_rappi_real <= mejor_valor)

                    if is_winning or brecha_pct <= 0.05:
                        # Tercio Superior (Ganando o a menos de 5% de distancia)
                        st.markdown(f"""
                        <div class='strategic-box' style='border-left-color: #27ae60; background-color: #f1fdf6;'>
                            <div class='strat-title'>🏆 <strong>Tercio Superior (Alta Competitividad)</strong></div>
                            Rappi ({round(val_rappi_real, 4)}) lidera o está muy cerca de alcanzar a los competidores (Líder {mejor_nombre}: {round(mejor_valor, 4)}).<br><br>
                            <b>Recomendación:</b> Ir aquí con prioridad para asegurar y expandir el dominio en esta métrica.
                        </div>""", unsafe_allow_html=True)
                    elif brecha_pct <= 0.15:
                        # Tercio Medio (Entre 5% y 15% de distancia)
                        st.markdown(f"""
                        <div class='strategic-box' style='border-left-color: #f39c12; background-color: #fffaf0;'>
                            <div class='strat-title'>⚖️ <strong>Tercio Medio (Competitividad Estable)</strong></div>
                            Rappi ({round(val_rappi_real, 4)}) se encuentra a una distancia moderada del líder ({mejor_nombre}: {round(mejor_valor, 4)}).<br><br>
                            <b>Recomendación:</b> Debemos mantener las acciones de acuerdo al plan establecido para cerrar la brecha gradualmente.
                        </div>""", unsafe_allow_html=True)
                    else:
                        # Tercio Inferior (A más del 15% de distancia)
                        st.markdown(f"""
                        <div class='strategic-box' style='border-left-color: #e74c3c; background-color: #fdf3f2;'>
                            <div class='strat-title'>🚨 <strong>Tercio Inferior (Rezago Competitivo)</strong></div>
                            Rappi ({round(val_rappi_real, 4)}) presenta una brecha significativa frente a la competencia ({mejor_nombre}: {round(mejor_valor, 4)}).<br><br>
                            <b>Recomendación:</b> Tomar acción rápida porque los competidores se están volviendo muy fuertes en este espacio. Revisar tácticas como {tactica}.
                        </div>""", unsafe_allow_html=True)

            # 4. RENDERIZADO VISUAL
            col_tabla, col_grafico = st.columns([1, 2])
            
            with col_tabla:
                st.markdown("##### Valor Actual (Consolidado)")
                df_tabla_display = df_det[['COMPETITOR', 'Actual']].copy()
                df_tabla_display['Actual'] = df_tabla_display['Actual'].round(4)
                st.table(df_tabla_display.set_index('COMPETITOR'))
                
            with col_grafico:
                st.markdown("##### 📈 Evolución Histórica (Últimas 8 Semanas)")
                orden_tiempo = columnas_historicas[::-1]
                df_trend = df_det.melt(
                    id_vars=['COMPETITOR'], value_vars=orden_tiempo, var_name='Semana', value_name='Valor'
                )
                
                fig_trend = px.line(
                    df_trend, x='Semana', y='Valor', color='COMPETITOR', markers=True,
                    color_discrete_map={'Rappi': '#FF4646', 'Uber Eats': '#000000', 'DiDi Food': '#F56C27', '🎯 Target Esperado (Rappi)': '#2ecc71'}
                )
                
                fig_trend.update_traces(patch={"line": {"dash": "dash"}}, selector={"name": "🎯 Target Esperado (Rappi)"})
                fig_trend.update_layout(yaxis_title=m_sel, xaxis_title="Eje de Tiempo", height=400)
                st.plotly_chart(fig_trend, use_container_width=True)
            
        else:
            st.warning("No hay métricas disponibles para esta zona.")

    st.divider()
    st.caption("Rappi Data Collection Plan Dashboard | Motor analítico focalizado por métrica y terciles.")

else:
    st.error("No se pudieron cargar los datos.")
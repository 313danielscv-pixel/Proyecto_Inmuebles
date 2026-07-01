from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Proyecto Inmuebles Global",
    page_icon="🏠",
    layout="wide",
)

ROOT_DIR = Path(__file__).resolve().parent
DATA_FILE = ROOT_DIR / "proyecto-inmobiliario-global" / "streamlit_data" / "base_rentable.csv"

DEFAULT_MAX_PRICE = 120000.0
DEFAULT_MIN_RENT = 1000.0
DEFAULT_MAX_PAYBACK = 20.0
DEFAULT_TARGET_ENTRY = 30000.0
DEFAULT_ENTRY_CAP = 80000.0


@st.cache_data(show_spinner=False)
def load_base() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE)


def parse_currency(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace("€", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace(" ", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def minmax(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce")
    valid = series.dropna()
    if valid.empty or valid.nunique() <= 1:
        return pd.Series(0.0, index=series.index)
    lo, hi = valid.min(), valid.max()
    return (series - lo) / (hi - lo)


def build_workframe(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()

    if "price_eur_num" not in work.columns:
        if "price_in_Euro_calculo" in work.columns:
            work["price_eur_num"] = pd.to_numeric(work["price_in_Euro_calculo"], errors="coerce")
        else:
            work["price_eur_num"] = parse_currency(work["price_in_Euro"])

    if "entry_eur_num" not in work.columns:
        work["entry_eur_num"] = parse_currency(work.get("entry_price_eur", pd.Series(index=work.index, dtype="object")))

    if "rent_eur_month_num" not in work.columns:
        work["rent_eur_month_num"] = parse_currency(work.get("zone_rental_price", pd.Series(index=work.index, dtype="object")))

    work["price_eur_num"] = pd.to_numeric(work["price_eur_num"], errors="coerce")
    work["entry_eur_num"] = pd.to_numeric(work["entry_eur_num"], errors="coerce")
    work["rent_eur_month_num"] = pd.to_numeric(work["rent_eur_month_num"], errors="coerce")

    work["payback_years"] = work["price_eur_num"] / (work["rent_eur_month_num"] * 12.0)

    work["score_price"] = 1.0 - (work["price_eur_num"] / DEFAULT_MAX_PRICE)
    work["score_price"] = work["score_price"].clip(lower=0.0, upper=1.0)

    work["score_entry"] = 1.0 - (work["entry_eur_num"] / DEFAULT_ENTRY_CAP)
    work["score_entry"] = work["score_entry"].clip(lower=0.0, upper=1.0)

    work["score_affordability"] = (0.6 * work["score_price"] + 0.4 * work["score_entry"])

    riesgo_map = {"bajo": 1.0, "medio": 0.55, "alto": 0.0}
    work["riesgo_norm"] = (
        work.get("riesgo_ocupacion", pd.Series(index=work.index, dtype="object"))
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .map(riesgo_map)
    )
    work["riesgo_norm"] = work["riesgo_norm"].fillna(0.5)

    work["safety_num"] = pd.to_numeric(work.get("safety_num", work.get("safety_index")), errors="coerce")
    if work["safety_num"].isna().all():
        work["safety_num"] = 50.0
    work["score_safety"] = minmax(work["safety_num"])

    work["crime_num"] = pd.to_numeric(work.get("crime_num", work.get("crime_index")), errors="coerce")
    if work["crime_num"].isna().all():
        work["crime_num"] = 50.0
    work["score_crime"] = 1.0 - minmax(work["crime_num"])

    rent_score = minmax(work["rent_eur_month_num"])
    work["score_oportunidad"] = 100.0 * (
        0.35 * rent_score
        + 0.30 * work["score_affordability"]
        + 0.20 * work["riesgo_norm"]
        + 0.10 * work["score_safety"]
        + 0.05 * work["score_crime"]
    )

    return work


def get_top20(df: pd.DataFrame, max_price: float, min_rent: float, max_payback: float) -> pd.DataFrame:
    base = df.copy()
    base = base[
        base["price_eur_num"].notna()
        & base["entry_eur_num"].notna()
        & base["rent_eur_month_num"].notna()
        & base["latitude"].notna()
        & base["longitude"].notna()
        & (base["rent_eur_month_num"] >= min_rent)
        & (base["price_eur_num"] <= max_price)
        & (base["payback_years"] <= max_payback)
        & (base["country"].fillna("") != "UAE")
    ].copy()

    top_por_pais = (
        base.sort_values(["country", "score_oportunidad"], ascending=[True, False])
        .drop_duplicates("country", keep="first")
        .sort_values("score_oportunidad", ascending=False)
    )

    espana = top_por_pais[top_por_pais["country"] == "Spain"].head(1)
    otros = top_por_pais[top_por_pais["country"] != "Spain"].copy()

    if len(espana) == 1:
        top_2 = otros.head(2)
        rest = otros.iloc[2:].head(17)
        top20 = pd.concat([top_2, espana, rest], ignore_index=True).head(20)
    else:
        top20 = otros.head(20).reset_index(drop=True)

    top20 = top20.reset_index(drop=True)
    top20["rank_final"] = np.arange(1, len(top20) + 1)
    return top20


def render_formula_summary(max_price: float, min_rent: float, max_payback: float) -> None:
    st.markdown("### Como se calcula el score")
    st.markdown(
        f"""
- Filtro de negocio: `precio <= EUR {max_price:,.0f}`, `renta >= EUR {min_rent:,.0f}/mes`, `payback <= {max_payback:.0f} anios`
- `score_affordability = 0.6 * score_price + 0.4 * score_entry`
- `score_price = 1 - (price / {DEFAULT_MAX_PRICE:,.0f})`
- `score_entry = 1 - (entry / {DEFAULT_ENTRY_CAP:,.0f})`
- `score_oportunidad = 100 * (0.35 * score_renta + 0.30 * score_affordability + 0.20 * riesgo_norm + 0.10 * seguridad + 0.05 * crimen)`
"""
    )


def render_property_result(title: str, row_data: dict) -> None:
    row = pd.Series(row_data)
    st.markdown(f"### {title}")
    st.success(f"Pais seleccionado: {row.get('country', 'N/A')}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Precio", row.get("price_in_Euro", "N/A"))
    c2.metric("Entrada", row.get("entry_price_eur", "N/A"))
    c3.metric("Renta mensual", row.get("zone_rental_price", "N/A"))

    c4, c5, c6 = st.columns(3)
    c4.metric("Score total", f"{float(row.get('score_oportunidad', 0.0)):.2f}")
    c5.metric("Payback", f"{float(row.get('payback_years', 0.0)):.1f} anios")
    c6.metric("Accesibilidad", f"{float(row.get('score_affordability', 0.0)):.2f}")

    st.markdown(
        f"""
**Ubicacion:** {row.get('location', 'N/A')}  
**Score precio:** {float(row.get('score_price', 0.0)):.2f}  
**Score entrada:** {float(row.get('score_entry', 0.0)):.2f}  
**Score accesibilidad:** {float(row.get('score_affordability', 0.0)):.2f}  
**Seguridad:** {float(row.get('score_safety', 0.0)):.2f}  
**Crimen:** {float(row.get('score_crime', 0.0)):.2f}  
**Riesgo ocupacion:** {float(row.get('riesgo_norm', 0.0)):.2f}
"""
    )

    if pd.notna(row.get("leyes_de_ocupacion_comentario")):
        st.markdown(f"**Ley / comentario:** {row.get('leyes_de_ocupacion_comentario')}")
    if pd.notna(row.get("leyes_de_ocupacion_url")):
        st.markdown(f"[Fuente legal]({row.get('leyes_de_ocupacion_url')})")
    if pd.notna(row.get("url")):
        st.markdown(f"[Abrir inmueble]({row.get('url')})")


def get_best_row_for_country(top20: pd.DataFrame, country: str) -> dict | None:
    matches = top20[top20["country"] == country]
    if matches.empty:
        return None
    return matches.sort_values("score_oportunidad", ascending=False).iloc[0].to_dict()


def get_best_row_from_filters(work: pd.DataFrame, max_price: float, min_rent: float, max_payback: float) -> dict | None:
    filtered = work[
        work["price_eur_num"].notna()
        & work["entry_eur_num"].notna()
        & work["rent_eur_month_num"].notna()
        & work["latitude"].notna()
        & work["longitude"].notna()
        & (work["rent_eur_month_num"] >= min_rent)
        & (work["price_eur_num"] <= max_price)
        & (work["payback_years"] <= max_payback)
        & (work["country"].fillna("") != "UAE")
    ].copy()
    if filtered.empty:
        return None
    return filtered.sort_values("score_oportunidad", ascending=False).head(1).iloc[0].to_dict()


def page_1(top20: pd.DataFrame, base: pd.DataFrame) -> None:
    st.subheader("Pagina 1: Mapa, grafica y tabla")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Paises Top20", int(top20["country"].nunique()))
    c2.metric("Score medio", f"{top20['score_oportunidad'].mean():.2f}")
    c3.metric("Precio medio", f"EUR {top20['price_eur_num'].mean():,.0f}")
    c4.metric("Renta media", f"EUR {top20['rent_eur_month_num'].mean():,.0f}/mes")

    render_formula_summary(float(st.session_state.max_price), float(st.session_state.min_rent), float(st.session_state.max_payback))

    col_map, col_bar = st.columns([1.5, 1.0])
    with col_map:
        st.markdown("### Mapa de ubicaciones")
        map_fig = px.scatter_geo(
            top20,
            lat="latitude",
            lon="longitude",
            color="score_oportunidad",
            size="rent_eur_month_num",
            hover_name="country",
            hover_data={
                "location": True,
                "price_in_Euro": True,
                "entry_price_eur": True,
                "zone_rental_price": True,
                "leyes_de_ocupacion_comentario": True,
                "rank_final": True,
            },
            color_continuous_scale="Viridis",
            projection="natural earth",
            height=540,
        )
        map_fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(map_fig, width="stretch")

    with col_bar:
        st.markdown("### Score medio por pais")
        chart_top = (
            base.groupby("country", as_index=False)
            .agg(
                inmuebles=("country", "size"),
                score_medio=("score_oportunidad", "mean"),
                renta_media=("rent_eur_month_num", "mean"),
                payback_medio=("payback_years", "mean"),
            )
            .sort_values("score_medio", ascending=False)
            .head(15)
        )
        bar_fig = px.bar(
            chart_top,
            x="country",
            y="score_medio",
            hover_data=["inmuebles", "renta_media", "payback_medio"],
            color="score_medio",
            color_continuous_scale="Blues",
            height=540,
        )
        bar_fig.update_layout(xaxis_tickangle=-45, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(bar_fig, width="stretch")

    st.markdown("### Tabla Top 20")
    table_cols = [
        "rank_final",
        "country",
        "location",
        "price_in_Euro",
        "entry_price_eur",
        "zone_rental_price",
        "leyes_de_ocupacion_comentario",
        "leyes_de_ocupacion_url",
        "score_oportunidad",
        "payback_years",
        "url",
    ]

    table_event = st.dataframe(
        top20[table_cols].sort_values("rank_final").reset_index(drop=True),
        width="stretch",
        hide_index=True,
        key="top20_table",
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "url": st.column_config.LinkColumn("Enlace inmueble"),
            "leyes_de_ocupacion_url": st.column_config.LinkColumn("Ley / fuente"),
            "score_oportunidad": st.column_config.NumberColumn("score_oportunidad", format="%.2f"),
            "payback_years": st.column_config.NumberColumn("payback_years", format="%.1f"),
        },
    )

    if table_event.selection.rows:
        selected_row = top20[table_cols].sort_values("rank_final").reset_index(drop=True).iloc[table_event.selection.rows[0]].to_dict()
        st.session_state.selected_table_result = selected_row

    if "selected_table_result" in st.session_state:
        st.markdown("### Resultado del pais clicado en la tabla")
        render_property_result("Mejor resultado de la tabla", st.session_state.selected_table_result)

    with st.expander("Resumen base filtrada"):
        st.write(f"Registros elegibles: {len(base):,}")
        st.write(f"Paises elegibles: {base['country'].nunique()}")
        st.write(f"Max precio: EUR {st.session_state.max_price:,.0f}")
        st.write(f"Min renta: EUR {st.session_state.min_rent:,.0f}/mes")
        st.write(f"Max payback: {st.session_state.max_payback:.0f} anios")


def page_2(top20: pd.DataFrame) -> None:
    st.subheader("Pagina 2: Ruleta y resultado")

    col_ruleta, col_info = st.columns([1.1, 1.0])

    with col_ruleta:
        st.markdown("### Ruleta de oportunidad")
        wheel = top20[["rank_final", "country", "score_oportunidad"]].copy()
        wheel["peso_ruleta"] = wheel["score_oportunidad"] / wheel["score_oportunidad"].sum()
        wheel["porcentaje_ruleta"] = (wheel["peso_ruleta"] * 100).round(2)

        pie_fig = px.pie(
            wheel,
            names="country",
            values="porcentaje_ruleta",
            hole=0.45,
            height=560,
        )
        pie_fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(pie_fig, width="stretch")

        if st.button("Girar ruleta"):
            winner_country = np.random.choice(wheel["country"], p=wheel["peso_ruleta"])
            winner_row = top20[top20["country"] == winner_country].iloc[0]
            st.session_state.winner_country = winner_country
            st.session_state.winner_row = winner_row.to_dict()

        if st.button("Buscar mejor con estos filtros"):
            best_filtered = get_best_row_from_filters(
                work=build_workframe(load_base()),
                max_price=float(st.session_state.max_price),
                min_rent=float(st.session_state.min_rent),
                max_payback=float(st.session_state.max_payback),
            )
            if best_filtered is None:
                st.warning("No hay resultados con esos filtros.")
            else:
                st.session_state.filtered_row = best_filtered

    with col_info:
        st.markdown("### Resultado ejecutivo")
        if "winner_row" in st.session_state:
            render_property_result("Resultado de la ruleta", st.session_state.winner_row)
        else:
            st.info("Pulsa 'Girar ruleta' para ver un pais ganador y su inmueble principal.")

        if "selected_table_result" in st.session_state:
            st.markdown("---")
            render_property_result("Resultado del pais clicado", st.session_state.selected_table_result)

        if "filtered_row" in st.session_state:
            st.markdown("---")
            render_property_result("Mejor resultado con los filtros", st.session_state.filtered_row)

        st.markdown("### Tabla de probabilidades")
        wheel_view = wheel[["rank_final", "country", "porcentaje_ruleta"]].sort_values("rank_final")
        st.dataframe(
            wheel_view,
            width="stretch",
            hide_index=True,
            column_config={
                "porcentaje_ruleta": st.column_config.NumberColumn("porcentaje_ruleta", format="%.2f"),
            },
        )


def main() -> None:
    st.title("Dashboard Inmobiliario Global")
    st.caption("Version Streamlit unificada, sin Power BI")

    if not DATA_FILE.exists():
        st.error(f"No existe el archivo base: {DATA_FILE}")
        st.stop()

    if "max_price" not in st.session_state:
        st.session_state.max_price = DEFAULT_MAX_PRICE
    if "min_rent" not in st.session_state:
        st.session_state.min_rent = DEFAULT_MIN_RENT
    if "max_payback" not in st.session_state:
        st.session_state.max_payback = DEFAULT_MAX_PAYBACK

    with st.sidebar:
        st.header("Filtros")
        st.session_state.max_price = st.slider(
            "Precio maximo del inmueble",
            min_value=20000.0,
            max_value=400000.0,
            value=float(st.session_state.max_price),
            step=5000.0,
            format="EUR %.0f",
        )
        st.session_state.min_rent = st.slider(
            "Renta minima mensual",
            min_value=500.0,
            max_value=5000.0,
            value=float(st.session_state.min_rent),
            step=50.0,
            format="EUR %.0f",
        )
        st.session_state.max_payback = st.slider(
            "Payback maximo",
            min_value=5.0,
            max_value=30.0,
            value=float(st.session_state.max_payback),
            step=1.0,
            format="%.0f anios",
        )
        st.markdown("---")
        st.markdown("**Criterio clave**: prioriza precios cercanos a 30k-60k, renta alta y riesgo bajo.")

    df = load_base()
    work = build_workframe(df)

    top20 = get_top20(work, st.session_state.max_price, st.session_state.min_rent, st.session_state.max_payback)

    page = st.radio("Selecciona pagina", ["Pagina 1", "Pagina 2"], horizontal=True)

    if page == "Pagina 1":
        page_1(top20, work)
    else:
        page_2(top20)


if __name__ == "__main__":
    main()

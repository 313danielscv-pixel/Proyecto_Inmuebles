from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Proyecto Inmuebles Global",
    page_icon="🏠",
    layout="wide",
)

ROOT_DIR = Path(__file__).resolve().parent
DATA_FILE = ROOT_DIR / "proyecto-inmobiliario-global" / "streamlit_data" / "base_rentable.csv"
PRECOMPUTED_TOP20_FILE = ROOT_DIR / "proyecto-inmobiliario-global" / "streamlit_data" / "top20_paises_verificables.csv"

DEFAULT_MAX_PRICE = 120000.0
DEFAULT_MIN_RENT = 1000.0
DEFAULT_MAX_PAYBACK = 20.0
DEFAULT_TARGET_ENTRY = 30000.0
DEFAULT_TARGET_PRICE = 30000.0
DEFAULT_TARGET_RENT = 1200.0
DEFAULT_ENTRY_CAP = 80000.0
MIN_TOP20_COUNTRIES = 13


@st.cache_data(show_spinner=False)
def load_base() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE)


@st.cache_data(show_spinner=False)
def load_precomputed_top20() -> pd.DataFrame:
    if not PRECOMPUTED_TOP20_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(PRECOMPUTED_TOP20_FILE)


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


@st.cache_data(show_spinner=False, ttl=60 * 60 * 6)
def is_listing_url_active(url: str) -> bool:
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return False

    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
    )

    try:
        with urlopen(request, timeout=5) as response:
            status_code = getattr(response, "status", 200)
            if status_code >= 400:
                return False
            # Read enough body to capture status badges that are often placed deeper in the page.
            content = response.read(300000).decode("utf-8", errors="ignore").lower()
    except (HTTPError, URLError, TimeoutError):
        return False
    except Exception:
        return False

    inactive_pattern = (
        r"sold|sold\s+or\s+out\s+of\s+date|out\s*of\s*date|outdated|archive\s*cost|"
        r"listing\s+no\s+longer\s+available|"
        r"property\s+no\s+longer\s+available|not\s*found|404|archived|unavailable|"
        r"no\s+longer\s+on\s+the\s+market|vendido|vendida|reservado|reserved"
    )
    return re.search(inactive_pattern, content) is None


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

    listing_text = (
        work.get("location", pd.Series(index=work.index, dtype="object")).fillna("").astype(str).str.lower()
        + " "
        + work.get("url", pd.Series(index=work.index, dtype="object")).fillna("").astype(str).str.lower()
        + " "
        + work.get("image", pd.Series(index=work.index, dtype="object")).fillna("").astype(str).str.lower()
    )
    sold_pattern = r"\bsold\b|\bvendido\b|\bvendida\b|\breservado\b|\breserved\b"
    inactive_pattern = r"not\s*found|404|unavailable|off[- ]?market|no\s*found"
    work["is_sold"] = listing_text.str.contains(sold_pattern, regex=True, na=False)
    work["is_inactive_hint"] = listing_text.str.contains(inactive_pattern, regex=True, na=False)
    work["has_valid_url"] = work.get("url", pd.Series(index=work.index, dtype="object")).fillna("").astype(str).str.contains(r"^https?://", regex=True)
    work = work[(~work["is_sold"]) & (~work["is_inactive_hint"]) & work["has_valid_url"]].copy()

    work["payback_years"] = work["price_eur_num"] / (work["rent_eur_month_num"] * 12.0)
    work["annual_yield"] = (work["rent_eur_month_num"] * 12.0) / work["price_eur_num"]

    # Remove improbable rent/price outliers.
    # NOTE: zone_rental_price can represent market zone prices (not actual property yield),
    # so the upper limit is kept generous (5.0 = 500%) to avoid discarding valid precomputed entries.
    work = work[
        work["annual_yield"].notna()
        & (work["annual_yield"] >= 0.01)
        & (work["annual_yield"] <= 5.0)
        & (work["rent_eur_month_num"] <= 10000)
    ].copy()

    work["score_price"] = 1.0 - (work["price_eur_num"] / DEFAULT_MAX_PRICE)
    work["score_price"] = work["score_price"].clip(lower=0.0, upper=1.0)

    work["score_entry"] = 1.0 - (work["entry_eur_num"] / DEFAULT_ENTRY_CAP)
    work["score_entry"] = work["score_entry"].clip(lower=0.0, upper=1.0)

    work["score_affordability"] = (0.6 * work["score_price"] + 0.4 * work["score_entry"])

    # Proximity scores to business targets: total price around 30k and monthly rent around 1200.
    work["score_target_price"] = (1.0 - (work["price_eur_num"] - DEFAULT_TARGET_PRICE).abs() / DEFAULT_TARGET_PRICE).clip(0.0, 1.0)
    work["score_target_rent"] = (1.0 - (work["rent_eur_month_num"] - DEFAULT_TARGET_RENT).abs() / DEFAULT_TARGET_RENT).clip(0.0, 1.0)
    work["score_target_profile"] = (0.60 * work["score_target_price"] + 0.40 * work["score_target_rent"])

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

    work["score_yield"] = minmax(work["annual_yield"])
    work["score_payback"] = 1.0 - minmax(work["payback_years"])

    work["location_text"] = (
        work.get("location", pd.Series(index=work.index, dtype="object")).fillna("").astype(str).str.lower()
    )
    urban_pattern = r"city|center|centre|downtown|urban|capital|madrid|barcelona|valencia|lisbon|porto|athens|istanbul"
    beach_pattern = r"beach|coast|coastal|sea|seaside|marina|playa|costa"
    rural_pattern = r"campo|country\s?house|farm|rural|village|finca"

    work["is_urban"] = work["location_text"].str.contains(urban_pattern, regex=True, na=False)
    work["is_beach"] = work["location_text"].str.contains(beach_pattern, regex=True, na=False)
    work["is_rural"] = work["location_text"].str.contains(rural_pattern, regex=True, na=False)

    work["score_urban"] = np.where(work["is_urban"], 1.0, 0.35)
    work["score_beach"] = np.where(work["is_beach"], 1.0, 0.25)
    work["rural_penalty"] = np.where(work["is_rural"], 0.70, 0.0)
    work["score_location"] = (0.70 * work["score_urban"] + 0.30 * work["score_beach"] - work["rural_penalty"]).clip(0.0, 1.0)

    work["has_legal_comment"] = work.get("leyes_de_ocupacion_comentario", pd.Series(index=work.index, dtype="object")).notna().astype(float)
    work["has_legal_url"] = work.get("leyes_de_ocupacion_url", pd.Series(index=work.index, dtype="object")).notna().astype(float)
    work["score_legal"] = (0.75 * work["riesgo_norm"] + 0.15 * work["has_legal_comment"] + 0.10 * work["has_legal_url"]).clip(0.0, 1.0)
    work["score_legal_pct"] = work["score_legal"] * 100.0

    work["score_rent"] = minmax(work["rent_eur_month_num"])

    work["score_raw"] = (
        0.13 * work["score_yield"]
        + 0.10 * work["score_payback"]
        + 0.11 * work["score_affordability"]
        + 0.08 * work["score_rent"]
        + 0.18 * work["score_legal"]
        + 0.11 * work["score_location"]
        + 0.28 * work["score_target_profile"]
        + 0.01 * work["score_safety"]
        + 0.01 * work["score_crime"]
    )
    work["score_oportunidad"] = 100.0 * minmax(work["score_raw"])

    return work


def get_top20(
    df: pd.DataFrame,
    max_price: float,
    min_rent: float,
    max_payback: float,
    validate_live_urls: bool = False,
) -> pd.DataFrame:
    strict_base = df.copy()
    strict_base = strict_base[
        strict_base["price_eur_num"].notna()
        & strict_base["entry_eur_num"].notna()
        & strict_base["rent_eur_month_num"].notna()
        & strict_base["latitude"].notna()
        & strict_base["longitude"].notna()
        & (strict_base["rent_eur_month_num"] >= min_rent)
        & (strict_base["price_eur_num"] <= max_price)
        & (strict_base["payback_years"] <= max_payback)
        & (strict_base["score_location"] >= 0.35)
        & (strict_base["price_eur_num"] >= 18000)
        & (strict_base["price_eur_num"] <= 45000)
        & (strict_base["rent_eur_month_num"] >= 900)
        & (strict_base["rent_eur_month_num"] <= 1700)
        & (strict_base["country"].fillna("") != "UAE")
    ].copy()

    relaxed_base = df.copy()
    relaxed_base = relaxed_base[
        relaxed_base["price_eur_num"].notna()
        & relaxed_base["entry_eur_num"].notna()
        & relaxed_base["rent_eur_month_num"].notna()
        & relaxed_base["latitude"].notna()
        & relaxed_base["longitude"].notna()
        & (relaxed_base["rent_eur_month_num"] >= min_rent)
        & (relaxed_base["price_eur_num"] <= max_price)
        & (relaxed_base["score_location"] >= 0.20)
        & (relaxed_base["price_eur_num"] >= 15000)
        & (relaxed_base["price_eur_num"] <= 65000)
        & (relaxed_base["rent_eur_month_num"] <= 2200)
        & (relaxed_base["country"].fillna("") != "UAE")
    ].copy()

    fallback_base = df.copy()
    fallback_base = fallback_base[
        fallback_base["price_eur_num"].notna()
        & fallback_base["entry_eur_num"].notna()
        & fallback_base["rent_eur_month_num"].notna()
        & fallback_base["latitude"].notna()
        & fallback_base["longitude"].notna()
        & (fallback_base["rent_eur_month_num"] >= min_rent)
        & (fallback_base["price_eur_num"] <= max_price)
        & (fallback_base["country"].fillna("") != "UAE")
    ].copy()

    fallback_price = df.copy()
    fallback_price = fallback_price[
        fallback_price["price_eur_num"].notna()
        & fallback_price["entry_eur_num"].notna()
        & fallback_price["rent_eur_month_num"].notna()
        & fallback_price["latitude"].notna()
        & fallback_price["longitude"].notna()
        & (fallback_price["price_eur_num"] <= max_price)
        & (fallback_price["country"].fillna("") != "UAE")
    ].copy()

    fallback_geo = df.copy()
    fallback_geo = fallback_geo[
        fallback_geo["latitude"].notna()
        & fallback_geo["longitude"].notna()
        & (fallback_geo["country"].fillna("") != "UAE")
    ].copy()

    ranking_pool = pd.concat([strict_base, relaxed_base, fallback_base, fallback_price, fallback_geo], ignore_index=True)
    ranking_pool = ranking_pool.drop_duplicates(subset=["url", "location", "country"]).copy()
    ranking_pool = ranking_pool.sort_values(
        ["score_target_profile", "score_oportunidad", "score_legal", "score_location"],
        ascending=[False, False, False, False],
    )

    selected_rows = []
    country_counts: dict[str, int] = {}
    max_per_country = 3

    for _, row in ranking_pool.iterrows():
        country = str(row.get("country", "")).strip()
        if not country:
            continue

        if country_counts.get(country, 0) >= max_per_country:
            continue

        if validate_live_urls and (not is_listing_url_active(str(row.get("url", "")))):
            continue

        selected_rows.append(row)
        country_counts[country] = country_counts.get(country, 0) + 1

        if len(selected_rows) >= MIN_TOP20_COUNTRIES:
            break

    top20 = pd.DataFrame(selected_rows)
    if top20.empty:
        top20 = ranking_pool.head(MIN_TOP20_COUNTRIES).copy()
    else:
        top20 = top20.head(MIN_TOP20_COUNTRIES).copy()

    top20 = top20.reset_index(drop=True)
    top20["rank_final"] = np.arange(1, len(top20) + 1)
    return top20


def get_top20_from_precomputed(work: pd.DataFrame) -> pd.DataFrame:
    pre = load_precomputed_top20()
    if pre.empty or ("url" not in pre.columns):
        return pd.DataFrame()

    pre = pre.dropna(subset=["url"]).copy()
    pre["url"] = pre["url"].astype(str).str.strip()
    pre = pre[pre["url"] != ""].drop_duplicates(subset=["url"]).copy()
    if pre.empty:
        return pd.DataFrame()

    # Strategy 1: enrich with already-computed work scores (inner merge).
    work_by_url = work.drop_duplicates(subset=["url"]).copy()
    top20 = pre[["url"]].merge(work_by_url, on="url", how="inner")

    # Strategy 2 (fallback): build scores directly on the precomputed raw data.
    # This handles the case where yield-filter in build_workframe removed zone-price entries.
    if top20.empty or len(top20) < len(pre) * 0.5:
        top20_direct = build_workframe(pre.copy())
        if len(top20_direct) >= len(top20):
            top20 = top20_direct

    if top20.empty:
        return pd.DataFrame()

    # Restore notebook ranking order if available.
    if "rank_top20" in pre.columns:
        order = pre[["url", "rank_top20"]].rename(columns={"rank_top20": "_nb_rank"})
        top20 = order.merge(top20.drop(columns=["_nb_rank"], errors="ignore"), on="url", how="inner")
        top20 = top20.sort_values("_nb_rank").drop(columns=["_nb_rank"])

    top20 = top20.head(MIN_TOP20_COUNTRIES).reset_index(drop=True)
    top20["rank_final"] = np.arange(1, len(top20) + 1)
    return top20


def render_formula_summary(max_price: float, min_rent: float, max_payback: float) -> None:
    st.markdown("### Como se calcula el score")
    st.markdown(
        f"""
- Filtro de negocio: `precio <= EUR {max_price:,.0f}`, `renta >= EUR {min_rent:,.0f}/mes`, `payback <= {max_payback:.0f} anios`
- Limpieza previa: se excluyen anuncios vendidos/reservados, anuncios inactivos y URLs no validas.
- Variables de tabla usadas: `location`, `price_in_Euro`, `entry_price_eur`, `zone_rental_price`, `leyes_de_ocupacion_comentario`, `leyes_de_ocupacion_url`, `payback_years`
- `annual_yield = (renta mensual * 12) / precio`
- `score_price = 1 - (price / {DEFAULT_MAX_PRICE:,.0f})`
- `score_entry = 1 - (entry / {DEFAULT_ENTRY_CAP:,.0f})`
- `score_affordability = 0.6 * score_price + 0.4 * score_entry`
- `score_target_profile = 0.60 * cercania(precio_total, 30k) + 0.40 * cercania(renta, 1200)`
- `score_legal_% = 100 * (0.75 * riesgo + 0.15 * comentario_legal + 0.10 * fuente_legal)`
- `score_location = 0.70 * urbano + 0.30 * playa - penalizacion_rural`
- `score_raw = 0.13*yield + 0.10*payback + 0.11*affordability + 0.08*renta + 0.18*legal + 0.11*ubicacion + 0.28*objetivo_30k_1200`
- `score_oportunidad = 100 * minmax(score_raw)`  (mejor inmueble del universo = 100)
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
    c6.metric("Score legal", f"{float(row.get('score_legal_pct', 0.0)):.0f}%")

    st.markdown(
        f"""
**Ubicacion:** {row.get('location', 'N/A')}  
**Score precio:** {float(row.get('score_price', 0.0)) * 100:.0f}%  
**Score entrada:** {float(row.get('score_entry', 0.0)) * 100:.0f}%  
**Score accesibilidad:** {float(row.get('score_affordability', 0.0)) * 100:.0f}%  
**Score legal:** {float(row.get('score_legal_pct', 0.0)):.0f}%  
**Seguridad:** {float(row.get('score_safety', 0.0)) * 100:.0f}%  
**Crimen (inverso):** {float(row.get('score_crime', 0.0)) * 100:.0f}%  
**Riesgo ocupacion:** {float(row.get('riesgo_norm', 0.0)) * 100:.0f}%
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
        & (work["score_location"] >= 0.35)
        & (work["country"].fillna("") != "UAE")
    ].copy()
    if filtered.empty:
        return None
    return filtered.sort_values("score_oportunidad", ascending=False).head(1).iloc[0].to_dict()


def page_1(top20: pd.DataFrame, base: pd.DataFrame) -> None:
    st.subheader("Pagina 1: Mapa, grafica y tabla")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Paises Top 13", int(top20["country"].nunique()))
    c2.metric("Score medio", f"{top20['score_oportunidad'].mean():.2f}")
    c3.metric("Precio medio", f"EUR {top20['price_eur_num'].mean():,.0f}")
    c4.metric("Renta media", f"EUR {top20['rent_eur_month_num'].mean():,.0f}/mes")

    col_map, col_bar = st.columns([1.5, 1.0])
    with col_map:
        st.markdown("### Mapa Top 13 — paises iluminados")
        map_data = top20.reset_index(drop=True).copy()

        map_fig = go.Figure()

        # Capa choropleth: ilumina los paises del Top 20
        map_fig.add_trace(go.Choropleth(
            locations=map_data["country"],
            locationmode="country names",
            z=map_data["score_oportunidad"],
            colorscale=[[0, "rgba(255,200,0,0.20)"], [1, "rgba(230,80,0,0.65)"]],
            showscale=False,
            marker_line_color="gold",
            marker_line_width=1.5,
            hoverinfo="skip",
            showlegend=False,
        ))

        # Capa scatter: punto por inmueble
        marker_size = (map_data["rent_eur_month_num"].fillna(500) / map_data["rent_eur_month_num"].fillna(500).max() * 18 + 7).fillna(10)
        map_fig.add_trace(go.Scattergeo(
            lat=map_data["latitude"],
            lon=map_data["longitude"],
            mode="markers+text",
            text=map_data["rank_final"].astype(str),
            textposition="top center",
            textfont=dict(size=9, color="white"),
            marker=dict(
                size=marker_size,
                color=map_data["score_oportunidad"],
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Score", thickness=12, len=0.6),
                line=dict(color="white", width=0.8),
            ),
            customdata=map_data[["location", "price_in_Euro", "entry_price_eur", "zone_rental_price", "rank_final", "country"]].values,
            hovertemplate=(
                "<b>#%{customdata[4]} %{customdata[5]}</b><br>"
                "Ubicacion: %{customdata[0]}<br>"
                "Score: %{marker.color:.1f}%<br>"
                "Renta: %{customdata[3]}<br>"
                "Precio: %{customdata[1]}<extra></extra>"
            ),
            name="Top 13",
        ))

        map_fig.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="rgba(150,150,150,0.5)",
                showland=True,
                landcolor="rgba(240,240,240,1)",
                showocean=True,
                oceancolor="rgba(210,230,255,1)",
                projection_type="natural earth",
            ),
            height=540,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(map_fig, width="stretch")

    with col_bar:
        st.markdown("### Grafico 1: Score por pais (Top 13)")
        chart_top20 = top20[["country", "score_oportunidad", "annual_yield", "riesgo_norm"]].copy()
        bar_score = px.bar(
            chart_top20.sort_values("score_oportunidad", ascending=False),
            x="country",
            y="score_oportunidad",
            hover_data=["annual_yield", "riesgo_norm"],
            color="score_oportunidad",
            color_continuous_scale="Blues",
            height=260,
            range_y=[0, 100],
        )
        bar_score.update_layout(
            xaxis_tickangle=-45,
            margin=dict(l=0, r=0, t=0, b=0),
            yaxis_title="Score oportunidad (0-100%)",
            coloraxis=dict(cmin=0, cmax=100),
        )
        st.plotly_chart(bar_score, width="stretch")

        st.markdown("### Grafico 2: Ubicacion (urbano y playa)")
        bars2 = top20[["country", "score_urban", "score_beach", "score_location"]].copy()
        bars2 = bars2.melt(id_vars=["country"], var_name="componente", value_name="valor")
        bars2["valor_pct"] = bars2["valor"] * 100
        bar_components = px.bar(
            bars2,
            x="country",
            y="valor_pct",
            color="componente",
            barmode="group",
            height=260,
        )
        bar_components.update_layout(xaxis_tickangle=-45, margin=dict(l=0, r=0, t=0, b=0), yaxis_title="Ubicacion (0-100)")
        st.plotly_chart(bar_components, width="stretch")

    st.markdown("### Tabla Top 13")
    table_cols = [
        "rank_final",
        "country",
        "location",
        "price_in_Euro",
        "entry_price_eur",
        "zone_rental_price",
        "leyes_de_ocupacion_comentario",
        "leyes_de_ocupacion_url",
        "score_legal_pct",
        "score_location",
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
            "score_legal_pct": st.column_config.NumberColumn("score_legal_%", format="%.0f%%"),
            "score_location": st.column_config.NumberColumn("score_location", format="%.2f"),
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


def page_2(top20: pd.DataFrame, work: pd.DataFrame) -> None:
    st.subheader("Pagina 2: Ruleta y resultado")

    col_ruleta, col_info = st.columns([1.1, 1.0])

    with col_ruleta:
        st.markdown("### Ruleta de oportunidad")
        # Ruleta: peso = seguridad (score_legal) × rentabilidad (score_target_profile)
        wheel = top20[["rank_final", "country", "score_legal", "score_target_profile"]].copy()
        wheel["score_seg_rent"] = (
            0.55 * wheel["score_legal"].fillna(0)
            + 0.45 * wheel["score_target_profile"].fillna(0)
        ).clip(lower=0.01)  # evita ceros para que todos aparezcan
        wheel["peso_ruleta"] = wheel["score_seg_rent"] / wheel["score_seg_rent"].sum()
        # Puntuacion de 1 a 10
        raw_min = wheel["score_seg_rent"].min()
        raw_max = wheel["score_seg_rent"].max()
        if raw_max > raw_min:
            wheel["puntuacion_10"] = (1.0 + 9.0 * (wheel["score_seg_rent"] - raw_min) / (raw_max - raw_min)).round(1)
        else:
            wheel["puntuacion_10"] = 5.0

        st.caption(
            "**Puntuacion 1-10 por pais**: 55% seguridad (riesgo ocupacion + leyes ocupacion + crime_index + safety_index) "
            "+ 45% objetivo precio-renta (cercania a 30k EUR & 1.200 EUR/mes)"
        )
        pie_fig = px.pie(
            wheel,
            names="country",
            values="puntuacion_10",
            hole=0.45,
            height=560,
            title="Seguridad × Rentabilidad (puntuacion 1-10)",
        )
        pie_fig.update_traces(
            textposition="inside",
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>Puntuacion: %{value:.1f}/10<extra></extra>",
        )
        pie_fig.update_layout(title_font_size=13, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(pie_fig, width="stretch")

        if st.button("Girar ruleta"):
            winner_country = np.random.choice(wheel["country"], p=wheel["peso_ruleta"])
            winner_row = top20[top20["country"] == winner_country].iloc[0]
            st.session_state.winner_country = winner_country
            st.session_state.winner_row = winner_row.to_dict()

        if st.button("Buscar mejor con estos filtros"):
            best_filtered = get_best_row_from_filters(
                work=work,
                max_price=float(st.session_state.max_price),
                min_rent=float(st.session_state.min_rent),
                max_payback=float(st.session_state.max_payback),
            )
            if best_filtered is None:
                st.warning("No hay resultados con esos filtros.")
            else:
                st.session_state.filtered_row = best_filtered

        st.markdown("### Buscar por pais")
        country_input = st.text_input("Escribe un pais", placeholder="Ejemplo: Spain")
        if st.button("Buscar pisos"):
            if country_input.strip():
                pisos_found = (
                    work[work["country"].str.lower() == country_input.strip().lower()]
                    .sort_values("score_oportunidad", ascending=False)
                    .copy()
                )
                if pisos_found.empty:
                    st.warning(f"No hay pisos para '{country_input.strip()}' en los datos actuales.")
                else:
                    st.session_state.pisos_pais = pisos_found.to_dict("records")
                    st.session_state.pisos_pais_name = country_input.strip()
                    st.session_state.pisos_pais_idx = 0

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

        if "pisos_pais" in st.session_state:
            pisos = st.session_state.pisos_pais
            idx = int(st.session_state.get("pisos_pais_idx", 0))
            total = len(pisos)
            nombre_pais = st.session_state.get("pisos_pais_name", "")
            st.markdown("---")
            st.markdown(f"#### {nombre_pais} — piso {idx + 1} de {total}")
            render_property_result(f"Piso {idx + 1}", pisos[idx])
            col_prev, col_mid, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.button("\u25c4 Anterior", disabled=(idx == 0), key="btn_prev_piso"):
                    st.session_state.pisos_pais_idx = idx - 1
                    st.rerun()
            with col_mid:
                st.markdown(
                    f"<div style='text-align:center;padding-top:8px;font-size:13px'>{idx + 1} / {total}</div>",
                    unsafe_allow_html=True,
                )
            with col_next:
                if st.button("Siguiente \u25ba", disabled=(idx >= total - 1), key="btn_next_piso"):
                    st.session_state.pisos_pais_idx = idx + 1
                    st.rerun()

        st.markdown("### Top 8 — Filtro estricto: precio 30k–45k EUR | renta ≥ 1.200 EUR/mes")
        st.caption("Mejor piso por pais. Score = 60% cercania a 30k + 40% cercania a 1.200 EUR/mes.")
        top8_strict = work[
            work["price_eur_num"].between(30_000, 45_000, inclusive="both")
            & (work["rent_eur_month_num"] >= 1_200)
            & work["country"].notna()
            & work["url"].notna()
        ].copy()
        if not top8_strict.empty:
            top8_strict["score_estricto"] = (
                0.60 * (1.0 - (top8_strict["price_eur_num"] - 30_000).abs() / 30_000).clip(0, 1)
                + 0.40 * (top8_strict["rent_eur_month_num"] / 1_200).clip(0, 1)
            ) * 100
            top8_strict = (
                top8_strict.sort_values("score_estricto", ascending=False)
                .groupby("country", as_index=False).head(1)
                .sort_values("score_estricto", ascending=False)
                .head(8)
                .reset_index(drop=True)
            )
            top8_strict.insert(0, "#", range(1, len(top8_strict) + 1))
            t8_cols = [c for c in ["#", "country", "location", "price_eur_num", "rent_eur_month_num", "score_estricto", "leyes_de_ocupacion_comentario", "url"] if c in top8_strict.columns]
            st.dataframe(
                top8_strict[t8_cols].reset_index(drop=True),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "url": st.column_config.LinkColumn("Enlace"),
                    "price_eur_num": st.column_config.NumberColumn("Precio (EUR)", format="%.0f"),
                    "rent_eur_month_num": st.column_config.NumberColumn("Renta/mes (EUR)", format="%.0f"),
                    "score_estricto": st.column_config.NumberColumn("Score %", format="%.1f"),
                    "leyes_de_ocupacion_comentario": st.column_config.TextColumn("Ley ocupacion"),
                },
            )
        else:
            st.info("No hay pisos que cumplan precio 30k–45k EUR y renta ≥ 1.200 EUR/mes con los datos actuales.")


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
    if "use_precomputed_top20" not in st.session_state:
        st.session_state.use_precomputed_top20 = True
    if "validate_live_urls" not in st.session_state:
        st.session_state.validate_live_urls = False

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
        st.session_state.use_precomputed_top20 = st.checkbox(
            "Usar Top 20 preprocesado (recomendado)",
            value=bool(st.session_state.use_precomputed_top20),
            help="Lee la lista validada en notebook una sola vez y evita recalculo pesado en Streamlit.",
        )
        st.session_state.validate_live_urls = st.checkbox(
            "Validar enlaces en vivo (mas lento)",
            value=bool(st.session_state.validate_live_urls),
            help="Si esta activo, el Top 20 verifica cada URL contra la web para excluir anuncios inactivos.",
            disabled=bool(st.session_state.use_precomputed_top20),
        )
        st.markdown("---")
        st.markdown("**Criterio clave**: prioriza precios cercanos a 30k-60k, renta alta y riesgo bajo.")

    df = load_base()
    work = build_workframe(df)

    top20 = pd.DataFrame()
    if bool(st.session_state.use_precomputed_top20):
        top20 = get_top20_from_precomputed(work)
        if top20.empty:
            st.warning(
                "No se encontro un Top 20 preprocesado valido. Ejecuta la exportacion en notebook o desactiva 'Usar Top 20 preprocesado'."
            )

    if top20.empty:
        top20 = get_top20(
            work,
            st.session_state.max_price,
            st.session_state.min_rent,
            st.session_state.max_payback,
            validate_live_urls=bool(st.session_state.validate_live_urls),
        )

    page = st.radio("Selecciona pagina", ["Pagina 1", "Pagina 2"], horizontal=True)

    if page == "Pagina 1":
        page_1(top20, work)
    else:
        page_2(top20, work)


if __name__ == "__main__":
    main()

import re
import hashlib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from core import render_top_nav
from modules.peer_service import fetch_peer_pack, normalize_symbol

st.set_page_config(
    page_title="同行分析",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------- 全局样式：所有白色/灰色字体改为高亮暖黄色 #FFE484 --------------------
st.markdown(
    f"""
<style>
:root{{
    --bg:#07070B;
    --bg2:#0E0E16;
    --card:#141420;
    --line:rgba(255,45,85,.35);
    --red:#ff2d55;
    --text:#FFE484;     /* 高亮暖黄 */
    --muted:#FFE484;    /* 原灰色改为暖黄 */
}}

/* 隐藏侧栏 */
[data-testid="stSidebar"] {{display: none;}}

/* 主背景 */
[data-testid="stAppViewContainer"]{{
    background:
      radial-gradient(1200px 600px at 90% -10%, rgba(255,45,85,.20), transparent 55%),
      radial-gradient(900px 500px at -10% 20%, rgba(255,45,85,.12), transparent 45%),
      linear-gradient(180deg, var(--bg), var(--bg2));
    color: var(--text);
}}

/* 顶部透明 */
[data-testid="stHeader"]{{ background: transparent; }}

/* 页面主体 */
.block-container{{
    max-width: 1280px;
    padding-top: 1.2rem;
    padding-bottom: 1rem;
}}
h1, h2, h3, h4, p, label, .stMarkdown, .stCaption {{
    color: var(--text) !important;
    letter-spacing: .2px;
}}
.muted {{color: var(--muted) !important; font-size: .92rem;}}

/* 输入控件 */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
[data-testid="stNumberInput"] > div > div,
[data-testid="stTextInput"] > div > div {{
    background: #151522 !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
}}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within,
[data-testid="stNumberInput"] > div > div:focus-within,
[data-testid="stTextInput"] > div > div:focus-within {{
    border-color: var(--red) !important;
    box-shadow: 0 0 0 1px var(--red), 0 0 16px rgba(255,45,85,.25) !important;
}}

/* 输入内容暖黄色 */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
div[data-baseweb="input"] input {{
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
    caret-color: var(--text) !important;
}}
.stTextInput input::placeholder,
.stNumberInput input::placeholder,
.stTextArea textarea::placeholder,
div[data-baseweb="input"] input::placeholder {{
    color: rgba(255,228,132,0.70) !important;
    -webkit-text-fill-color: rgba(255,228,132,0.70) !important;
}}

/* Select 控件内文字 */
div[data-baseweb="select"] *,
div[data-baseweb="select"] input {{
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
}}

/* ========= 关键修复：弹出层、下拉菜单、多选框选项 ========= */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"],
div[role="listbox"] {{
    background: #151522 !important;
    border: 1px solid rgba(255,45,85,.35) !important;
    color: var(--text) !important;
}}

/* 选项条目 */
div[data-baseweb="menu"] div[role="option"],
div[data-baseweb="menu"] li[role="option"],
ul[role="listbox"] li,
div[role="listbox"] div[role="option"],
div[data-baseweb="menu"] div[role="menuitem"] {{
    background: #151522 !important;
    color: var(--text) !important;
}}

/* hover 状态 */
div[data-baseweb="menu"] div[role="option"]:hover,
div[data-baseweb="menu"] li[role="option"]:hover,
ul[role="listbox"] li:hover,
div[role="listbox"] div[role="option"]:hover {{
    background: rgba(255,45,85,.22) !important;
    color: var(--text) !important;
}}

/* 选中状态 */
div[data-baseweb="menu"] [aria-selected="true"],
div[role="listbox"] [aria-selected="true"] {{
    background: rgba(255,45,85,.28) !important;
    color: var(--text) !important;
}}

/* 自定义 Excel 风格筛选器的复选框文字 */
div[data-testid="stCheckbox"] label {{
    color: var(--text) !important;
}}
div[data-testid="stCheckbox"] label span {{
    color: var(--text) !important;
}}

/* popover 内部所有文字 */
div[data-testid="stPopoverContent"] *,
div[data-baseweb="popover"] * {{
    color: var(--text) !important;
}}

/* popover 内部输入框背景 */
div[data-testid="stPopoverContent"] div[data-baseweb="input"] > div,
div[data-baseweb="popover"] div[data-baseweb="input"] > div {{
    background: #10101A !important;
    border: 1px solid rgba(255,45,85,.35) !important;
}}

/* 按钮（全选/清空/反选）在 popover 内保持一致 */
div[data-testid="stPopoverContent"] div.stButton > button {{
    background: rgba(255,45,85,0.2) !important;
    border: 1px solid var(--red) !important;
    color: var(--text) !important;
}}
div[data-testid="stPopoverContent"] div.stButton > button:hover {{
    background: rgba(255,45,85,0.4) !important;
}}

/* 按钮全局 */
div.stButton > button{{
    color: var(--text) !important;
    border: 1px solid var(--red) !important;
    background: linear-gradient(90deg, #7e0d27, #bf173c, #ff2d55) !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}}
div.stButton > button:hover{{
    box-shadow: 0 0 18px rgba(255,45,85,.45);
    transform: translateY(-1px);
}}

/* tabs 样式优化 */
button[data-baseweb="tab"]{{
    color: var(--text) !important;
    background: rgba(255,255,255,.03) !important;
    border: 1px solid rgba(255,45,85,.18) !important;
    border-radius: 10px !important;
    margin-right: 6px;
}}
button[data-baseweb="tab"][aria-selected="true"]{{
    color: var(--text) !important;
    border-color: rgba(255,45,85,.55) !important;
    box-shadow: inset 0 0 16px rgba(255,45,85,.18);
}}

/* metric 卡片 */
div[data-testid="stMetric"]{{
    background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.00)), var(--card);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 10px 12px;
    box-shadow: inset 0 0 22px rgba(255,45,85,.08), 0 10px 24px rgba(0,0,0,.35);
}}
div[data-testid="stMetricLabel"]{{ color: var(--muted) !important; }}
div[data-testid="stMetricValue"]{{ color: var(--text) !important; font-size: 1.15rem; }}

/* dataframe 表格样式增强 */
[data-testid="stDataFrame"]{{
    border: 1px solid var(--line);
    border-radius: 10px;
    overflow: hidden;
}}
[data-testid="stDataFrame"] div[role="grid"] {{
    font-size: 13px;
    color: var(--text) !important;
    background: #0E0E16 !important;
}}
[data-testid="stDataFrame"] .dataframe thead th {{
    background: #1a1a2a !important;
    color: var(--text) !important;
    border-bottom: 1px solid var(--line);
}}
[data-testid="stDataFrame"] .dataframe tbody td {{
    color: var(--text) !important;
    background: #0E0E16 !important;
}}

/* expander 样式 */
details[data-testid="stExpander"]{{
    border: 1px solid var(--line);
    border-radius: 10px;
    background: rgba(20,20,32,.6);
}}
details[data-testid="stExpander"] summary {{
    color: var(--text) !important;
}}

/* 分割线 */
.hr{{
    height:1px;
    background: linear-gradient(90deg, transparent, rgba(255,45,85,.55), transparent);
    margin: 8px 0 16px 0;
}}

/* 三列 metrics 卡片区域调整间距 */
div[data-testid="column"] div[data-testid="stMetric"] {{
    margin: 0 0.2rem;
}}

/* 自定义容器边框圆角 */
div[data-testid="stContainer"] {{
    border-radius: 12px;
}}

/* 信息框、警告框文字颜色 */
div[data-testid="stInfo"], div[data-testid="stWarning"], div[data-testid="stError"] {{
    color: var(--text) !important;
}}
</style>
""",
    unsafe_allow_html=True,
)

render_top_nav("peer")
st.title("🧭 个股同行分析")
st.caption("数据源：东方财富（AkShare）｜横截面对比（横轴为指标，不是时间）")
st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

SPECIAL_NAMES = {"行业平均", "行业中值"}


# -------------------- 数据读取 --------------------
@st.cache_data(ttl=1800, show_spinner="正在加载同行数据...")
def load_data(symbol: str):
    return fetch_peer_pack(symbol)


def safe_get_df(pack: dict, key: str) -> pd.DataFrame:
    if not isinstance(pack, dict):
        return pd.DataFrame()
    df = pack.get(key)
    return df if isinstance(df, pd.DataFrame) else pd.DataFrame()


# -------------------- 数据处理 --------------------
def add_display_name(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    d = df.copy()
    d["代码"] = d["代码"].astype(str).fillna("")
    d["简称"] = d["简称"].astype(str).fillna("")
    d["代码"] = d["代码"].str.extract(r"(\d{6})", expand=False).fillna(d["代码"])

    def _disp(row):
        code = str(row["代码"])
        name = str(row["简称"])
        if name in SPECIAL_NAMES or code in SPECIAL_NAMES:
            return name
        return f"{name}({code})" if code else name

    d["显示名"] = d.apply(_disp, axis=1)
    return d


def _parse_number(v):
    if pd.isna(v):
        return np.nan
    if isinstance(v, (int, float, np.number)):
        return float(v)

    s = str(v).strip().replace(",", "")
    if s in {"", "--", "-", "nan", "None"}:
        return np.nan

    unit = 1.0
    if s.endswith("亿"):
        unit = 1e8
        s = s[:-1]
    elif s.endswith("万"):
        unit = 1e4
        s = s[:-1]

    if s.endswith("%"):
        s = s[:-1]

    s = re.sub(r"[^0-9\\.\\-]", "", s)
    if s in {"", "-", ".", "-."}:
        return np.nan

    try:
        return float(s) * unit
    except Exception:
        return np.nan


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    d = df.copy()
    skip = {"代码", "简称", "显示名"}
    for c in d.columns:
        if c not in skip:
            d[c] = d[c].apply(_parse_number)
    return d


def default_companies(df: pd.DataFrame, symbol: str):
    """默认全选全部公司（含行业平均/中值）"""
    if df is None or df.empty:
        return []
    return df["显示名"].dropna().drop_duplicates().tolist()


def robust_normalize(long_df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    """每家公司按“首个有效指标值=100”标准化"""
    d = long_df.copy()
    d["指标"] = pd.Categorical(d["指标"], categories=metrics, ordered=True)
    d = d.sort_values(["显示名", "指标"])

    def first_valid(s):
        s = s.dropna()
        return s.iloc[0] if len(s) else np.nan

    base = d.groupby("显示名")["数值"].transform(first_valid)
    invalid = base.isna() | (base == 0)

    d["数值_std"] = d["数值"] / base * 100
    d.loc[~invalid, "数值"] = d.loc[~invalid, "数值_std"]
    d.drop(columns=["数值_std"], inplace=True)

    bad = d.loc[invalid, "显示名"].dropna().unique().tolist()
    if bad:
        st.warning(f"以下公司首个有效指标为0或缺失，已跳过标准化：{', '.join(bad)}", icon="⚠️")
    return d


# -------------------- Excel风格下拉勾选 --------------------
def _opt_key(base_key: str, opt: str) -> str:
    digest = hashlib.md5(str(opt).encode("utf-8")).hexdigest()[:12]
    return f"{base_key}_opt_{digest}"


def _init_excel_filter(key: str, options: list[str], default_selected: list[str]):
    init_key = f"{key}_inited"

    options = list(dict.fromkeys([str(x) for x in options]))
    default_set = set(default_selected)

    if init_key not in st.session_state:
        for o in options:
            st.session_state[_opt_key(key, o)] = (o in default_set)
        st.session_state[init_key] = True
        return

    for o in options:
        k = _opt_key(key, o)
        if k not in st.session_state:
            st.session_state[k] = (o in default_set)


def excel_like_filter(
    label: str,
    options: list[str],
    default_selected: list[str],
    key: str,
    search_placeholder: str = "输入关键词搜索…",
    height: int = 280,
):
    options = list(dict.fromkeys([str(x) for x in options]))
    default_selected = [x for x in default_selected if x in options]

    if not options:
        st.info(f"{label}：无可选项")
        return []

    _init_excel_filter(key, options, default_selected)

    with st.popover(
        f"{label}（已选 {sum(st.session_state.get(_opt_key(key, o), False) for o in options)}/{len(options)}）",
        use_container_width=True
    ):
        kw = st.text_input(
            "搜索",
            key=f"{key}_search",
            placeholder=search_placeholder,
            label_visibility="collapsed",
        )

        filtered = [o for o in options if (kw.lower() in o.lower())] if kw else options

        c1, c2, c3 = st.columns(3)
        if c1.button("全选当前", key=f"{key}_btn_all", use_container_width=True):
            for o in filtered:
                st.session_state[_opt_key(key, o)] = True
            st.rerun()

        if c2.button("清空当前", key=f"{key}_btn_clear", use_container_width=True):
            for o in filtered:
                st.session_state[_opt_key(key, o)] = False
            st.rerun()

        if c3.button("反选当前", key=f"{key}_btn_inv", use_container_width=True):
            for o in filtered:
                k = _opt_key(key, o)
                st.session_state[k] = not bool(st.session_state.get(k, False))
            st.rerun()

        box = st.container(height=height, border=True)
        if not filtered:
            box.caption("无匹配项")
        else:
            for o in filtered:
                box.checkbox(o, key=_opt_key(key, o))

    selected = [o for o in options if st.session_state.get(_opt_key(key, o), False)]
    return selected


# -------------------- 会话状态 --------------------
def reset_panel_states():
    prefixes = ("growth_", "valuation_", "dupont_", "scale_")
    to_del = [k for k in st.session_state.keys() if k.startswith(prefixes)]
    for k in to_del:
        del st.session_state[k]


if "peer_loaded" not in st.session_state:
    st.session_state.peer_loaded = False
if "peer_symbol" not in st.session_state:
    st.session_state.peer_symbol = ""
if "peer_pack" not in st.session_state:
    st.session_state.peer_pack = None


# -------------------- 顶部加载区 --------------------
with st.container(border=True):
    c1, c2 = st.columns([2.2, 1.0])
    with c1:
        symbol_input = st.text_input(
            "股票代码（支持 000895 / SZ000895）",
            value=st.session_state.peer_symbol or "SZ000895",
            placeholder="例如：000895 或 SZ000895",
        )
    with c2:
        st.write("")
        run = st.button("加载同行数据", use_container_width=True, type="primary")

if run:
    try:
        symbol = normalize_symbol(symbol_input)
        pack = load_data(symbol)

        if symbol != st.session_state.peer_symbol:
            reset_panel_states()

        st.session_state.peer_symbol = symbol
        st.session_state.peer_pack = pack
        st.session_state.peer_loaded = True
    except Exception as e:
        st.error(f"加载失败：{e}")
        st.stop()


# -------------------- 绘图面板 --------------------
def render_line_panel(raw_df: pd.DataFrame, symbol: str, title: str, key_prefix: str):
    st.subheader(title)

    if raw_df is None or raw_df.empty:
        st.info("暂无数据。")
        return

    df = add_display_name(raw_df)
    df = coerce_numeric(df)

    include_rank = st.toggle("包含“排名”类指标", value=False, key=f"{key_prefix}_rank")

    metric_cols = [c for c in df.columns if c not in ["代码", "简称", "显示名"]]
    if not include_rank:
        metric_cols = [c for c in metric_cols if "排名" not in c]
    metric_cols = [c for c in metric_cols if df[c].notna().any()]

    if not metric_cols:
        st.warning("没有可用指标可绘图。")
        return

    company_options = df["显示名"].dropna().drop_duplicates().tolist()

    m1, m2, m3 = st.columns(3, gap="small")
    m1.metric("可选指标", len(metric_cols))
    m2.metric("可选公司", len(company_options))
    m3.metric("当前股票", symbol)

    left, mid, right = st.columns([1.6, 1.6, 0.8], vertical_alignment="top")

    with left:
        metrics = excel_like_filter(
            label="选择指标",
            options=metric_cols,
            default_selected=metric_cols[: min(6, len(metric_cols))],
            key=f"{key_prefix}_metrics",
            height=300,
        )

    with mid:
        selected_companies = excel_like_filter(
            label="选择公司",
            options=company_options,
            default_selected=default_companies(df, symbol),
            key=f"{key_prefix}_companies",
            height=300,
        )

    with right:
        normalize = st.toggle("标准化（首指标=100）", value=False, key=f"{key_prefix}_norm")

    if len(metrics) == 0:
        st.info("请至少选择 1 个指标。")
        return
    if len(selected_companies) == 0:
        st.info("请至少选择 1 家公司。")
        return

    plot_df = df[df["显示名"].isin(selected_companies)][["显示名"] + metrics].copy()
    long_df = (
        plot_df.melt(id_vars=["显示名"], var_name="指标", value_name="数值")
        .dropna(subset=["数值"])
        .copy()
    )

    if long_df.empty:
        st.info("当前筛选条件下无可绘图数据。")
        return

    long_df["指标"] = pd.Categorical(long_df["指标"], categories=metrics, ordered=True)
    long_df = long_df.sort_values(["显示名", "指标"])

    if normalize:
        long_df = robust_normalize(long_df, metrics)
        y_title = "标准化指数（首指标=100）"
    else:
        y_title = "指标值"

    fig = px.line(
        long_df,
        x="指标",
        y="数值",
        color="显示名",
        markers=True,
        title=f"{title} - 折线对比",
        template="plotly_dark",
        color_discrete_sequence=[
            "#ff2d55", "#ff5f7e", "#ff8aa3", "#ffb3c2", "#ffd1da",
            "#8e7dff", "#56cfe1", "#80ed99", "#f9c74f", "#f8961e"
        ],
    )
    fig.update_layout(
        height=560,
        hovermode="x unified",
        xaxis_title="指标",
        yaxis_title=y_title,
        legend_title_text="公司",
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,20,32,0.65)",
        font=dict(color="#FFE484"),  # 图表字体改为暖黄色
    )
    fig.update_xaxes(
        tickangle=-35,
        gridcolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.25)",
        title_font=dict(color="#FFE484"),
        tickfont=dict(color="#FFE484"),
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.25)",
        title_font=dict(color="#FFE484"),
        tickfont=dict(color="#FFE484"),
    )
    # 更新图例文字颜色
    fig.update_layout(legend=dict(font=dict(color="#FFE484")))

    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

    with st.expander("查看明细数据", expanded=False):
        show_cols = ["显示名"] + metrics
        detail = df[df["显示名"].isin(selected_companies)][show_cols].copy()
        detail = detail.set_index("显示名")
        detail = detail.reindex(selected_companies)

        def fmt(x):
            if pd.isna(x):
                return "-"
            return f"{x:,.2f}"

        styled = detail.style.format(fmt)
        styled = styled.set_table_styles([
            {"selector": "th", "props": [("color", "#FFE484"), ("background", "#1a1a2a")]},
            {"selector": "td", "props": [("color", "#FFE484"), ("background", "#0E0E16")]},
        ])
        h = min(700, max(260, 38 * (len(detail) + 1)))
        st.dataframe(styled, use_container_width=True, height=h)
        st.caption(f"共 {len(detail)} 行 × {len(detail.columns)} 列")


# -------------------- 主体 --------------------
if st.session_state.peer_loaded and st.session_state.peer_pack is not None:
    pack = st.session_state.peer_pack
    symbol = st.session_state.peer_symbol

    t1, t2, t3, t4 = st.tabs(["成长性", "估值", "杜邦", "规模"])
    with t1:
        render_line_panel(safe_get_df(pack, "growth"), symbol, "成长性对比", "growth")
    with t2:
        render_line_panel(safe_get_df(pack, "valuation"), symbol, "估值对比", "valuation")
    with t3:
        render_line_panel(safe_get_df(pack, "dupont"), symbol, "杜邦对比", "dupont")
    with t4:
        render_line_panel(safe_get_df(pack, "scale"), symbol, "规模对比", "scale")
else:
    st.info("请输入股票代码并点击【加载同行数据】。")
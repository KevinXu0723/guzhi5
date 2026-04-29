import streamlit as st
from core import render_top_nav

st.set_page_config(page_title="股票分析平台", page_icon="📊", layout="wide")

# ===== 首页样式（偏红风格）=====
st.markdown("""
<style>
/* 页面整体 */
.main > div {
    padding-top: 1.2rem;
}

/* 标题区卡片（蓝 -> 红） */
.hero-card {
    background: linear-gradient(135deg, #3f0a0a 0%, #991b1b 55%, #dc2626 100%);
    border-radius: 16px;
    padding: 24px 26px;
    color: #ffffff;
    box-shadow: 0 8px 24px rgba(220, 38, 38, 0.28);
    margin-bottom: 14px;
}

.hero-title {
    font-size: 30px;
    font-weight: 800;
    margin: 0 0 8px 0;
    letter-spacing: 0.3px;
}

.hero-subtitle {
    font-size: 15px;
    opacity: 0.95;
    margin: 0;
}

/* 推广信息条（红系） */
.promo {
    margin-top: 10px;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-left: 4px solid #dc2626;
    border-radius: 10px;
    padding: 10px 12px;
    color: #7f1d1d;
    font-size: 14px;
}

/* 小标签 */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 8px;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.35);
}

/* 功能卡片 */
.tool-card {
    background: #ffffff;
    border: 1px solid #fee2e2;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(220, 38, 38, 0.08);
    margin-top: 18px;
}

.tool-title {
    font-size: 20px;
    font-weight: 700;
    color: #7f1d1d;
    margin-bottom: 6px;
}

.tool-desc {
    color: #555;
    font-size: 14px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# 顶部导航
render_top_nav("home")

# ===== 首页内容 =====
st.markdown("""
<div class="hero-card">
    <div>
        <span class="badge">数据驱动</span>
        <span class="badge">投研效率</span>
    </div>
    <h1 class="hero-title">📊 股票分析平台</h1>
    <p class="hero-subtitle">使用顶部导航进入不同模块：估值工具 / 同行分析 / 增长率计算器</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="promo">
    📣 公众号：<b>持续加载</b> &nbsp;&nbsp;|&nbsp;&nbsp; 
    📕 小红书：<b>面壁者</b>
</div>
""", unsafe_allow_html=True)

st.write("")
st.write("欢迎使用，建议先关注公众号“持续加载”，加入微信交流群，学习了解价值投资后使用此工具。")

# ===== 新增：功能入口区域 =====
st.markdown("""
<div class="tool-card">
    <div class="tool-title">📈 年复合增长率计算器</div>
    <div class="tool-desc">
        支持标准 CAGR 计算，也支持初值为负、终值转正时基于线性假设计算转正后 CAGR。
    </div>
</div>
""", unsafe_allow_html=True)

# 方式一：使用按钮跳转，推荐 Streamlit 新版本使用
if st.button("进入增长率计算器", type="primary"):
    st.switch_page("pages/growth.py")

# 如果你的 Streamlit 版本较旧，不支持 st.switch_page，
# 可以注释掉上面的 if st.button 部分，改用下面这一行：
# st.page_link("pages/growth.py", label="📈 进入增长率计算器", icon="📈")

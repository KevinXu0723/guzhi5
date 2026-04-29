import streamlit as st
from core import render_top_nav

st.set_page_config(page_title="增长率计算器", page_icon="📈", layout="wide")


def compute_cagr(init_val, final_val, n_years):
    """
    计算 CAGR。

    支持两类情况：
    1. 初值 > 0，终值 > 0：
       使用标准 CAGR 公式。

    2. 初值 < 0，终值 > 0：
       假设从初值到终值之间为线性增长，
       先找到首次转正的年份，
       再计算转正后到终值之间的 CAGR。
    """

    if n_years <= 0:
        raise ValueError("总年数必须大于 0")

    # ===== 情况一：标准 CAGR =====
    if init_val > 0 and final_val > 0:
        cagr = (final_val / init_val) ** (1 / n_years) - 1

        return {
            "method": "标准CAGR",
            "cagr": cagr
        }

    # ===== 情况二：初值为负，终值为正 =====
    elif init_val < 0 and final_val > 0:
        annual_increment = (final_val - init_val) / n_years

        first_positive_year = None
        first_positive_value = None

        # 从第 1 年末开始，逐年寻找首次转正年份
        for year in range(1, n_years + 1):
            current_value = init_val + annual_increment * year

            if current_value > 0:
                first_positive_year = year
                first_positive_value = current_value
                break

        # 理论上，只要 init_val < 0 且 final_val > 0，一定会转正
        # 这里保留异常处理，增强健壮性
        if first_positive_year is None:
            return {
                "method": "负转正（线性假设）",
                "annual_increment": annual_increment,
                "first_positive_year": None,
                "first_positive_value": None,
                "remaining_years": None,
                "cagr": None,
                "message": "在给定年限内未转正，无法计算转正后 CAGR。"
            }

        remaining_years = n_years - first_positive_year

        # 如果最后一年才转正，则没有剩余年份计算 CAGR
        if remaining_years <= 0:
            return {
                "method": "负转正（线性假设）",
                "annual_increment": annual_increment,
                "first_positive_year": first_positive_year,
                "first_positive_value": first_positive_value,
                "remaining_years": remaining_years,
                "cagr": None,
                "message": "现金流在最后一年才转正，没有剩余期间用于计算 CAGR。"
            }

        # 转正后 CAGR
        cagr = (final_val / first_positive_value) ** (1 / remaining_years) - 1

        return {
            "method": "负转正（线性假设）",
            "annual_increment": annual_increment,
            "first_positive_year": first_positive_year,
            "first_positive_value": first_positive_value,
            "remaining_years": remaining_years,
            "cagr": cagr,
            "message": "计算成功"
        }

    # ===== 其他暂不支持情况 =====
    else:
        raise ValueError("当前仅支持：初值为正且终值为正，或初值为负且终值为正的情况。")


# ===== 顶部导航 =====
render_top_nav("growth")

# ===== 页面标题 =====
st.markdown("## 📈 年复合增长率计算器")
st.markdown("支持正负初值，初值为负时基于线性增长假设计算转正后 CAGR。")

# ===== 输入区 =====
col1, col2, col3 = st.columns(3)

with col1:
    init_val = st.number_input(
        "初值（第0年末现金流）",
        value=1.00,
        format="%.2f"
    )

with col2:
    final_val = st.number_input(
        "终值（最后一年末现金流）",
        value=1.00,
        format="%.2f"
    )

with col3:
    n_years = st.number_input(
        "总年数",
        min_value=1,
        value=1,
        step=1
    )

# ===== 计算按钮 =====
if st.button("计算增长率", type="primary"):
    try:
        result = compute_cagr(init_val, final_val, n_years)

        st.success("计算完成")
        st.write(f"**计算方法：** {result['method']}")

        # 标准 CAGR 显示
        if result["method"] == "标准CAGR":
            cagr_pct = result["cagr"] * 100

            st.metric(
                label="年复合增长率 CAGR",
                value=f"{cagr_pct:.2f}%"
            )

        # 负转正显示
        elif result["method"] == "负转正（线性假设）":
            st.write(f"每年绝对增加额：`{result['annual_increment']:.4f}`")

            if result["first_positive_year"] is not None:
                st.write(f"现金流首次转正年份：**第 {result['first_positive_year']} 年末**")
                st.write(f"转正时数值：`{result['first_positive_value']:.4f}`")

                if result["cagr"] is not None:
                    st.write(f"转正后剩余年数：`{result['remaining_years']}`")

                    st.metric(
                        label="后段年复合增长率",
                        value=f"{result['cagr'] * 100:.2f}%"
                    )
                else:
                    st.warning(result["message"])
            else:
                st.error(result["message"])

    except ValueError as e:
        st.error(f"计算错误：{e}")

else:
    st.info("请输入数据后点击计算。")




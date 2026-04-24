import matplotlib
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from data_processor import load_and_process_data, get_subject_groups

matplotlib.rcParams['font.sans-serif'] = [
    'SimHei',
    'Microsoft YaHei',
    'sans-serif'
]
matplotlib.rcParams['axes.unicode_minus'] = False

st.set_page_config(
    page_title="超文本阅读认知评估可视化系统",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("<h1 style='font-size: 1.8rem; margin-bottom: 0.3rem;'>超文本阅读认知评估可视化系统</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size: 0.85rem; color: #666; margin-top: 0;'>
系统说明：本系统基于行为实验与主观量表数据，可视化呈现用户在超文本阅读任务中的多维认知表现。
</p>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    return load_and_process_data()


data = load_data()
subject_groups = get_subject_groups(data)

# ========== 侧边栏 ==========
with st.sidebar:
    st.header("筛选条件")

    nav_options = ["全部", "主动", "静态"]
    selected_nav = st.selectbox("导航辅助方式", nav_options)

    text_options = ["全部", "冲突", "无冲突"]
    selected_text = st.selectbox("文本类型", text_options)

    # 根据筛选条件过滤参与者
    filtered_subjects = []
    for sid in data.keys():
        info = subject_groups.get(sid, {})
        if selected_nav != "全部" and info.get("nav_type") != selected_nav:
            continue
        if selected_text != "全部" and info.get("text_type") != selected_text:
            continue
        filtered_subjects.append(sid)

    if not filtered_subjects:
        st.warning("没有符合条件的参与者，请调整筛选条件")
        selected_subject = None
    else:
        selected_subject = st.selectbox("选择参与者", filtered_subjects)

    if selected_subject:
        info = subject_groups.get(selected_subject, {})
        st.divider()
        st.subheader("参与者信息")
        st.write(f"**编号**: {selected_subject}")
        st.write(f"**实验组别**: {info.get('group', '未知')}")
        st.write(f"**导航方式**: {info.get('nav_type', '未知')}")
        st.write(f"**文本条件**: {info.get('text_type', '未知')}")

    st.sidebar.markdown("""
    ---
    **使用说明**：
    1. 在侧边栏选择导航辅助方式和文本类型进行筛选
    2. 选择特定参与者查看详细数据
    3. 主视图显示参与者的五维度雷达图
    4. 点击标签页查看各维度详细指标
    """)


# ========== 主视图 ==========
if selected_subject is None:
    st.info("请在侧边栏选择参与者")
    st.stop()

subject_data = data.get(selected_subject, {})

# 左右分栏：左侧雷达图，右侧指标概览
left_col, right_col = st.columns([1, 1.2])

with left_col:
    def plot_radar_chart(subject_data):
        dimensions = ["信息定位", "阅读流畅", "冲突检测", "认知负荷", "知识迁移"]
        scores = [
            subject_data.get("信息定位", 0),
            subject_data.get("阅读流畅", 0),
            subject_data.get("冲突检测", 0),
            subject_data.get("认知负荷", 0),
            subject_data.get("知识迁移", 0)
        ]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        fig.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.15)

        angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
        angles += angles[:1]
        scores_plot = scores + scores[:1]

        ax.plot(angles, scores_plot, 'o-', linewidth=2, color='#1f77b4')
        ax.fill(angles, scores_plot, alpha=0.25, color='#1f77b4')

        ax.set_xticks(angles[:-1])
        ax.set_thetagrids(np.degrees(angles[:-1]), dimensions, fontsize=10)
        ax.tick_params(axis='x', pad=15)

        ax.set_ylim(0, 10)
        ax.set_yticks([2, 4, 6, 8, 10])
        ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=8, color='gray')
        ax.grid(True, linestyle='--', alpha=0.5)

        st.pyplot(fig)

    plot_radar_chart(subject_data)

with right_col:
    st.subheader("维度得分概览")
    cols = st.columns(3)

    dim_info = [
        ("信息定位", " "),
        ("阅读流畅", " "),
        ("冲突检测", " "),
        ("认知负荷", " "),
        ("知识迁移", " "),
    ]

    for idx, (dim, icon) in enumerate(dim_info):
        with cols[idx % 3]:
            score = subject_data.get(dim, 0)
            if dim == "冲突检测" and subject_data.get("冲突检测", 0) == 0:
                st.metric(label=f"{icon} {dim}", value="—", help="无冲突文本条件，未进行冲突检测任务")
            else:
                delta_color = "normal"
                if score >= 8:
                    delta_color = "inverse"
                elif score < 4:
                    delta_color = "off"
                st.metric(label=f"{icon} {dim}", value=f"{score:.1f}")

    st.divider()
    st.caption("评分说明：各维度满分10分，分数越高代表该维度表现越优")
    st.caption("（认知负荷维度分数越高表示主观负荷越低）")

# ========== 详细数据标签页 ==========
st.subheader("详细指标数据")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["信息定位", "阅读流畅", "冲突检测", "认知负荷", "知识迁移"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("综合得分", f"{subject_data.get('信息定位', 0):.2f}")
    c2.metric("首次导航区注视时间", f"{subject_data.get('首次导航区注视时间（ms）', 0):.0f} ms")
    c3.metric("导航区注视比例", f"{subject_data.get('导航区注视比例', 0):.4f}")
    st.metric("总页面访问次数", f"{subject_data.get('总页面访问次数', 0):.0f}")

with tab2:
    c1, c2, c3 = st.columns(3)
    c1.metric("综合得分", f"{subject_data.get('阅读流畅', 0):.2f}")
    c2.metric("总阅读时间", f"{subject_data.get('总阅读时间', 0):.0f} ms")
    c3.metric("总页面访问次数", f"{subject_data.get('总页面访问次数', 0):.0f}")

with tab3:
    if subject_data.get("冲突检测", 0) == 0:
        st.info("该参与者属于**无冲突文本条件**，未进行冲突检测任务。")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("综合得分", f"{subject_data.get('冲突检测', 0):.2f}")
        c2.metric("冲突标记正确率", f"{subject_data.get('冲突标记正确率', 0):.2%}")
        c3.metric("平均点击反应时", f"{subject_data.get('平均点击反应时', 0):.0f} ms")

with tab4:
    c1, c2, c3 = st.columns(3)
    c1.metric("综合得分", f"{subject_data.get('认知负荷', 0):.2f}")
    c2.metric("脑力需求", f"{subject_data.get('脑力需求', 0):.1f}")
    c3.metric("体力需求", f"{subject_data.get('体力需求', 0):.1f}")
    c4, c5, c6 = st.columns(3)
    c4.metric("时间需求", f"{subject_data.get('时间需求', 0):.1f}")
    c5.metric("努力程度", f"{subject_data.get('努力程度', 0):.1f}")
    c6.metric("业绩水平", f"{subject_data.get('业绩水平', 0):.1f}")
    c7, c8 = st.columns(2)
    c7.metric("受挫程度", f"{subject_data.get('受挫程度', 0):.1f}")
    c8.metric("认知负荷程度", f"{subject_data.get('认知负荷程度', 0):.2f}")

with tab5:
    c1, c2, c3 = st.columns(3)
    c1.metric("综合得分", f"{subject_data.get('知识迁移', 0):.2f}")
    c2.metric("选择题正确率", f"{subject_data.get('选择题正确率', 0):.0%}")
    c3.metric("人工评分均值", f"{(subject_data.get('人工评分1', 0) + subject_data.get('人工评分2', 0)) / 2:.1f}")
    c4, c5 = st.columns(2)
    c4.metric("人工评分1", f"{subject_data.get('人工评分1', 0):.1f}")
    c5.metric("人工评分2", f"{subject_data.get('人工评分2', 0):.1f}")
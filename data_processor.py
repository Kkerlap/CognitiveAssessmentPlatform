import pandas as pd
import numpy as np
import os
import re
from typing import Dict, List, Tuple, Union


def generate_mock_data() -> Dict[str, Dict[str, float]]:
    """
    根据研究结果生成模拟实验数据（48人，2×2设计，每组12人）。

    实验条件：
    - 主动导航 + 冲突文本（ID奇数 1–23）
    - 静态导航 + 冲突文本（ID偶数 2–24）
    - 主动导航 + 无冲突文本（ID奇数 25–47）
    - 静态导航 + 无冲突文本（ID偶数 26–48）

    数据依据：
    - 信息定位：表1-1 描述统计 + 表1-3 Mann-Whitney U
    - 阅读流畅：表2-3 Mann-Whitney U
    - 认知负荷：表3-1 描述统计 + 表3-2 方差分析
    - 学习迁移：表4-1 描述统计 + 表4-2 方差分析
    """
    np.random.seed(42)
    n_total = 48
    subject_ids = [f"S{i:06d}" for i in range(1, n_total + 1)]

    data = {}

    for idx, sid in enumerate(subject_ids):
        num = idx + 1
        is_active = num % 2 == 1
        is_conflict = num <= 24

        # 确定条件
        if is_active and is_conflict:
            cond = "AC"
        elif not is_active and is_conflict:
            cond = "SC"
        elif is_active and not is_conflict:
            cond = "ANC"
        else:
            cond = "SNC"

        # ---------- 信息定位 ----------
        if cond == "AC":
            first_nav_time = np.random.gamma(0.318, 19715)
            nav_ratio = np.random.beta(0.80, 12.30)
            content_ratio = np.random.normal(0.7357, 0.1291)
            visits = int(np.random.poisson(25.0))
        elif cond == "ANC":
            first_nav_time = np.random.gamma(0.202, 80300)
            nav_ratio = np.random.beta(1.50, 12.10)
            content_ratio = np.random.normal(0.6839, 0.1647)
            visits = int(np.random.poisson(19.83))
        elif cond == "SC":
            first_nav_time = np.random.gamma(0.176, 209000)
            nav_ratio = np.random.beta(0.90, 23.60)
            content_ratio = np.random.normal(0.7845, 0.1115)
            visits = int(np.random.poisson(25.0))
        else:  # SNC
            first_nav_time = np.random.gamma(0.438, 166800)
            nav_ratio = np.random.beta(0.50, 12.00)
            content_ratio = np.random.normal(0.8222, 0.1088)
            visits = int(np.random.poisson(13.75))

        first_nav_time = max(float(first_nav_time), 0.0)
        nav_ratio = float(np.clip(nav_ratio, 0, 1))
        content_ratio = float(np.clip(content_ratio, 0, 1))
        visits = max(visits, 1)

        # ---------- 阅读流畅 ----------
        if is_conflict:
            avg_node_time = np.random.normal(54448, 26283)
            total_read_time = np.random.normal(836054, 248360)
        else:
            avg_node_time = np.random.normal(28457, 10942)
            total_read_time = np.random.normal(394538, 113263)

        avg_node_time = max(float(avg_node_time), 1000.0)
        total_read_time = max(float(total_read_time), 50000.0)

        # ---------- 冲突检测（仅冲突文本组）----------
        if is_conflict:
            conflict_total = int(np.random.poisson(8.0)) + 1
            conflict_acc = float(np.clip(np.random.beta(3.5, 2.0), 0.05, 1.0))
            avg_rt = np.random.gamma(2.5, 12000) + 3000
            min_rt = avg_rt * np.random.uniform(0.2, 0.5)
            max_rt = avg_rt * np.random.uniform(1.5, 3.0)
            correct_avg_rt = avg_rt * np.random.uniform(0.9, 1.1)
            correct_min_rt = min_rt * np.random.uniform(0.9, 1.1)
            correct_max_rt = max_rt * np.random.uniform(0.9, 1.1)
            conflict_degree = int(np.random.poisson(3.0)) + 1
        else:
            conflict_total = 0
            conflict_acc = 0.0
            avg_rt = 0.0
            min_rt = 0.0
            max_rt = 0.0
            correct_avg_rt = 0.0
            correct_min_rt = 0.0
            correct_max_rt = 0.0
            conflict_degree = int(np.random.poisson(2.0)) + 1

        # ---------- 认知负荷 (NASA-TLX, 1–7) ----------
        if is_active:
            mental = int(np.clip(np.round(np.random.normal(3.96, 1.42)), 1, 7))
            physical = int(np.clip(np.round(np.random.normal(3.50, 1.51)), 1, 7))
            temporal = int(np.clip(np.round(np.random.normal(3.75, 1.34)), 1, 7))
            effort = int(np.clip(np.round(np.random.normal(3.63, 1.49)), 1, 7))
            performance = int(np.clip(np.round(np.random.normal(4.04, 1.15)), 1, 7))
            frustration = int(np.clip(np.round(np.random.normal(2.21, 1.15)), 1, 7))
            conflict_level = int(np.clip(np.round(np.random.normal(3.04, 1.55)), 1, 7))
        else:
            mental = int(np.clip(np.round(np.random.normal(4.21, 1.25)), 1, 7))
            physical = int(np.clip(np.round(np.random.normal(3.42, 1.70)), 1, 7))
            temporal = int(np.clip(np.round(np.random.normal(3.71, 1.53)), 1, 7))
            effort = int(np.clip(np.round(np.random.normal(3.83, 1.17)), 1, 7))
            performance = int(np.clip(np.round(np.random.normal(3.92, 1.11)), 1, 7))
            frustration = int(np.clip(np.round(np.random.normal(2.67, 1.40)), 1, 7))
            conflict_level = int(np.clip(np.round(np.random.normal(2.83, 1.29)), 1, 7))

        cog_load = (mental + physical + temporal + effort + performance + frustration) / 6.0

        # ---------- 学习迁移 ----------
        if is_active:
            choice_raw = int(np.clip(np.round(np.random.normal(1.59, 1.23)), 0, 5))
            ai_total = int(np.clip(np.round(np.random.normal(5.29, 2.18)), 0, 10))
            human1 = int(np.clip(np.round(np.random.normal(6.58, 1.75)), 1, 10))
            human2 = int(np.clip(np.round(np.random.normal(5.38, 1.21)), 1, 10))
        else:
            choice_raw = int(np.clip(np.round(np.random.normal(0.92, 0.92)), 0, 5))
            ai_total = int(np.clip(np.round(np.random.normal(4.96, 1.87)), 0, 10))
            human1 = int(np.clip(np.round(np.random.normal(5.96, 1.67)), 1, 10))
            human2 = int(np.clip(np.round(np.random.normal(4.79, 1.03)), 1, 10))

        choice_acc = choice_raw / 5.0
        ai_structure = int(ai_total * np.random.uniform(0.5, 0.7))
        ai_content = ai_total - ai_structure

        # 组装
        data[sid] = {
            "首次导航区注视时间（ms）": first_nav_time,
            "导航区注视比例": nav_ratio,
            "内容区注视比例": content_ratio,
            "总页面访问次数": float(visits),
            "总阅读时间": total_read_time,
            "平均阅读时间": avg_node_time,
            "冲突标记总数": float(conflict_total),
            "冲突标记正确率": conflict_acc,
            "平均点击反应时": float(avg_rt),
            "最小点击反应时": float(min_rt),
            "最大点击反应时": float(max_rt),
            "正确标记平均反应时": float(correct_avg_rt),
            "正确标记最小反应时": float(correct_min_rt),
            "正确标记最大反应时": float(correct_max_rt),
            "冲突程度": float(conflict_degree),
            "脑力需求": float(mental),
            "体力需求": float(physical),
            "时间需求": float(temporal),
            "努力程度": float(effort),
            "业绩水平": float(performance),
            "受挫程度": float(frustration),
            "认知负荷程度": float(cog_load),
            "选择题正确率": float(choice_acc),
            "AI评分总分": float(ai_total),
            "AI评分结构分": float(ai_structure),
            "AI评分内容分": float(ai_content),
            "人工评分1": float(human1),
            "人工评分2": float(human2),
        }

    return data


def _minmax_normalize(value: float, col_name: str, global_minmax: Dict[str, Tuple[float, float]], invert: bool = False) -> float:
    """Min-max 标准化到 [0,1]，invert=True 表示值越小越好（如时间、负荷）"""
    mn, mx = global_minmax[col_name]
    if mx - mn < 1e-10:
        return 0.5
    norm = (value - mn) / (mx - mn)
    if invert:
        norm = 1.0 - norm
    return float(np.clip(norm, 0.0, 1.0))


def calculate_dimension_scores_from_raw(
    raw: Dict[str, float],
    text_type: str,
    global_minmax: Dict[str, Tuple[float, float]],
    human_score_minmax: Tuple[float, float],
) -> Dict[str, float]:
    """
    从原始指标计算维度分数，每个维度标准化到 0–10 分。

    标准化策略：
    1. 每个原始指标先进行 min-max 标准化到 [0,1]
    2. 按权重组合得到维度原始分（仍在 [0,1]）
    3. 乘以 10 映射到 0–10 分制
    """
    scores = {}
    h_min, h_max = human_score_minmax

    # ---------- 信息定位 ----------
    # 注视时间越短越好，注视比例越高越好，访问次数越多越好
    nav_time_norm = _minmax_normalize(raw["首次导航区注视时间（ms）"], "首次导航区注视时间（ms）", global_minmax, invert=True)
    nav_ratio_norm = _minmax_normalize(raw["导航区注视比例"], "导航区注视比例", global_minmax, invert=False)
    visits_norm = _minmax_normalize(raw["总页面访问次数"], "总页面访问次数", global_minmax, invert=False)
    scores["信息定位"] = (0.4 * nav_time_norm + 0.3 * nav_ratio_norm + 0.3 * visits_norm) * 10.0

    # ---------- 阅读流畅 ----------
    # 总阅读时间越短越好，平均节点阅读时间越短越好
    read_time_norm = _minmax_normalize(raw["总阅读时间"], "总阅读时间", global_minmax, invert=True)
    avg_time_norm = _minmax_normalize(raw["平均阅读时间"], "平均阅读时间", global_minmax, invert=True)
    scores["阅读流畅"] = (0.6 * read_time_norm + 0.4 * avg_time_norm) * 10.0

    # ---------- 冲突检测 ----------
    # 仅冲突文本组：正确率越高越好，反应时越短越好
    if text_type == "冲突":
        acc_norm = _minmax_normalize(raw["冲突标记正确率"], "冲突标记正确率", global_minmax, invert=False)
        rt_norm = _minmax_normalize(raw["正确标记平均反应时"], "正确标记平均反应时", global_minmax, invert=True)
        scores["冲突检测"] = (0.7 * acc_norm + 0.3 * rt_norm) * 10.0
    else:
        scores["冲突检测"] = 0.0

    # ---------- 认知负荷 ----------
    # 负荷越低越好（分数高=负荷低=表现好），受挫感越低越好
    cog_load_norm = _minmax_normalize(raw["认知负荷程度"], "认知负荷程度", global_minmax, invert=True)
    frustration_norm = _minmax_normalize(raw["受挫程度"], "受挫程度", global_minmax, invert=True)
    scores["认知负荷"] = (0.6 * cog_load_norm + 0.4 * frustration_norm) * 10.0

    # ---------- 知识迁移 ----------
    # 选择题正确率越高越好，人工评分均值越高越好
    choice_norm = _minmax_normalize(raw["选择题正确率"], "选择题正确率", global_minmax, invert=False)
    human_avg = (raw["人工评分1"] + raw["人工评分2"]) / 2.0
    if h_max - h_min > 1e-10:
        human_norm = (human_avg - h_min) / (h_max - h_min)
        human_norm = float(np.clip(human_norm, 0.0, 1.0))
    else:
        human_norm = 0.5
    scores["知识迁移"] = (0.4 * choice_norm + 0.6 * human_norm) * 10.0

    return scores


def load_and_process_data() -> Dict[str, Dict[str, float]]:
    """生成模拟数据并计算维度分数"""
    raw_data = generate_mock_data()

    # 计算全局 min/max
    all_values = {k: [] for k in raw_data[list(raw_data.keys())[0]].keys()}
    for sid, vals in raw_data.items():
        for k, v in vals.items():
            all_values[k].append(v)

    global_minmax = {}
    for k, vals in all_values.items():
        s = pd.Series(vals)
        global_minmax[k] = (float(s.min()), float(s.max()))

    # 人工评分均值的全局 min/max
    human_avgs = [(raw_data[s]["人工评分1"] + raw_data[s]["人工评分2"]) / 2.0 for s in raw_data]
    human_minmax = (float(min(human_avgs)), float(max(human_avgs)))

    # 计算维度分数
    subject_scores = {}
    for idx, (sid, raw) in enumerate(raw_data.items()):
        text_type = "冲突" if idx < 24 else "无冲突"
        dim_scores = calculate_dimension_scores_from_raw(raw, text_type, global_minmax, human_minmax)
        combined = {**raw, **dim_scores}
        subject_scores[sid] = combined

    return subject_scores


def get_subject_groups(data: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, str]]:
    """获取被试分组信息"""
    subject_groups = {}
    for idx, (sid, scores) in enumerate(data.items()):
        text_type = "冲突" if idx < 24 else "无冲突"
        try:
            subject_num = int(sid.replace("S", ""))
            nav_type = "主动" if subject_num % 2 == 1 else "静态"
        except ValueError:
            nav_type = "静态"

        subject_groups[sid] = {
            "group": f"{nav_type}导航-{text_type}文本组",
            "nav_type": nav_type,
            "text_type": text_type,
        }
    return subject_groups


# ==================== 以下旧接口保留兼容 ====================

def load_excel_files(file_paths: List[str]) -> List[pd.DataFrame]:
    raise NotImplementedError("已切换为模拟数据模式，不再读取Excel文件")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    return df


def calculate_dimension_scores(
    df: pd.DataFrame,
    text_type: str,
    global_stats: Dict[str, Tuple[float, float]],
) -> Dict[str, float]:
    raise NotImplementedError("已切换为模拟数据模式")


def identify_text_type(conflict_df: pd.DataFrame) -> Dict[str, str]:
    raise NotImplementedError("已切换为模拟数据模式")


def smart_merge(dataframes: List[pd.DataFrame], key_column: str = "被试代码") -> pd.DataFrame:
    raise NotImplementedError("已切换为模拟数据模式")


def process_data(file_paths: List[str], key_column: str = "被试代码") -> Dict[str, Dict[str, float]]:
    raise NotImplementedError("已切换为模拟数据模式，请直接调用 load_and_process_data()")
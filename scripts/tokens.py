"""Design tokens：本仓库一切视觉数值的唯一权威源。

语义与取值理由见 DESIGN.md。改动 token 后必须重跑
    python3 scripts/render_header.py
以再生成 assets/ 下的 header。
"""

TOKENS = {
    # 画布与文字：取 GitHub 明暗主题原生色系，与页面融合
    "bg_dark": "#0d1117", "bg_light": "#ffffff",
    "ink_dark": "#c9d1d9", "ink_light": "#1f2328",
    "muted_dark": "#8b949e", "muted_light": "#57606a",
    "grid_dark": "#30363d", "grid_light": "#d0d7de",

    # 唯一强调色：雷达磷光绿（题材依据：ATC 雷达屏）；亮底用深绿保证对比度
    "accent_dark": "#3fb950", "accent_light": "#1a7f37",

    # 飞行类别语义色，绑定 FAA 标准阈值（阈值实现在 render_metar.py:flight_category）
    "vfr_dark": "#3fb950", "mvfr_dark": "#58a6ff",
    "ifr_dark": "#f85149", "lifr_dark": "#db61a2",
    "vfr_light": "#1a7f37", "mvfr_light": "#0969da",
    "ifr_light": "#cf222e", "lifr_light": "#bf3989",

    # 图表序列色：两条数据线需要两个可区分色相，非装饰
    "series_temp_dark": "#d29922", "series_temp_light": "#9a6700",
    "series_wind_dark": "#58a6ff", "series_wind_light": "#0969da",

    # 字体与字阶（12px 为硬下限；SVG 作 <img> 加载不得引外部字体）
    "font_mono": "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace",
    "fs_sm": 12, "fs_md": 14, "fs_lg": 20, "fs_xl": 36,

    # 几何与动效
    "space": 8, "radius": 6, "stroke": 1.5,
    "sweep_period_s": 8,
}


def theme(mode):
    """按 dark / light 取主题色子集。"""
    return {
        "bg": TOKENS[f"bg_{mode}"],
        "ink": TOKENS[f"ink_{mode}"],
        "muted": TOKENS[f"muted_{mode}"],
        "grid": TOKENS[f"grid_{mode}"],
        "accent": TOKENS[f"accent_{mode}"],
        "vfr": TOKENS[f"vfr_{mode}"],
        "mvfr": TOKENS[f"mvfr_{mode}"],
        "ifr": TOKENS[f"ifr_{mode}"],
        "lifr": TOKENS[f"lifr_{mode}"],
        "series_temp": TOKENS[f"series_temp_{mode}"],
        "series_wind": TOKENS[f"series_wind_{mode}"],
    }

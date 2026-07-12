# CLAUDE.md — qiaoqiaobby profile 仓库规范

## 定位

GitHub 个人主页仓库（README 即门面），**公开可见**：一切入库内容按公开标准书写，不出现私有仓名、内部排期、密钥。

## 目录约定

- `README.md`：门面本体。
- `assets/`：设计期生成的静态资产（header SVG），进 main；由 `scripts/render_header.py` 生成。
- `scripts/`：渲染脚本，Python 3 标准库 only，禁止引入第三方依赖。
- `.github/workflows/`：定时渲染任务。
- 机器生成物（METAR 卡、风温图、3D 贡献图、贡献蛇）只进 `output` 分支，由 workflow 提交，禁止手改 output 分支。
- 本地目录 `output/`（任务产物）、`mid/`（过程文件）、`dist/`（渲染中间产物）与 `ROADMAP.md` 已 gitignore，不提交。

## 视觉纪律

一切视觉数值出自 `scripts/tokens.py` 的 `TOKENS`；细则、宣读定稿与预检清单见 `DESIGN.md`。改 token 后必须重跑 `python3 scripts/render_header.py` 同步 assets/。

## workflow 清单

| workflow | cron (UTC) | 产物（output 分支） |
|---|---|---|
| metar.yml | `17 * * * *` | metar-zbaa-{dark,light}.svg |
| wind.yml | `13 21 * * *` | wind-beijing-{dark,light}.svg |
| contrib-3d.yml | `29 19 * * *` | contrib-3d-{dark,light}.svg |
| snake.yml | `47 0 * * *` | github-contribution-grid-snake{,-dark}.svg |

统一部署模式：渲染到 dist/ → clone output 分支增量 commit（有 diff 才提交，push 冲突 rebase 重试一次）。cron 分钟已互相错开，禁止改回整点或改用替换式部署（ghaction-github-pages 会清空分支上其他产物）。渲染脚本失败以非零码退出且不产文件，旧卡自然保留——卡内 UTC 时间戳即数据年龄。

## 已知事项

- 公开仓 60 天无 commit 会自动停用 scheduled workflow；本仓有每日 bot 提交，实际风险低。
- Open-Meteo 数据为 CC-BY 4.0：卡内 footer 与 README fine print 双署名，不可移除。
- output 分支年增数千个小 commit 属预期，可选每年用 orphan 分支重建瘦身（高风险操作，先问）。

## 红线

- push 与一切账号侧操作（pin、仓库描述、侧栏资料、转公开）先获用户明确授权。
- 不虚构数据；私有项目不得表述为开源；fork 不得标为自研。

# GitHub 极客终端主页使用指南

本项目会每天通过 GitHub Actions 自动拉取你的最新 GitHub 数据（近一年提交数、总 Stars、仓库数、账号年限、置顶/高星代表项目、53 周贡献热力矩阵），渲染出深浅色自适应的 **Neofetch 终端风 SVG 主页**。

## 1. 创建同名特殊仓库

1. 在 GitHub 点击右上角 `+` -> `New repository`。
2. **Repository name** 填写与你的 GitHub 用户名**完全一致**的名称（例如用户名是 `alice`，就建 `alice/alice`）。
3. 保持仓库为 **Public**，将本目录中的所有文件上传/推送到该仓库的默认分支（`main` 或 `master`）。

## 2. 修改个人信息

打开 `profile.config.json`，按需修改以下字段：

```json
{
  "username": "你的GitHub用户名",
  "display_name": "终端里显示的名字",
  "tagline": "一句简短的个人签名",
  "role": "职业定位（如 Systems & AI Engineer）",
  "stack": "主力技术栈（如 TypeScript · Go · Rust）",
  "focus": "当前专注方向",
  "location": "所在城市",
  "links": "个人网站 · 邮箱",
  "ascii_art": "alpine"
}
```

### 切换内置 ASCII 字符画

`ascii_art` 支持三个极简暗夜风内置预设：
- `"alpine"`：星空几何山峰（默认）
- `"prism"`：线框棱镜八面体
- `"orbit"`：星环轨道遥测图
- `"custom"`：配合 `custom_ascii` 数组传入最多 13 行自定义等宽字符画

## 3. 启用自动更新

1. 推送代码后，进入仓库的 **Actions** 标签页，确保 Workflows 已启用。
2. 也可在 Actions 中点击 **Update Terminal Profile** -> **Run workflow** 立即手动触发一次同步。

### （可选）包含私有仓库贡献统计

默认使用仓库自带的 `GITHUB_TOKEN`，仅统计公开仓库提交与公开仓库 Stars。如果你希望热力图和 `COMMITS (1Y)` 包含私有仓库贡献：

1. 打开 GitHub 右上角头像 -> **Settings** -> **Developer settings** -> **Personal access tokens** -> **Tokens (classic)**。
2. 生成一个新 Token，勾选 `read:user` 与 `repo` 权限。
3. 回到你的同名仓库 -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**。
4. Name 填 `PROFILE_TOKEN`，Value 粘贴刚才生成的 Token。

## 4. 本地预览测试

无需配置任何依赖，使用 Python 3 即可生成演示预览图：

```bash
python3 scripts/generate.py --demo
```

如果本地环境变量设置了 `GITHUB_TOKEN`，也可以直接拉取真实数据生成：

```bash
GITHUB_TOKEN=你的token GITHUB_USERNAME=你的用户名 python3 scripts/generate.py
```

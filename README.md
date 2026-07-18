# 📜 古风取名软件 — Gufeng Naming Tool

[![Version](https://img.shields.io/badge/version-v3.2-8b6f47)](https://github.com/toobey521/gufeng-naming-tool/releases)

3206字库 + 八字命理 + 五维评分体系的智能取名工具，纯本地运行，无需联网。

## 功能

- 🏯 **3206字字库**：完整汉字数据库，含拼音/笔画/五行/字义/结构/标签
- 📐 **五维评分**：五行命理(35) + 诗文出处(20) + 音律读音(20) + 字义内涵(20) + 字形书写(15)
- 🔮 **八字排盘**：根据出生年月日时推算八字、五行旺衰、喜用神
- 📖 **诗文出处**：20907个名字对，源自诗经、楚辞、唐诗宋词等经典文献
- 🔧 **固定字筛选**：支持固定中间字或末尾字，适合辈分字
- ⚧ **性别区分**：男/女/中性分类，精准筛选
- 🧩 **23.9万篇诗文库**：完整文学数据库，出处可查

## 快速开始

1. 从 [Releases](https://github.com/toobey521/gufeng-naming-tool/releases) 下载最新版
2. 双击运行 exe
3. 浏览器自动打开 http://localhost:5592
4. 输入姓氏和出生信息
5. 点击「开始取名」

## 评分维度

| 维度 | 满分 | 说明 |
|------|------|------|
| 🏯 五行命理 | 35 | 八字喜用神匹配、五行相生 |
| 📖 诗文出处 | 20 | 源自经典文献的质量和数量 |
| 🎵 音律读音 | 20 | 声调搭配、发音流畅度 |
| 📝 字义内涵 | 20 | 寓意美好、正向含义 |
| ✍️ 字形书写 | 15 | 笔画协调、结构搭配 |
| **总分** | **110 → 100** | 百分比转换显示 |

## 技术栈

- 后端: Python Flask
- 前端: 原生 HTML/CSS/JS
- 数据: Unicode Unihan + chinese-poetry 数据集
- 打包: PyInstaller

## 数据来源

- **汉字数据**: Unicode 官方 Unihan 数据库 (unicode.org)
- **诗文数据**: chinese-poetry 数据集 (github.com/chinese-poetry)
- **拼音**: pypinyin 库

## 隐私说明

所有数据在本地处理，不上传任何个人信息，无需联网。

## License

MIT License — Copyright © 2026 郭云宁

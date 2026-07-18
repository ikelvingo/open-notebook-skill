# 📓 Open Notebook Skill

`#skills` `#open-notebook` `#agent-skill`

通过 REST API 管理 [Open Notebook](https://github.com/lfnovo/open-notebook) 研究知识库的 Agent 技能。适用于 **Claude Code / Gemini CLI / Copilot CLI** agent 自动化。

## 环境要求

- Python 3.8+
- 已部署运行的 [Open Notebook](https://github.com/lfnovo/open-notebook) 实例

## 配置

```bash
export OPEN_NOTEBOOK_BASE_URL="http://localhost:8000"
export OPEN_NOTEBOOK_API_KEY="your-api-key"  # 可选
```

## 快速开始

```bash
# 列出笔记本
python open_notebook.py notebook list

# 创建笔记本
python open_notebook.py notebook create --name "研究项目"

# 采集网页
python open_notebook.py source create --type url --url "https://example.com" --notebook_id notebook:XXX

# 语义搜索
python open_notebook.py search query --query "agent 架构" --type vector
```

## 命令概览

```
notebook   list | get | create | update | delete | preview-delete | add-source | remove-source
source     list | get | create | update | delete | status | retry
note       list | get | create | update | delete
insight    list | get | create | delete | save-as-note
search     query
```

使用 `python open_notebook.py --help` 查看完整参数。

## 作者

ikelvingo — [github.com/ikelvingo/open-notebook-skill](https://github.com/ikelvingo/open-notebook-skill)

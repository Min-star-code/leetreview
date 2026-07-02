# LeetReview

LeetReview 是一个使用 Python 和 LLM API 开发的 LeetCode 刷题复盘工具。

用户提供题目信息和自己的代码后，LeetReview 会调用大语言模型分析解题思路、潜在误区、复杂度和知识点，并将结果保存为本地 Markdown 错题卡。

## 功能

- 读取题号、题名、题目描述和代码文件
- 支持 C、Python 等不同编程语言
- 调用 OpenAI Responses API 生成中文复盘
- 判断代码是否正确，不强行把正确代码当作错题
- 自动生成 Markdown 错题卡
- 记录创建日期和下次复习日期
- 提供不调用 LLM 的手动错题卡模式
- 使用 pytest 进行基础测试

## 工作流程

```text
题目描述 + 学生代码
        ↓
LeetReview 组成 Prompt
        ↓
OpenAI API 返回分析
        ↓
生成 Markdown 错题卡
        ↓
保存到 notebook/
```

## 环境要求

- Python 3.10 或更高版本
- OpenAI API Key
- 可访问 OpenAI API 的网络环境

## 安装

克隆项目并进入项目目录后，运行：

```bash
python3 -m pip install -e ".[dev]"
```

`-e` 表示以可编辑模式安装。修改源代码后，不需要重复安装项目。

## 配置 API Key

1. 在 [OpenAI API Keys](https://platform.openai.com/api-keys) 创建 API Key。
2. 将 `.env.example` 复制为 `.env`。
3. 在 `.env` 中填写真实 Key：

```dotenv
OPENAI_API_KEY=your_real_api_key
OPENAI_MODEL=gpt-5.4-mini
```

不要把真实 API Key 写进源代码，也不要提交 `.env`。项目的 `.gitignore` 已经忽略该文件。

检查 API 连接：

```bash
python3 -m leetreview.cli check-api
```

成功时会显示：

```text
LeetReview API connection successful
```

## 使用 LLM 分析代码

项目中包含 LeetCode 21 的示例题目描述和 C 语言代码：

```bash
python3 -m leetreview.cli analyze \
  --problem-id 21 \
  --title "Merge Two Sorted Lists" \
  --description-file examples/merge_two_sorted_lists.md \
  --code-file examples/merge_two_sorted_lists.c \
  --language c
```

生成的错题卡保存在：

```text
notebook/21-merge-two-sorted-lists.md
```

`notebook/` 默认不会提交到 Git，用户可以把它作为自己的私人错题本。

可以先查看项目中的[公开示例错题卡](examples/sample_review.md)，了解最终输出效果。

## 手动生成错题卡

不使用 LLM 时，也可以手动提供复盘内容：

```bash
python3 -m leetreview.cli new \
  --problem-id 1 \
  --title "Two Sum" \
  --code-file examples/two_sum_wrong.py \
  --language python \
  --mistake "使用了两层循环" \
  --better-approach "使用哈希表记录已经访问的数字" \
  --knowledge "hash map, complement search, time complexity"
```

## 运行测试

```bash
python3 -m pytest
```

## 项目结构

```text
.
├── examples/               # 示例题目和代码
├── src/leetreview/
│   ├── cli.py              # 命令行入口
│   ├── llm.py              # Prompt 和 OpenAI API 调用
│   └── notebook.py         # Markdown 错题卡生成
├── tests/                  # 自动测试
├── .env.example            # API 配置示例
├── .gitignore              # Git 忽略规则
├── pyproject.toml          # Python 项目配置
└── README.md
```

## 当前状态

项目目前处于 MVP 阶段，已经完成从代码输入、LLM 分析到 Markdown 保存的核心流程。

后续计划：

- 使用结构化输出提高分析结果的稳定性
- 增加更友好的交互式输入
- 支持错题检索和复习状态管理
- 添加 Web 界面

## 安全与费用

- API 请求可能产生费用，请在 OpenAI Platform 设置合理的使用额度。
- 不要公开 `.env`、API Key 或其他个人凭据。
- 提交代码前建议运行 `git status`，确认 `.env` 没有进入待提交列表。

## License

本项目使用 [MIT License](LICENSE)。

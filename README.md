# Qianxin Hunter MCP Server

一个用于查询 Qianxin Hunter 网络空间测绘平台（奇安信鹰图平台）的 MCP (Model Context Protocol) 服务器。

## 功能特性

- 🔍 **查询资产**: 支持按照语法进行资产查询
- 🗂️ **批量查询**: 支持批量 IP、Domain、Company 等查询，支持从本地上传批量查询文件
- 📤 **导出任务创建**: 支持创建导出任务（异步任务）
- 🔄 **导出进度查询**: 支持查询导出任务进度
- 📥 **导出文件下载**: 下载结果文件到本地
- ⚙️ **环境变量配置**: 通过环境变量配置 API-KEY、默认查询字段、默认导出字段、文件下载目录

## 安装 MCP Server

#### 使用 uvx 从 PyPI 下载安装 Mcp

```bash
uvx hunter-mcp
```

#### 使用 pip 从 PyPI 下载安装 Mcp

```bash
pip install hunter-mcp
#pip install --index-url https://pypi.org/simple hunter-mcp
```

#### 从 github 下载安装 Mcp，使用 pip 安装

```bash
git clone https://github.com/PiggyHurry/hunter-mcp.git
cd hunter-mcp
pip install .
# pip install -e . # Editable
#pip show hunter-mcp
```

## 配置 MCP Client

##### 简单快速配置（免先安装）

```json
{
  "mcpServers": {
    "hunter-mcp": {
      "command": "uvx",
      "args": [
        "hunter-mcp"
      ],
      "env": {
        "HUNTER_API_KEY": "xxx"
      }
    }
  }
}
```

##### 或（确保已安装）

```json
{
  "mcpServers": {
    "hunter-mcp": {
      "command": "uv",
      "args": [
        "run",
        "hunter-mcp"
      ],
      "env": {
        "HUNTER_API_KEY": "xxx"
      }
    }
  }
}
```

##### 配置环境变量

```json
{
  "mcpServers": {
    "hunter-mcp": {
      "command": "uvx",
      "args": [
        "hunter-mcp"
      ],
      "env": {
        "HUNTER_API_KEY": "xxx",
        "DEFAULT_SEARCH_FIELDS": "ip,port,domain",
        "DEFAULT_BATCH_FIELDS": "ip,port,domain",
        "DEFAULT_BATCH_SAVE_DIR": "/path/to/download/dir/"
      }
    }
  }
}
```

#### 环境变量说明

```text
DEFAULT_SEARCH_FIELDS: 检索接口默认返回字段。非必须。
DEFAULT_BATCH_FIELDS: 批量/导出接口默认返回字段。非必须。
DEFAULT_BATCH_SAVE_DIR: 导出文件默认下载目录。非必须。

hunter检索接口和批量/导出接口，默认返回权限内所有可导出字段。
对于检索接口，响应结果会直接返回给大模型，可能会导致模型token消耗过多。可在对话中指定字段，或者配置默认字段的环境变量，以降低token消耗。
    字段优先级：对话中指定字段 > 模型自主选择字段 > 环境变量默认配置字段 > 默认权限内所有字段
对于导出任务，下载接口返回的文件会保存到本地，然后仅将保存地址返回给大模型，不会造成模型token消耗过多。
    如无必要，不要让大模型分析下载后的文件，除非token用不完。
```

#### 获取 api-key

- 登录 [https://hunter.qianxin.com](https://hunter.qianxin.com) → 个人中心 → API管理

## MCP 工具说明

#### 1. Hunter 查询 (`hunter_search`)

**主要参数**:

- `search`: 查询语法（如`ip="1.1.1.1"`）
- `page`: 页码（默认 1）
- `page_size`: 每页资产条数（可选：10/50/100，默认 10）
- `start_time`: 开始时间（格式：YYYY-MM-DD）
- `end_time`: 结束时间（格式：YYYY-MM-DD）
- `is_web`: 资产类型，1代表”web资产“，2代表”非web资产“，3代表”全部“
- `status_code`: 状态码列表，以逗号分隔，如”200,401“
- `fields`: 返回字段

#### 2.1. Hunter 批量查询/导出 (`hunter_batch_task_create`)

**主要参数**:

- `search`: 查询语法（如`ip="1.1.1.1"`）
- `file_path`: 包含检索目标的本地 CSV 文件路径（与 search 二选一提供）。
- `start_time`: 开始时间（格式：YYYY-MM-DD）
- `end_time`: 结束时间（格式：YYYY-MM-DD）
- `is_web`: 资产类型，1代表”web资产“，2代表”非web资产“，3代表”全部“
- `status_code`: 状态码列表，以逗号分隔，如”200,401“
- `fields`: 返回字段
- `search_type`: 上传文件类型，枚举值：all、ip、domain、company
- `assets_limit`: 预期导出的资产数量（限制导出条数）

#### 2.2. Hunter 批量查询/导出进度查询 (`hunter_batch_task_progress`)

**主要参数**:

- `task_id`: 创建批量任务时返回的任务 ID。

#### 2.3. Hunter 批量查询/导出CSV结果下载 (`hunter_batch_task_result_download`)

**主要参数**:

- `task_id`: 创建批量任务时返回的任务 ID。
- `save_dir`: 可选。保存文件的目录。如果未提供，将尝试从环境变量里获取默认目录。
- `file_name`: 可选。保存的文件名。如果未提供，将尝试使用服务器返回的文件名。

## Hunter 语法简介

**匹配运算符**:

- `=` - 模糊查询，查询包含关键词的资产
- `==` - 精确查询，查询有且仅有关键词的资产
- `!=` - 模糊剔除，剔除包含关键词的资产。使用 `!=""` 可查询值不为空的情况
- `!==` - 精确剔除，剔除有且仅有关键词的资产

**逻辑运算符**:

- `&&` - 与（AND）
- `||` - 或（OR）
- `()` - 括号内表示查询优先级最高

**查询示例**:

```
# 模糊匹配
domain="example"
web.body="admin"

# 精确匹配
domain=="example.com"
web.title=="login"

# 模糊剔除
web.body!="admin"

# 精确剔除
domain!=="example.com"

# 查询值不为空
web.title!==""
is_domain="true"

# 逻辑 AND（&&）
ip="1.1.1.1" && is_domain="false"
domain="example.com" && header.status_code="200"

# 逻辑 OR（||）
domain="example.com" || domain="test.com"
web.title="admin" || web.title="login"

# 优先级控制
(web.title="admin" || web.title="login") && ip.tag="CDN"
```

## 使用案例（技巧）

```text
1、从Hunter查询 ip="1.1.1.1" && port=80 的测绘资产
预期：（1）Tool: hunter_search {search: "ip=\"1.1.1.1\" && port=80"}

2、从Hunter查询 ip="1.1.1.1" && port=53 的测绘资产，fields="ip,port,domain,banner"
预期：（1）Tool: hunter_search {search: "ip=\"1.1.1.1\" && port=53", fields="ip,port,domain,banner"}
注意：fields参数可省略，默认返回权限内所有字段。优先级：对话中指定字段 > 模型自主选择字段 > 环境变量默认配置字段 > 默认权限内所有字段

3、从Hunter查询 app="OpenClaw" 2026-03-10 更新的资产数量
预期：（1）Tool: hunter_search {search: "ip=\"1.1.1.1\" && port=53", start_time="2026-03-10", end_time="2026-03-10"}

4、从Hunter查询 app="OpenClaw" 从2026年3月5日到2026年3月10日之间的资产变化趋势，每个日期对应的资产数为该日期往前推一个月的资产。然后帮我整理一个该趋势变化的表格。接口限速2s一次。
预期：（1）Tool: hunter_search {search: "app=\"OpenClaw\"", start_time="2026-02-05", end_time="2026-03-05"}
     （2）Tool: hunter_search {search: "app=\"OpenClaw\"", start_time="2026-02-06", end_time="2026-03-06"}
     （3）Tool: hunter_search {search: "app=\"OpenClaw\"", start_time="2026-02-07", end_time="2026-03-07"}
     （4）Tool: hunter_search {search: "app=\"OpenClaw\"", start_time="2026-02-08", end_time="2026-03-08"}
     （5）Tool: hunter_search {search: "app=\"OpenClaw\"", start_time="2026-02-09", end_time="2026-03-09"}
     （6）Tool: hunter_search {search: "app=\"OpenClaw\"", start_time="2026-02-10", end_time="2026-03-10"}
注意：接口有限速，连续/并发调用工具可能会触发限速，请在对话中说明限速

5、从Hunter导出 app="OpenClaw" 2026-03-10 更新的资产
预期：（1）Tool: hunter_search_batch {search: "app=\"OpenClaw\"", start_time="2026-03-10", end_time="2026-03-10"}
     （2）Tool: hunter_search_batch_process {task_id: 123456}
     （.）Tool: hunter_search_batch_process {task_id: 123456} ... until process 100%
     （3）Tool: hunter_search_batch_download {task_id: 123456} ... until download finish
注意：若未在对话中说明下载目录，则尽量在环境变量中配置默认下载目录

6、从Hunter导出 app="OpenClaw" 2026-03-10 更新的资产，导出权限内所有可导出字段，保存到 /path 目录
预期：（1）Tool: hunter_search_batch {search: "app=\"OpenClaw\"", start_time="2026-03-10", end_time="2026-03-10", "fields":""}
     （2）Tool: hunter_search_batch_process {task_id: 123456}
     （.）Tool: hunter_search_batch_process {task_id: 123456} ... until process 100%
     （3）Tool: hunter_search_batch_download {task_id: 123456, save_dir="/path"} ... until download finish

7、从Hunter导出 /path/ip.csv 文件对应的测绘资产，导出类型选择ip，文件保存到 /path 目录
预期：（1）Tool: hunter_search_batch {file_path: "/path/ip.csv", search_type="ip"}
     （2）Tool: hunter_search_batch_process {task_id: 123456}
     （.）Tool: hunter_search_batch_process {task_id: 123456} ... until process 100%
     （3）Tool: hunter_search_batch_download {task_id: 123456, save_dir="/path"} ... until download finish
```

## Links
- **PyPI**: https://pypi.org/project/hunter-mcp
- **GitHub**: https://github.com/PiggyHurry/hunter-mcp
- **Hunter**: https://hunter.qianxin.com
- **Hunter-Help**: https://hunter.qianxin.com/home/helpCenter

## 许可证

[MIT License](LICENSE)
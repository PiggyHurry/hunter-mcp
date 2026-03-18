# Hunter MCP Server

一个用于查询 Hunter 网络空间测绘平台的 MCP (Model Context Protocol) 服务器。

## 功能特性

- 🔍 Hunter 查询: 支持奇安信鹰图平台的资产查询

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
#pip install -e . #Editable
#pip show hunter-mcp
```

## 配置 MCP Client

#### 配置 json

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

#### 获取 api-key

- 登录 https://hunter.qianxin.com → 个人中心 → API管理

## 功能说明

### Hunter 查询 (hunter_search)

**主要参数**:

- search: 搜索语法（如 'title="北京"'）
- page: 页码，默认为 1。
- page_size: 每页资产条数，默认为 10。
- start_time: 开始时间，格式为 YYYY-MM-DD（超出近30天将扣除积分）。
- end_time: 结束时间，格式为 YYYY-MM-DD（超出近30天将扣除积分）。
- is_web: 资产类型，1代表”web资产“，2代表”非web资产“，3代表”全部“。
- status_code: 状态码列表，以逗号分隔，如”200,401“。
- fields: 可选返回字段，以逗号分隔（如 ip,port,domain 等）。

## 许可证

[MIT License](LICENSE)
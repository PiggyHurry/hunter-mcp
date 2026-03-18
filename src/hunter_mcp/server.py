from mcp.server.fastmcp import FastMCP
import base64
import httpx
import os

mcp = FastMCP("hunter-mcp")


@mcp.tool()
async def hunter_search(
        search: str,
        page: int = 1,
        page_size: int = 10,
        start_time: str | None = None,
        end_time: str | None = None,
        is_web: int | None = None,
        status_code: str | None = None,
        fields: str | None = None
):
    """
    使用 Hunter 语法查询网络空间测绘数据。
    
    Args:
        search: 搜索语法（如 'title="北京"'），程序会自动进行 base64url 编码处理。
        page: 页码，默认为 1。
        page_size: 每页资产条数，默认为 10。
        start_time: 开始时间，格式为 YYYY-MM-DD（超出近30天将扣除积分）。
        end_time: 结束时间，格式为 YYYY-MM-DD（超出近30天将扣除积分）。
        is_web: 资产类型，1代表”web资产“，2代表”非web资产“，3代表”全部“。
        status_code: 状态码列表，以逗号分隔，如”200,401“。
        fields: 可选返回字段，以逗号分隔（如 ip,port,domain 等）。
    """

    api_key = os.getenv("HUNTER_API_KEY")
    if not api_key:
        raise RuntimeError("HUNTER_API_KEY environment variable not set")

    url = "https://hunter.qianxin.com/openApi/search"

    encode_search = base64.urlsafe_b64encode(search.encode()).decode()

    params = {
        "api-key": api_key,
        "search": encode_search,
        "page": page,
        "page_size": page_size
    }

    if start_time: params["start_time"] = start_time
    if end_time: params["end_time"] = end_time
    if is_web: params["is_web"] = is_web
    if status_code: params["status_code"] = status_code
    if fields: params["fields"] = fields

    async with httpx.AsyncClient(timeout=50) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            return f"网络错误: {str(e)}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()

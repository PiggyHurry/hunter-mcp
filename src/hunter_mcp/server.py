from fastmcp import FastMCP
import base64
import httpx
import os
import re

mcp = FastMCP("hunter-mcp")


def get_api_key():
    """获取并校验 API KEY"""
    api_key = os.environ.get("HUNTER_API_KEY")
    if not api_key:
        raise ValueError("未找到环境变量 HUNTER_API_KEY，请确保已配置。")
    return api_key


@mcp.tool()
async def hunter_search(
        search: str,
        page: int = 1,
        page_size: int = 10,
        start_time: str = None,
        end_time: str = None,
        is_web: int = None,
        status_code: str = None,
        fields: str = None
) -> str:
    """
    使用 Qianxin Hunter（奇安信鹰图平台）语法查询网络空间测绘数据（小批量实时查询）。若只关心资产数量，请设置 fields="ip,port,domain"，page_size=1。

    Args:
        search: 搜索语法（如 'title="北京"'），程序会自动进行 base64url 编码处理。
        page: 页码，默认为 1。
        page_size: 每页资产条数，默认为 10。可选：1/10/50/100。
        start_time: 开始时间，格式为 YYYY-MM-DD（超出近30天将扣除积分）。
        end_time: 结束时间，格式为 YYYY-MM-DD（超出近30天将扣除积分）。
        is_web: 资产类型，1代表”web资产“，2代表”非web资产“，3代表”全部“，默认"全部"。
        status_code: 状态码列表，以逗号分隔，如”200,401“。
        fields: 可选返回字段，以逗号分隔（如 "ip,port,domain"）。默认为空代表选择权限内所有可导出字段。可选字段枚举: ip,port,domain,ip_tag,url,web_title,is_risk_protocol,protocol,base_protocol,status_code,os,company,number,icp_exception,country,province,city,is_web,isp,as_org,cert_sha256,ssl_certificate,component,asset_tag,updated_at,header,header_server,banner,whois,body,vul_list
    """

    try:
        api_key = get_api_key()
    except ValueError as e:
        return f"错误: {e}"

    # 逻辑：优先使用传入的 fields，否则使用环境变量 DEFAULT_SEARCH_FIELDS
    fields = fields or os.environ.get("DEFAULT_SEARCH_FIELDS")

    search_encoded = base64.urlsafe_b64encode(search.encode("utf-8")).decode("utf-8")
    url = "https://hunter.qianxin.com/openApi/search"

    params = {"api-key": api_key, "search": search_encoded, "page": page, "page_size": page_size}
    if start_time: params["start_time"] = start_time
    if end_time: params["end_time"] = end_time
    if is_web: params["is_web"] = is_web
    if status_code: params["status_code"] = status_code
    if fields: params["fields"] = fields

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            return f"网络错误: {str(e)}"


@mcp.tool()
async def hunter_batch_task_create(
        search: str = None,
        file_path: str = None,
        start_time: str = None,
        end_time: str = None,
        is_web: int = None,
        status_code: str = None,
        fields: str = None,
        search_type: str = "all",
        assets_limit: int = None
) -> str:
    """
    创建 Qianxin Hunter 批量查询任务，任务将以异步方式导出数据为csv。支持通过上传文件(file_path)对批量的ip/domain/company进行资产查询和结果导出，或通过搜索语法(search)进行资产查询和结果导出。成功调用后将返回 task_id，用于后续查询进度和下载文件。

    Args:
        search: 搜索语法（与 file_path 二选一提供）。
        file_path: 包含检索目标的本地 CSV 文件路径（与 search 二选一提供）。
        search_type: 上传文件的类型，枚举值：all、ip、domain、company，默认为all。
        assets_limit: 预期导出的资产数量。
        start_time: 开始时间，格式为 YYYY-MM-DD（超出近30天将扣除积分）。
        end_time: 结束时间，格式为 YYYY-MM-DD（超出近30天将扣除积分）。
        is_web: 资产类型，1代表”web资产“，2代表”非web资产“，3代表”全部“，默认"全部"。
        status_code: 状态码列表，以逗号分隔，如”200,401“。
        fields: 可选返回字段，以逗号分隔（如 ip,port,domain 等）。默认为空代表选择权限内所有可导出字段。可选字段枚举: ip,port,domain,ip_tag,url,web_title,is_risk_protocol,protocol,base_protocol,status_code,os,company,number,icp_exception,country,province,city,is_web,isp,as_org,cert_sha256,ssl_certificate,component,asset_tag,updated_at,header,header_server,banner,whois,body,vul_list
    """
    try:
        api_key = get_api_key()
    except ValueError as e:
        return f"错误: {e}"

    # 处理默认值
    fields = fields or os.environ.get("DEFAULT_BATCH_FIELDS")

    if not search and not file_path:
        return "错误: 必须提供 'search' (搜索语法) 或 'file_path' (文件路径) 中的一个。"

    url = "https://hunter.qianxin.com/openApi/search/batch"  #
    params = {"api-key": api_key}  #

    # 选填参数映射
    if start_time: params["start_time"] = start_time
    if end_time: params["end_time"] = end_time
    if is_web: params["is_web"] = is_web
    if status_code: params["status_code"] = status_code
    if fields: params["fields"] = fields
    if search_type: params["search_type"] = search_type
    if assets_limit: params["assets_limit"] = assets_limit

    async with httpx.AsyncClient() as client:
        try:
            if file_path:
                # 方式一：传文件
                if not os.path.exists(file_path):
                    return f"错误: 找不到文件 {file_path}"
                with open(file_path, "rb") as f:
                    files = {"file": (os.path.basename(file_path), f, "text/csv")}
                    response = await client.post(url, params=params, files=files)
            else:
                # 方式二：传语法
                search_encoded = base64.urlsafe_b64encode(search.encode("utf-8")).decode("utf-8")  #
                params["search"] = search_encoded  #
                response = await client.post(url, params=params)  #

            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            return f"创建批量任务时发生网络错误: {str(e)}"


@mcp.tool()
async def hunter_batch_task_progress(task_id: int) -> str:
    """
    查看 Qianxin Hunter 批量查询任务的执行进度。

    Args:
        task_id: 创建批量任务时返回的任务 ID。
    """
    try:
        api_key = get_api_key()
    except ValueError as e:
        return f"错误: {e}"

    url = f"https://hunter.qianxin.com/openApi/search/batch/{task_id}"  #
    params = {"api-key": api_key}  #

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)  #
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            return f"查询任务进度时发生网络错误: {str(e)}"


@mcp.tool()
async def hunter_batch_task_result_download(task_id: int, save_dir: str = None, file_name: str = None) -> str:
    """
    下载 Qianxin Hunter 批量查询的导出文件（CSV格式），保存到本地。注意：需先使用 hunter_batch_task_progress 确认任务已完成。

    Args:
        task_id: 任务 ID。
        save_dir: 可选。保存文件的目录。如果未提供，将尝试从环境变量里获取默认目录。
        file_name: 可选。保存的文件名。如果未提供，将尝试使用服务器返回的文件名。
    """
    try:
        api_key = get_api_key()
    except ValueError as e:
        return f"错误: {e}"

    save_dir = save_dir or os.environ.get("DEFAULT_BATCH_SAVE_DIR", "")
    if not save_dir:
        return "错误: 必须指定 save_dir (文件保存目录) 或 配置环境变量 DEFAULT_BATCH_SAVE_DIR (默认的文件保存目录)"

    url = f"https://hunter.qianxin.com/openApi/search/download/{task_id}"  #

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={"api-key": api_key})  #

        # 检查是否返回了错误 JSON
        if "application/json" in response.headers.get("Content-Type", ""):
            return response.text

        response.raise_for_status()

        # 自动获取文件名逻辑
        final_file_name = file_name
        if not final_file_name:
            # 尝试从 Content-Disposition 解析文件名
            content_disposition = response.headers.get("Content-Disposition", "")
            match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if match:
                final_file_name = match.group(1)
            else:
                final_file_name = f"hunter_task_{task_id}.csv"

        full_save_path = os.path.join(save_dir, final_file_name)

        with open(full_save_path, "wb") as f:
            f.write(response.content)

        return f"文件已成功保存至: {full_save_path}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()

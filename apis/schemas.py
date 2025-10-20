
from pydantic import BaseModel, Field, DirectoryPath, FilePath
from typing import Optional, Any, List


# --- 积木 1: 标准状态响应 (你已经定义得很好，我们稍作优化) ---
class StatusResponse(BaseModel):
    """一个通用的、标准化的API响应模型。"""
    status: str = Field("success", description="操作结果状态，例如 'success' 或 'error'。")
    message: str = Field(..., description="描述操作结果的文本信息。")
    details: Optional[Any] = Field(None, description="可选的、用于携带额外信息的负载，例如处理结果统计。")


# --- 积木 2: 单个输入路径 ---
class SingleInputPath(BaseModel):
    """需要单个输入路径的基础请求。"""
    source_path: str = Field(..., description="源文件或文件夹的完整路径。")


# --- 积木 3: 输入/输出路径对 (这是你最常用的！) ---
class InputOutputPaths(BaseModel):
    """需要一个输入路径和一个输出路径的基础请求。"""
    source_path: str = Field(..., description="源文件夹的完整路径。")
    destination_path: str = Field(..., description="目标文件夹的完整路径。")


class ProcessAndComparePath(InputOutputPaths):
    gt_path: str = Field(..., description="标准答案(Ground Truth)JSON文件路径。"),
    expected_slips: int = Field(..., description="期望分割出的回单联数。")
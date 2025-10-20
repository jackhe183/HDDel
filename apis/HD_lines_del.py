from importlib.util import source_hash
import os

from fastapi import APIRouter

from .schemas import InputOutputPaths, StatusResponse, ProcessAndComparePath

from ..workers.获取图片线信息 import get_images_lines_info as process_images_from_folder
from ..workers.调用算法main import process_and_compare

router = APIRouter(
    prefix="/HDLineDel",
)

@router.post("/get_images_lines_info")
def get_images_lines_info_endpoint(request:InputOutputPaths):
    process_images_from_folder(
        source_folder_path=request.source_path,
        output_folder_path=request.destination_path
    )

    final_output_path = os.path.join(request.destination_path, "image_info.json")
    return StatusResponse(message=f"结果已成功保存至: {os.path.abspath(final_output_path)}")

@router.post("/process_and_compare")
def process_and_compare_endpoint(request:ProcessAndComparePath):
    process_and_compare(
        input_json_path=request.source_path,
        gt_json_path=request.gt_path,
        expected_slips=request.expected_slips,
        output_folder_path=request.destination_path
    )

    return StatusResponse(message=f"结果已成功保存至: {os.path.abspath(request.destination_path)}")

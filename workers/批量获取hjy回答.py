import os
import requests
import time
import json

from tenacity import sleep

# --- 请根据你第一步获取的信息修改以下配置 ---

# 1. 身份认证信息 (从浏览器开发者工具的请求头中复制)
LOGIN_COOKIE = 'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJpc3MiOiJyYmFjLWFkbWluIiwiZXhwIjoxNzc3Mjc1NDYxLCJuYmYiOjE3NTEzNTU0NjEsImlhdCI6MTc1MTM1NTQ2MX0.REVkWIkBmNTGt8j4Yn8yDcs5ABUFXbRyeEMqmbarn7uYQUybwcGvTlo_JSfj1CDrZ3hnpxLkwuQ9k9x1HsThUg'

# 2. 上传接口的URL (从浏览器开发者工具的网络请求中复制)
UPLOAD_URL = 'https://devops-server-test.hjysmart.com/devops/file/upload'

# 3. 上传文件时，表单中文件字段的名称 (从Payload中查看)
FILE_FIELD_NAME = 'file'


# --- 脚本主逻辑 ---

def images2url(image_path: str) -> str:
    """执行文件上传并返回URL"""
    print(f"  [步骤1/3] 开始上传文件: {os.path.basename(image_path)}...")

    headers = {
        'Authorization': f'Bearer {LOGIN_COOKIE}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
    }

    if not os.path.exists(image_path):
        print(f"  -> 错误：找不到输入文件 '{image_path}'。")
        return None

    try:
        with open(image_path, 'rb') as f:
            files = {FILE_FIELD_NAME: (os.path.basename(image_path), f, 'image/jpeg')}  # 明确指定MIME类型可能有助于服务器处理

            response = requests.post(UPLOAD_URL, headers=headers, files=files, timeout=60)
            response.raise_for_status()

            response_json = response.json()
            image_url = response_json.get('data')  # 使用 .get() 避免KeyError

            if isinstance(image_url, str) and image_url:
                print(f"  -> 上传成功, URL: {image_url}")
                time.sleep(0.5)  # 稍微减少等待时间
                return image_url
            else:
                print(f"  -> 上传成功但未在响应中找到有效的URL。服务器响应: {response.text}")
                return None

    except requests.exceptions.RequestException as e:
        print(f"  -> 上传失败: {os.path.basename(image_path)}, 错误: {e}")
        return None
    except Exception as e:
        print(f"  -> 发生未知错误: {e}")
        return None

def get_receipt_info(image_url: str, receipt_type: str) -> str:
    """
    根据提供的图片URL和票据类型，发送POST请求并返回响应的JSON字符串。

    :param image_url: 票据图片的URL地址.
    :param receipt_type: 票据类型，例如 "BANK_DZD" (对账单), "BANK_CDHP" (承兑汇票), "BANK_HD" (回单).
    :return: 服务器响应的JSON格式字符串。如果请求失败，则返回一个包含错误信息的JSON字符串。
    """
    # 基础URL和公用请求头
    base_url = "http://ocr26-daily.hjysmart.com/reciept/ai/parse"
    headers = {
        'Content-Type': 'application/json'
    }

    # 根据票据类型确定完整的请求URL
    # 注意：这里假设回单和对账单使用相同的 'bankStatement' 路径，承兑汇票使用 'bankAcceptanceBill'。
    # 如果实际情况不同，需要调整此处的逻辑。
    if receipt_type in "BANK_DZD":
        full_url = f"{base_url}/bankStatement"
    elif receipt_type == "BANK_CDHP":
        full_url = f"{base_url}/bankAcceptanceBill"
    elif receipt_type == "BANK_HD":
        full_url = f"{base_url}/bankReceipt"
    else:
        error_message = {"error": f"未知的票据类型: {receipt_type}"}
        return json.dumps(error_message, indent=4, ensure_ascii=False)

    # 构建请求体
    payload = {
        "entId": 1948305914895273984,  # 固定 entId
        "recieptUrl": image_url,
        "recieptType": receipt_type,
        "bankReceiptSource": "FROM_WEB"
    }

    try:
        # 发送POST请求
        response = requests.post(full_url, data=json.dumps(payload), headers=headers, timeout=60) # 设置60秒超时
        response.raise_for_status()  # 如果状态码不是 2xx，则抛出 HTTPError 异常

        # 返回格式化的JSON字符串
        return json.dumps(response.json(), indent=4, ensure_ascii=False)

    except requests.exceptions.HTTPError as errh:
        error_message = {"error": "Http Error", "details": str(errh)}
        return json.dumps(error_message, indent=4, ensure_ascii=False)
    except requests.exceptions.ConnectionError as errc:
        error_message = {"error": "Error Connecting", "details": str(errc)}
        return json.dumps(error_message, indent=4, ensure_ascii=False)
    except requests.exceptions.Timeout as errt:
        error_message = {"error": "Timeout Error", "details": str(errt)}
        return json.dumps(error_message, indent=4, ensure_ascii=False)
    except requests.exceptions.RequestException as err:
        error_message = {"error": "Oops: Something Else", "details": str(err)}
        return json.dumps(error_message, indent=4, ensure_ascii=False)
    except json.JSONDecodeError:
        error_message = {"error": "Failed to decode JSON", "response_text": response.text}
        return json.dumps(error_message, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    source_folder = \
        r"C:\Users\EDY\Desktop\mainProject\申元回单切割\拆点功能1017\新建文件夹"

    target_folder = \
        r'C:\Users\EDY\Desktop\mainProject\申元回单切割\hjyHD识别'

    bill_type = "BANK_DZD"

    print(f"开始处理文件夹: {source_folder}")
    print(f"JSON 输出将保存到: {target_folder}")

    if not os.path.isdir(source_folder):
        print(f"错误：源文件夹 '{source_folder}' 不存在或不是一个目录。")
    else:
        for dirpath, _, filenames in os.walk(source_folder):
            relative_path = os.path.relpath(dirpath, source_folder)
            target_dir = os.path.join(target_folder, relative_path)

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            for filename in filenames:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    source_file_path = os.path.join(dirpath, filename)
                    print(f"\n--- 正在处理文件: {source_file_path} ---")

                    bill_image_url = images2url(source_file_path)

                    if bill_image_url:
                        print(f"  [步骤2/3] 请求票据信息 (类型: {bill_type})...")
                        response_json_str = get_receipt_info(bill_image_url, bill_type)
                        time.sleep(0.1)
                        base_filename, _ = os.path.splitext(filename)
                        output_filename = f"{base_filename}.json"
                        output_filepath = os.path.join(target_dir, output_filename)

                        print(f"  [步骤3/3] 保存响应到: {output_filepath}")
                        try:
                            # 尝试解析JSON以确认其有效性
                            parsed_json = json.loads(response_json_str)
                            print(parsed_json)
                            sleep(0.1)
                            with open(output_filepath, 'w', encoding='utf-8') as f:
                                f.write(response_json_str)  # 写入已格式化的字符串

                        except json.JSONDecodeError:
                            print(f"  -> 错误: 从服务器收到的响应不是有效的JSON格式。响应内容: {response_json_str}")
                        except Exception as e:
                            print(f"  -> 保存JSON文件失败, 错误: {e}")
                    else:
                        print("  -> 获取图片URL失败，跳过此文件。")

        print("\n" + "=" * 50)
        print("所有文件处理完毕！")
        print("=" * 50 + "\n")
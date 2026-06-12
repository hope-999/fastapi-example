import time
import shutil
from pathlib import Path
from PIL import Image, ImageOps
from celery_app import celery_app

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@celery_app.task(bind=True, max_retries=3)
def process_image(self, image_path: str, target_width: int = 800):
    """图片压缩任务：带进度反馈和重试"""
    try:
        # 步骤 1：加载（20%）
        self.update_state(state="PROGRESS", meta={"progress": 20, "step": "loading"})
        img = Image.open(image_path)

        # 步骤 2：处理（60%）
        self.update_state(state="PROGRESS", meta={"progress": 60, "step": "processing"})
        ratio = target_width / img.width
        target_height = int(img.height * ratio)
        img = img.resize((target_width, target_height), Image.LANCZOS)
        img = ImageOps.autocontrast(img)

        # 步骤 3：保存（90%）
        output_path = image_path.replace(".", "_compressed.")
        self.update_state(state="PROGRESS", meta={"progress": 90, "step": "saving"})
        img.save(output_path, quality=85, optimize=True)

        return {
            "original": image_path,
            "output": output_path,
            "width": target_width,
            "height": target_height,
        }

    except Exception as exc:
        # 失败重试，间隔 10 秒
        raise self.retry(exc=exc, countdown=10)


@celery_app.task
def cleanup_old_files():
    """每天凌晨清理 24 小时前的上传文件"""
    now = time.time()
    cleaned = 0
    for f in UPLOAD_DIR.glob("*"):
        if now - f.stat().st_mtime > 86400:
            f.unlink()
            cleaned += 1
    return {"cleaned": cleaned}

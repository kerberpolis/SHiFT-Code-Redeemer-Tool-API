import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.config import get_config, AppConfig
from app.models.schemas import FeedbackData, ErrorResponse
from github import Github

router = APIRouter()


@router.post(
    get_config().BASE_PATH + '/feedback',
    tags=["github"],
    responses={
        422: {"model": ErrorResponse},
    }
)
def post_feedback(feedbackData: FeedbackData, config: AppConfig = Depends(get_config)):
    body = f"New feedback reported using the website interface.\n\n" \
            f"* **Reported**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n" \
            f"* **Browser**: {feedbackData.browser}," \
            f"version {feedbackData.browser_version}\n" \
            f"* **OS**: {feedbackData.os}\n" \
            f"* **Screen**: {feedbackData.width}x{feedbackData.height}\n\n" \
            f"## Description\n\n" \
            f"{feedbackData.desc}"

    data = {
        "title": feedbackData.title,
        "body": body,
        "assignee": "kerberpolis",
        "labels": ['Feedback'],
    }

    try:
        g = Github(config.GITHUB_ACCESS_TOKEN)
        repo = g.get_repo("kerberpolis/SHiFT-Code-Redeemer-Tool-API")
        repo.create_issue(**data)  # crete the issue

        return True
    except Exception as e:
        logging.info(e)
        raise HTTPException(status_code=500, detail="Error creating user feedback.")

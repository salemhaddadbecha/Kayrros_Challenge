from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
from starlette.responses import HTMLResponse

router = APIRouter()


@router.get("/", include_in_schema=False)
def overriden_root() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=308)


@router.get("/docs", include_in_schema=False)
def overridden_swagger() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Kayrros Hotspot API",
    )

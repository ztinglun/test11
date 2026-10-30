from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import psycopg
from psycopg.rows import dict_row

from db import get_connection

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_event(conn, event_id: int):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT id, title FROM events WHERE id = %s", (event_id,))
        return cur.fetchone()


@router.get("/events/{event_id}/register")
def register_form(request: Request, event_id: int):
    with get_connection() as conn:
        event = get_event(conn, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="找不到這個活動")

    return templates.TemplateResponse(
        request, "register.html",
        {"event_id": event_id, "event_title": event["title"], "error": None},
    )


@router.post("/events/{event_id}/register")
def register_submit(
    request: Request,
    event_id: int,
    name: str = Form(...),
    phone: str = Form(...),
):
    name = name.strip()
    phone = phone.strip()

    with get_connection() as conn:
        event = get_event(conn, event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="找不到這個活動")

        error = None
        if not name or not phone:
            error = "請填寫姓名和電話"
        else:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO registrations (event_id, name, phone) VALUES (%s, %s, %s)",
                        (event_id, name, phone),
                    )
            except psycopg.errors.UniqueViolation:
                conn.rollback()
                error = "你已經報名過這個活動了"

    if error:
        return templates.TemplateResponse(
            request, "register.html",
            {"event_id": event_id, "event_title": event["title"], "error": error},
        )

    return RedirectResponse(url=f"/events/{event_id}/registrations", status_code=303)


@router.get("/events/{event_id}/registrations")
def list_registrations(request: Request, event_id: int):
    with get_connection() as conn:
        event = get_event(conn, event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="找不到這個活動")

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT name, phone, registered_at FROM registrations "
                "WHERE event_id = %s ORDER BY registered_at",
                (event_id,),
            )
            rows = cur.fetchall()

    return templates.TemplateResponse(
        request, "registrations.html",
        {"event_id": event_id, "event_title": event["title"], "registrations": rows},
    )
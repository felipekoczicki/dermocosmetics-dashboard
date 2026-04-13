import sqlite3, os
from contextlib import asynccontextmanager, contextmanager
from datetime import date
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

DB_PATH = "tarefas.db"

# ── Database ───────────────────────────────────────────────────────────────────

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nome        TEXT NOT NULL,
                descricao   TEXT,
                prioridade  TEXT NOT NULL DEFAULT 'media',
                status      TEXT NOT NULL DEFAULT 'pendente',
                vencimento  TEXT,
                criado_em   TEXT DEFAULT (date('now','localtime'))
            );
        """)

# ── App ────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# ── Rotas ──────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, status: str = "", prioridade: str = ""):
    with get_db() as conn:
        conditions, params = [], []
        if status:
            conditions.append("status = ?")
            params.append(status)
        if prioridade:
            conditions.append("prioridade = ?")
            params.append(prioridade)
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        tarefas = conn.execute(
            f"SELECT * FROM tarefas {where} ORDER BY "
            f"CASE prioridade WHEN 'alta' THEN 1 WHEN 'media' THEN 2 WHEN 'baixa' THEN 3 END, "
            f"vencimento ASC NULLS LAST, id DESC",
            params
        ).fetchall()

        counts = {
            "total":      conn.execute("SELECT COUNT(*) FROM tarefas").fetchone()[0],
            "pendente":   conn.execute("SELECT COUNT(*) FROM tarefas WHERE status='pendente'").fetchone()[0],
            "andamento":  conn.execute("SELECT COUNT(*) FROM tarefas WHERE status='andamento'").fetchone()[0],
            "concluida":  conn.execute("SELECT COUNT(*) FROM tarefas WHERE status='concluida'").fetchone()[0],
            "vencendo":   conn.execute(
                "SELECT COUNT(*) FROM tarefas WHERE vencimento <= date('now','localtime','+2 days') "
                "AND vencimento >= date('now','localtime') AND status != 'concluida'"
            ).fetchone()[0],
        }

    hoje = date.today().isoformat()
    return templates.TemplateResponse("index.html", {
        "request":    request,
        "tarefas":    [dict(t) for t in tarefas],
        "counts":     counts,
        "status":     status,
        "prioridade": prioridade,
        "hoje":       hoje,
    })

@app.post("/criar")
async def criar(
    nome:       str  = Form(...),
    descricao:  str  = Form(""),
    prioridade: str  = Form("media"),
    vencimento: str  = Form(""),
):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO tarefas (nome, descricao, prioridade, vencimento) VALUES (?,?,?,?)",
            (nome.strip(), descricao.strip(), prioridade, vencimento or None)
        )
    return RedirectResponse("/", status_code=303)

@app.post("/atualizar/{tid}")
async def atualizar(
    tid:        int,
    nome:       str = Form(...),
    descricao:  str = Form(""),
    prioridade: str = Form("media"),
    status:     str = Form("pendente"),
    vencimento: str = Form(""),
):
    with get_db() as conn:
        conn.execute(
            "UPDATE tarefas SET nome=?, descricao=?, prioridade=?, status=?, vencimento=? WHERE id=?",
            (nome.strip(), descricao.strip(), prioridade, status, vencimento or None, tid)
        )
    return RedirectResponse("/", status_code=303)

@app.post("/status/{tid}")
async def mudar_status(tid: int, status: str = Form(...)):
    with get_db() as conn:
        conn.execute("UPDATE tarefas SET status=? WHERE id=?", (status, tid))
    return RedirectResponse("/", status_code=303)

@app.post("/excluir/{tid}")
async def excluir(tid: int):
    with get_db() as conn:
        conn.execute("DELETE FROM tarefas WHERE id=?", (tid,))
    return RedirectResponse("/", status_code=303)

@app.get("/tarefa/{tid}", response_class=HTMLResponse)
async def detalhe(request: Request, tid: int):
    with get_db() as conn:
        tarefa = conn.execute("SELECT * FROM tarefas WHERE id=?", (tid,)).fetchone()
    if not tarefa:
        return RedirectResponse("/")
    return templates.TemplateResponse("detalhe.html", {
        "request": request,
        "tarefa":  dict(tarefa),
        "hoje":    date.today().isoformat(),
    })

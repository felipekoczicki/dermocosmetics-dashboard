import os, json, hmac, hashlib, base64, secrets, sqlite3
from contextlib import asynccontextmanager, contextmanager
from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

CLIENT_ID     = os.getenv("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET")
SHOP          = os.getenv("SHOPIFY_SHOP")
APP_URL       = os.getenv("APP_URL")
SCOPES        = "read_products,read_themes,read_online_store_navigation"
API_VERSION   = "2024-10"
DB_PATH       = "monitor.db"

# ── Database ───────────────────────────────────────────────────────────────────

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
            CREATE TABLE IF NOT EXISTS config (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS alteracoes (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo         TEXT NOT NULL,
                recurso_id   TEXT,
                recurso_nome TEXT,
                acao         TEXT NOT NULL,
                descricao    TEXT,
                dados_json   TEXT,
                timestamp    TEXT DEFAULT (datetime('now','localtime'))
            );
            CREATE TABLE IF NOT EXISTS menu_snapshot (
                handle     TEXT PRIMARY KEY,
                dados_json TEXT,
                updated_at TEXT
            );
        """)

def get_token() -> str | None:
    with get_db() as conn:
        row = conn.execute("SELECT value FROM config WHERE key='access_token'").fetchone()
        return row["value"] if row else None

def save_token(token: str):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO config VALUES ('access_token', ?)", (token,))

def log_change(tipo, recurso_id, recurso_nome, acao, descricao, dados=None):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO alteracoes (tipo, recurso_id, recurso_nome, acao, descricao, dados_json) VALUES (?,?,?,?,?,?)",
            (tipo, str(recurso_id) if recurso_id else None, recurso_nome, acao, descricao,
             json.dumps(dados, ensure_ascii=False) if dados else None)
        )

# ── Shopify helpers ────────────────────────────────────────────────────────────

def verify_hmac(body: bytes, hmac_header: str) -> bool:
    digest = hmac.new(CLIENT_SECRET.encode(), body, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(digest).decode(), hmac_header)

async def shopify_get(path: str):
    token = get_token()
    if not token:
        return None
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            f"https://{SHOP}/admin/api/{API_VERSION}{path}",
            headers={"X-Shopify-Access-Token": token}
        )
        return r.json() if r.status_code == 200 else {"_status": r.status_code, "_body": r.text[:300]}

async def register_webhooks(token: str):
    topics = [
        ("products/create", "/webhooks/products"),
        ("products/update", "/webhooks/products"),
        ("products/delete", "/webhooks/products"),
        ("themes/create",   "/webhooks/themes"),
        ("themes/update",   "/webhooks/themes"),
        ("themes/delete",   "/webhooks/themes"),
        ("themes/publish",  "/webhooks/themes"),
    ]
    async with httpx.AsyncClient(timeout=15) as client:
        for topic, path in topics:
            await client.post(
                f"https://{SHOP}/admin/api/{API_VERSION}/webhooks.json",
                headers={"X-Shopify-Access-Token": token, "Content-Type": "application/json"},
                json={"webhook": {"topic": topic, "address": f"{APP_URL}{path}", "format": "json"}}
            )

# ── App ────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(lifespan=lifespan, title="Monitor Shopify")
templates = Jinja2Templates(directory="templates")

# ── OAuth ──────────────────────────────────────────────────────────────────────

@app.get("/install")
def install():
    return RedirectResponse(
        f"https://{SHOP}/admin/oauth/authorize"
        f"?client_id={CLIENT_ID}&scope={SCOPES}"
        f"&redirect_uri={APP_URL}/auth/callback"
        f"&state={secrets.token_hex(16)}"
    )

@app.get("/auth/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(400, "Código OAuth ausente")
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            f"https://{SHOP}/admin/oauth/access_token",
            json={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code}
        )
    token = r.json().get("access_token")
    if not token:
        raise HTTPException(400, f"Erro ao obter token: {r.json()}")
    save_token(token)
    await register_webhooks(token)
    log_change("sistema", None, "Monitor", "instalado", f"App conectado à loja {SHOP}")
    return RedirectResponse("/")

# ── Webhooks ───────────────────────────────────────────────────────────────────

@app.post("/webhooks/products")
async def wh_products(request: Request):
    body = await request.body()
    if not verify_hmac(body, request.headers.get("X-Shopify-Hmac-Sha256", "")):
        raise HTTPException(401, "HMAC inválido")
    topic = request.headers.get("X-Shopify-Topic", "")
    data  = json.loads(body)
    nome  = data.get("title", "—")
    pid   = data.get("id")
    ACOES = {
        "products/create": ("criado",     f"Produto '{nome}' criado"),
        "products/update": ("atualizado", f"Produto '{nome}' atualizado"),
        "products/delete": ("excluído",   f"Produto '{nome}' excluído"),
    }
    acao, desc = ACOES.get(topic, ("alterado", topic))
    detalhes = None
    if topic == "products/update":
        detalhes = {
            "status":    data.get("status"),
            "titulo":    nome,
            "tags":      data.get("tags"),
            "variantes": [
                {"sku": v.get("sku"), "preco": v.get("price"), "estoque": v.get("inventory_quantity")}
                for v in data.get("variants", [])
            ],
        }
    log_change("produto", pid, nome, acao, desc, detalhes)
    return {"ok": True}

@app.post("/webhooks/themes")
async def wh_themes(request: Request):
    body = await request.body()
    if not verify_hmac(body, request.headers.get("X-Shopify-Hmac-Sha256", "")):
        raise HTTPException(401, "HMAC inválido")
    topic = request.headers.get("X-Shopify-Topic", "")
    data  = json.loads(body)
    nome  = data.get("name", "—")
    tid   = data.get("id")
    ACOES = {
        "themes/create":  ("criado",     f"Tema '{nome}' criado"),
        "themes/update":  ("atualizado", f"Tema '{nome}' atualizado"),
        "themes/delete":  ("excluído",   f"Tema '{nome}' excluído"),
        "themes/publish": ("publicado",  f"Tema '{nome}' publicado como tema ativo"),
    }
    acao, desc = ACOES.get(topic, ("alterado", topic))
    log_change("tema", tid, nome, acao, desc, {"role": data.get("role")})
    return {"ok": True}

# ── Menu polling ───────────────────────────────────────────────────────────────

@app.get("/poll/menus")
async def poll_menus():
    """Verifica alterações nos menus comparando com o snapshot anterior."""
    token = get_token()
    if not token:
        return {"erro": "App não instalado. Acesse /install primeiro."}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            f"https://{SHOP}/admin/api/{API_VERSION}/menus.json",
            headers={"X-Shopify-Access-Token": token}
        )
    if r.status_code != 200:
        return {"erro": f"Endpoint indisponível (HTTP {r.status_code})", "detalhe": r.text[:300]}
    menus = r.json().get("menus", [])
    count = 0
    with get_db() as conn:
        for menu in menus:
            handle    = menu.get("handle")
            dados_str = json.dumps(menu, ensure_ascii=False, sort_keys=True)
            row       = conn.execute(
                "SELECT dados_json FROM menu_snapshot WHERE handle=?", (handle,)
            ).fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO menu_snapshot VALUES (?,?,datetime('now','localtime'))",
                    (handle, dados_str)
                )
                log_change("menu", menu.get("id"), menu.get("title"), "detectado",
                           f"Menu '{menu.get('title')}' registrado (snapshot inicial)")
                count += 1
            elif row["dados_json"] != dados_str:
                conn.execute(
                    "UPDATE menu_snapshot SET dados_json=?, updated_at=datetime('now','localtime') WHERE handle=?",
                    (dados_str, handle)
                )
                log_change("menu", menu.get("id"), menu.get("title"), "atualizado",
                           f"Menu '{menu.get('title')}' foi modificado", menu)
                count += 1
    return {"menus_verificados": len(menus), "alteracoes_detectadas": count}

# ── Dashboard ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, tipo: str = "", pagina: int = 1):
    per_page = 50
    offset   = (pagina - 1) * per_page
    with get_db() as conn:
        where  = "WHERE tipo = ?" if tipo else ""
        params = (tipo,) if tipo else ()
        total  = conn.execute(f"SELECT COUNT(*) FROM alteracoes {where}", params).fetchone()[0]
        rows   = conn.execute(
            f"SELECT * FROM alteracoes {where} ORDER BY id DESC LIMIT {per_page} OFFSET {offset}",
            params
        ).fetchall()
        stats = {
            "total":    conn.execute("SELECT COUNT(*) FROM alteracoes").fetchone()[0],
            "hoje":     conn.execute("SELECT COUNT(*) FROM alteracoes WHERE date(timestamp)=date('now','localtime')").fetchone()[0],
            "produtos": conn.execute("SELECT COUNT(*) FROM alteracoes WHERE tipo='produto'").fetchone()[0],
            "temas":    conn.execute("SELECT COUNT(*) FROM alteracoes WHERE tipo='tema'").fetchone()[0],
            "menus":    conn.execute("SELECT COUNT(*) FROM alteracoes WHERE tipo='menu'").fetchone()[0],
        }
    return templates.TemplateResponse("index.html", {
        "request":       request,
        "alteracoes":    [dict(r) for r in rows],
        "stats":         stats,
        "tipo":          tipo,
        "pagina":        pagina,
        "total_paginas": max(1, (total + per_page - 1) // per_page),
        "total":         total,
        "instalado":     get_token() is not None,
        "shop":          SHOP,
    })

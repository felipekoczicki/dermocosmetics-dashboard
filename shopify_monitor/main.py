import os, json, hashlib, sqlite3, asyncio
from contextlib import asynccontextmanager, contextmanager
from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

SHOP        = os.getenv("SHOPIFY_SHOP")
API_VERSION = "2024-10"
DB_PATH     = "monitor.db"
POLL_INTERVALO_MINUTOS = 30

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
            CREATE TABLE IF NOT EXISTS snapshots (
                tipo       TEXT NOT NULL,
                recurso_id TEXT NOT NULL,
                hash       TEXT NOT NULL,
                dados_json TEXT,
                updated_at TEXT DEFAULT (datetime('now','localtime')),
                PRIMARY KEY (tipo, recurso_id)
            );
        """)

def get_config(key: str) -> str | None:
    with get_db() as conn:
        row = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None

def set_config(key: str, value: str):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO config VALUES (?,?)", (key, value))

def get_token() -> str | None:
    return get_config("access_token")

def log_change(tipo, recurso_id, recurso_nome, acao, descricao, dados=None):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO alteracoes (tipo, recurso_id, recurso_nome, acao, descricao, dados_json) VALUES (?,?,?,?,?,?)",
            (tipo, str(recurso_id) if recurso_id else None, recurso_nome, acao, descricao,
             json.dumps(dados, ensure_ascii=False) if dados else None)
        )

# ── Shopify API ────────────────────────────────────────────────────────────────

async def shopify_get_all(path: str, chave: str) -> list:
    """Busca todos os registros com paginação."""
    token = get_token()
    if not token:
        return []
    resultados = []
    url = f"https://{SHOP}/admin/api/{API_VERSION}{path}?limit=250"
    async with httpx.AsyncClient(timeout=30) as client:
        while url:
            r = await client.get(url, headers={"X-Shopify-Access-Token": token})
            if r.status_code != 200:
                break
            resultados.extend(r.json().get(chave, []))
            # Paginação via Link header
            link = r.headers.get("Link", "")
            url = None
            if 'rel="next"' in link:
                for part in link.split(","):
                    if 'rel="next"' in part:
                        url = part.strip().split(";")[0].strip("<>")
                        break
    return resultados

def hash_dados(dados: dict) -> str:
    return hashlib.md5(json.dumps(dados, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

# ── Polling ────────────────────────────────────────────────────────────────────

def _campos_produto(p: dict) -> dict:
    """Extrai campos relevantes de um produto para comparação."""
    return {
        "titulo":   p.get("title"),
        "status":   p.get("status"),
        "tags":     p.get("tags"),
        "variantes": [
            {"sku": v.get("sku"), "preco": v.get("price"), "estoque": v.get("inventory_quantity")}
            for v in p.get("variants", [])
        ],
        "imagens": [i.get("src") for i in p.get("images", [])],
    }

async def poll_produtos() -> dict:
    produtos = await shopify_get_all("/products.json", "products")
    criados = atualizados = 0
    ids_atuais = set()
    with get_db() as conn:
        for p in produtos:
            pid      = str(p["id"])
            nome     = p.get("title", "—")
            campos   = _campos_produto(p)
            h        = hash_dados(campos)
            ids_atuais.add(pid)
            row = conn.execute(
                "SELECT hash FROM snapshots WHERE tipo='produto' AND recurso_id=?", (pid,)
            ).fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO snapshots VALUES ('produto',?,?,?,datetime('now','localtime'))",
                    (pid, h, json.dumps(campos, ensure_ascii=False))
                )
                log_change("produto", pid, nome, "criado", f"Produto '{nome}' detectado")
                criados += 1
            elif row["hash"] != h:
                conn.execute(
                    "UPDATE snapshots SET hash=?, dados_json=?, updated_at=datetime('now','localtime') WHERE tipo='produto' AND recurso_id=?",
                    (h, json.dumps(campos, ensure_ascii=False), pid)
                )
                log_change("produto", pid, nome, "atualizado", f"Produto '{nome}' foi modificado", campos)
                atualizados += 1

        # Detectar excluídos
        rows = conn.execute("SELECT recurso_id, dados_json FROM snapshots WHERE tipo='produto'").fetchall()
        for row in rows:
            if row["recurso_id"] not in ids_atuais:
                dados = json.loads(row["dados_json"] or "{}")
                nome  = dados.get("titulo", row["recurso_id"])
                log_change("produto", row["recurso_id"], nome, "excluído", f"Produto '{nome}' foi excluído")
                conn.execute("DELETE FROM snapshots WHERE tipo='produto' AND recurso_id=?", (row["recurso_id"],))

    return {"verificados": len(produtos), "criados": criados, "atualizados": atualizados}

async def poll_temas() -> dict:
    temas = await shopify_get_all("/themes.json", "themes")
    criados = atualizados = 0
    ids_atuais = set()
    with get_db() as conn:
        for t in temas:
            tid    = str(t["id"])
            nome   = t.get("name", "—")
            campos = {"nome": nome, "role": t.get("role"), "theme_store_id": t.get("theme_store_id")}
            h      = hash_dados(campos)
            ids_atuais.add(tid)
            row = conn.execute(
                "SELECT hash, dados_json FROM snapshots WHERE tipo='tema' AND recurso_id=?", (tid,)
            ).fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO snapshots VALUES ('tema',?,?,?,datetime('now','localtime'))",
                    (tid, h, json.dumps(campos, ensure_ascii=False))
                )
                log_change("tema", tid, nome, "criado", f"Tema '{nome}' detectado")
                criados += 1
            elif row["hash"] != h:
                ant   = json.loads(row["dados_json"] or "{}")
                acao  = "publicado" if campos.get("role") == "main" and ant.get("role") != "main" else "atualizado"
                desc  = f"Tema '{nome}' publicado como tema ativo" if acao == "publicado" else f"Tema '{nome}' atualizado"
                conn.execute(
                    "UPDATE snapshots SET hash=?, dados_json=?, updated_at=datetime('now','localtime') WHERE tipo='tema' AND recurso_id=?",
                    (h, json.dumps(campos, ensure_ascii=False), tid)
                )
                log_change("tema", tid, nome, acao, desc, {"antes": ant, "depois": campos})
                atualizados += 1

        rows = conn.execute("SELECT recurso_id, dados_json FROM snapshots WHERE tipo='tema'").fetchall()
        for row in rows:
            if row["recurso_id"] not in ids_atuais:
                dados = json.loads(row["dados_json"] or "{}")
                nome  = dados.get("nome", row["recurso_id"])
                log_change("tema", row["recurso_id"], nome, "excluído", f"Tema '{nome}' foi excluído")
                conn.execute("DELETE FROM snapshots WHERE tipo='tema' AND recurso_id=?", (row["recurso_id"],))

    return {"verificados": len(temas), "criados": criados, "atualizados": atualizados}

async def poll_menus() -> dict:
    token = get_token()
    if not token:
        return {"erro": "Token não configurado"}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            f"https://{SHOP}/admin/api/{API_VERSION}/menus.json",
            headers={"X-Shopify-Access-Token": token}
        )
    if r.status_code != 200:
        return {"erro": f"HTTP {r.status_code}", "detalhe": r.text[:200]}
    menus = r.json().get("menus", [])
    criados = atualizados = 0
    ids_atuais = set()
    with get_db() as conn:
        for m in menus:
            mid  = str(m["id"])
            nome = m.get("title", "—")
            h    = hash_dados(m)
            ids_atuais.add(mid)
            row  = conn.execute(
                "SELECT hash FROM snapshots WHERE tipo='menu' AND recurso_id=?", (mid,)
            ).fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO snapshots VALUES ('menu',?,?,?,datetime('now','localtime'))",
                    (mid, h, json.dumps(m, ensure_ascii=False))
                )
                log_change("menu", mid, nome, "criado", f"Menu '{nome}' detectado")
                criados += 1
            elif row["hash"] != h:
                conn.execute(
                    "UPDATE snapshots SET hash=?, dados_json=?, updated_at=datetime('now','localtime') WHERE tipo='menu' AND recurso_id=?",
                    (h, json.dumps(m, ensure_ascii=False), mid)
                )
                log_change("menu", mid, nome, "atualizado", f"Menu '{nome}' foi modificado", m)
                atualizados += 1

        rows = conn.execute("SELECT recurso_id, dados_json FROM snapshots WHERE tipo='menu'").fetchall()
        for row in rows:
            if row["recurso_id"] not in ids_atuais:
                dados = json.loads(row["dados_json"] or "{}")
                nome  = dados.get("title", row["recurso_id"])
                log_change("menu", row["recurso_id"], nome, "excluído", f"Menu '{nome}' excluído")
                conn.execute("DELETE FROM snapshots WHERE tipo='menu' AND recurso_id=?", (row["recurso_id"],))

    return {"verificados": len(menus), "criados": criados, "atualizados": atualizados}

async def poll_tudo():
    set_config("ultimo_poll", "rodando")
    r_p = await poll_produtos()
    r_t = await poll_temas()
    r_m = await poll_menus()
    from datetime import datetime
    set_config("ultimo_poll", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    return {"produtos": r_p, "temas": r_t, "menus": r_m}

# ── Scheduler ─────────────────────────────────────────────────────────────────

async def scheduler():
    """Executa poll a cada POLL_INTERVALO_MINUTOS."""
    await asyncio.sleep(5)  # aguarda app subir
    while True:
        try:
            if get_token():
                await poll_tudo()
        except Exception as e:
            log_change("sistema", None, "Scheduler", "erro", f"Erro no poll automático: {e}")
        await asyncio.sleep(POLL_INTERVALO_MINUTOS * 60)

# ── App ────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app):
    init_db()
    asyncio.create_task(scheduler())
    yield

app = FastAPI(lifespan=lifespan, title="Monitor Shopify")
templates = Jinja2Templates(directory="templates")

# ── Setup (token manual) ───────────────────────────────────────────────────────

@app.get("/setup", response_class=HTMLResponse)
async def setup_get(request: Request):
    return templates.TemplateResponse("setup.html", {"request": request, "shop": SHOP, "erro": None})

@app.post("/setup")
async def setup_post(token: str = Form(...)):
    token = token.strip()
    # Validar token chamando a API
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"https://{SHOP}/admin/api/{API_VERSION}/shop.json",
            headers={"X-Shopify-Access-Token": token}
        )
    if r.status_code != 200:
        return templates.TemplateResponse("setup.html", {
            "request": {}, "shop": SHOP,
            "erro": f"Token inválido (HTTP {r.status_code}). Verifique e tente novamente."
        })
    set_config("access_token", token)
    log_change("sistema", None, "Monitor", "configurado", f"Token configurado para {SHOP}")
    asyncio.create_task(poll_tudo())
    return RedirectResponse("/", status_code=303)

# ── Poll manual ────────────────────────────────────────────────────────────────

@app.get("/poll")
async def poll_manual():
    if not get_token():
        return RedirectResponse("/setup")
    resultado = await poll_tudo()
    return RedirectResponse("/", status_code=303)

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
        "ultimo_poll":   get_config("ultimo_poll") or "nunca",
        "intervalo":     POLL_INTERVALO_MINUTOS,
    })

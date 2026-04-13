"""
Execute este script UMA VEZ para obter o access token do Shopify.
Ele abre o navegador, você autoriza, e o token é salvo automaticamente no .env
"""
import os, json, secrets, webbrowser, threading, time
import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv, set_key
from pathlib import Path

load_dotenv()

CLIENT_ID     = os.getenv("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET")
SHOP          = os.getenv("SHOPIFY_SHOP")
SCOPES        = "read_products,read_themes,read_online_store_navigation"
REDIRECT_URI  = "http://localhost:9999/auth/callback"
PORT          = 9999
ENV_FILE      = Path(__file__).parent / ".env"

app = FastAPI()
servidor = None

@app.get("/auth/callback", response_class=HTMLResponse)
async def callback(code: str = None, error: str = None):
    global servidor

    if error:
        html = f"<h2>❌ Erro: {error}</h2><p>Feche e tente novamente.</p>"
        threading.Thread(target=lambda: (time.sleep(1), servidor.should_exit := True)).start()
        return HTMLResponse(html)

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            f"https://{SHOP}/admin/oauth/access_token",
            json={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code}
        )
    data = r.json()
    token = data.get("access_token")

    if token:
        set_key(str(ENV_FILE), "SHOPIFY_ACCESS_TOKEN", token)
        print(f"\n✅ Token obtido com sucesso!")
        print(f"   Salvo em: {ENV_FILE}")
        print(f"\n   Token: {token}")
        print(f"\n   Pode fechar o navegador e rodar o start.bat normalmente.\n")
        html = """
        <html><body style="font-family:sans-serif;padding:40px;text-align:center">
            <h2 style="color:green">✅ Token obtido com sucesso!</h2>
            <p>O token foi salvo. Pode fechar esta janela e usar o Monitor normalmente.</p>
        </body></html>
        """
    else:
        print(f"\n❌ Erro ao obter token: {data}\n")
        html = f"<h2>❌ Erro: {data}</h2>"

    def parar():
        time.sleep(2)
        servidor.should_exit = True
    threading.Thread(target=parar, daemon=True).start()
    return HTMLResponse(html)


def main():
    global servidor

    state = secrets.token_hex(16)
    oauth_url = (
        f"https://{SHOP}/admin/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&scope={SCOPES}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={state}"
    )

    print("=" * 55)
    print("  Obter Token de Acesso Shopify")
    print("=" * 55)
    print(f"\n  Loja: {SHOP}")
    print(f"\n  Abrindo navegador para autorização...")
    print(f"\n  Se não abrir automaticamente, acesse:")
    print(f"  {oauth_url}\n")

    def abrir_browser():
        time.sleep(1.5)
        webbrowser.open(oauth_url)
    threading.Thread(target=abrir_browser, daemon=True).start()

    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning")
    servidor = uvicorn.Server(config)
    servidor.run()

    print("Servidor encerrado.")

if __name__ == "__main__":
    main()

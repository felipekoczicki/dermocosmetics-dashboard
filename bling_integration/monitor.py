"""
Monitor de progresso da importação em tempo real.
Execute em outro terminal enquanto o run_sync.py roda.

Uso:
    python monitor.py
"""

import sqlite3
import time
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "pedidos_bling.db"
REFRESH = 5  # segundos entre atualizações
SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def bar(current, total, width=40):
    if total <= 0:
        filled = 0
        pct = 0.0
    else:
        pct = min(current / total, 1.0)
        filled = int(width * pct)
    b = "#" * filled + "-" * (width - filled)
    return f"[{b}] {pct*100:.1f}%"


def get_stats(conn, conta, data_inicio):
    row = conn.execute(
        "SELECT COUNT(*), MIN(data), MAX(data) FROM pedidos WHERE conta=? AND data >= ?",
        (conta, data_inicio)
    ).fetchone()
    return row[0] or 0, row[1], row[2]


def tail_log(path, n=6):
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
        return lines[-n:]
    except Exception:
        return []


def main():
    LOG_FILE = (
        Path(os.environ.get("TEMP", "C:/Temp"))
        / "claude"
        / "C--Users-Lenovo-Desktop-Claude-Cloude-Project"
    )
    # Encontra o arquivo de log mais recente
    log_path = None
    try:
        log_dirs = sorted(LOG_FILE.glob("*/tasks/*.output"), key=lambda p: p.stat().st_mtime, reverse=True)
        if log_dirs:
            log_path = log_dirs[0]
    except Exception:
        pass

    spin = 0
    prev_counts = {}
    start_times = {}
    DATA_INICIO = "2025-01-01"

    print("Aguardando banco de dados...")

    while True:
        try:
            conn = sqlite3.connect(str(DB_PATH))
            contas = [r[0] for r in conn.execute("SELECT DISTINCT conta FROM pedidos").fetchall()]

            clear()
            now = time.strftime("%H:%M:%S")
            print(f"  Importacao Bling  {SPINNER[spin % len(SPINNER)]}  [{now}]")
            print("=" * 60)

            total_geral = 0
            for conta in sorted(contas):
                count, data_min, data_max = get_stats(conn, conta, DATA_INICIO)
                total_geral += count

                # Calcula velocidade
                prev = prev_counts.get(conta, count)
                if conta not in start_times:
                    start_times[conta] = time.time()
                elapsed = time.time() - start_times[conta]
                delta = count - prev
                velocidade = (count / elapsed * 60) if elapsed > 0 else 0
                prev_counts[conta] = count

                # Estimativa baseada em paginas conhecidas
                estimado = 80000 if conta == "conta_1" else 10000

                print(f"\n  {conta}")
                print(f"  {bar(count, estimado)}")
                print(f"  Importados : {count:>8,} pedidos")
                print(f"  Periodo    : {data_min or '---'} ate {data_max or '---'}")
                print(f"  Velocidade : ~{velocidade:,.0f} pedidos/min")
                print(f"  Estimativa : ~{estimado:,} total (estimado)")

            print(f"\n{'=' * 60}")
            print(f"  TOTAL GERAL: {total_geral:,} pedidos importados desde {DATA_INICIO}")

            if log_path:
                linhas = tail_log(log_path)
                if linhas:
                    print(f"\n  Ultimo log:")
                    for l in linhas[-3:]:
                        txt = l.strip()
                        if txt and ("INFO" in txt or "WARNING" in txt):
                            # Extrai só a mensagem
                            parts = txt.split("  ", 2)
                            msg = parts[-1] if parts else txt
                            print(f"    {msg[:70]}")

            print(f"\n  Atualizando a cada {REFRESH}s  |  Ctrl+C para sair")

            conn.close()
            spin += 1
            time.sleep(REFRESH)

        except KeyboardInterrupt:
            print("\nMonitor encerrado.")
            break
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(REFRESH)


if __name__ == "__main__":
    main()

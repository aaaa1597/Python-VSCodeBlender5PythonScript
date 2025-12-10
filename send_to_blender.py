import os
import time
import socket
import sys
from pathlib import Path

# ======= 設定(環境変数で上書き可) ===============
HOST = os.getenv("BLENDER_HOST", "127.0.0.1")
PORT = int(os.getenv("BLENDER_PORT", "5000"))
# ==============================================

def is_server_ready(host: str, port: int, timeoutsec: float) -> bool:
  """ host:portが疎通できるか timeoutsecまで繰り返し試す """
  deadline = time.time() + timeoutsec
  while time.time() < deadline:
    try:
      with socket.create_connection((host, port), timeout=0.5):
        return True
    except OSError:
      time.sleep(0.2)
  return False

def send_concat(files):
  """ 複数ペイロードを結合して1回の送信で実行させる """
  parts = []
  for p in files:
    t = Path(p).read_text(encoding="utf-8").rstrip()
    parts.append(t)

  payload = "\nprint('--- payload separator ---')\n".join(parts) + "\n"
  print(f"[VS2Blend] Sending {len(files)} payload(s) to {HOST}:{PORT}.")

  with socket.create_connection((HOST, PORT), timeout=3.0) as s:
    s.sendall(payload.encode("utf-8"))
    try:
      s.settimeout(2.0)
      resp = s.recv(65536)
      print(resp.decode("utf-8", errors="replace"))
    except Exception:
      pass
  print(f"[VS2Blend] done.")

def main():
  files = sys.argv[1:]
  if not files:
    print("[VS2Blend] usage: send_to_blender.py <file1.py> <file2.py> ...", file=sys.stderr)
    sys.exit(2)

  # 先にBlender側のサーバが起動しているかを確認(手動起動)
  if not is_server_ready(HOST, PORT, 3.0):
    print(f"[VS2Blend] Blender TCP Server not ready at {HOST}:{PORT}", file=sys.stderr)
    print(f"先に blender_server_startup.blend をダブルクリックして起動してください。", file=sys.stderr)
    sys.exit(1)

  send_concat(files)

if __name__ == "__main__" :
  main()

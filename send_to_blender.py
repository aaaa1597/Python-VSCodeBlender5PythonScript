import os
import time
import socket
import subprocess
import sys
from pathlib import Path

# ======= 設定(環境変数で上書き可) ===============
HOST = os.getenv("BLENDER_HOST", "127.0.0.1")
PORT = int(os.getenv("BLENDER_PORT", "5000"))
# Blernder実行パス(Windows側)
BLENDER_EXE = os.getenv("BLENDER_EXE", "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe")
# 起動時、サーバー起動のblendファイルパス
STARTUP_BLEND = os.getenv("STARTUP_BLEND", str(Path.cwd() / "blender_server_startup.blend"))
BOOT_TIMEOUT_SEC = int(os.getenv("BOOT_TIMEOUT_SEC", "20"))
# ==============================================

def is_server_ready(host: str, port: int, timeoutsec: float) -> bool:
  """ host:portが疎通できるか timeoutsecまで繰り返し試す """
  deadline = time.time() + timeoutsec
  while time.time() < deadline:
    try:
      with socket.create_connection((host, port), timeout=1.0):
        return True
    except OSError:
      time.sleep(0.5)
  return False

def ensure_blender_running():
  """ 既存Blenderのサーバが動いていれば何もしない。未起動ならBlender + *.blendを起動してポートが開くまで待つ """
  # すでに動いているなら即 return
  if is_server_ready(HOST, PORT, 1.0):
    print(f"[Blender] Server already ready at {HOST}:{PORT}")
    return
  # 未起動とみなしてBlenderを起動
  exe = Path(BLENDER_EXE)
  blend = Path(STARTUP_BLEND)
  if not exe.exists():
    raise FileNotFoundError(f"Blender exe not found:{exe}")
  if not blend.exists():
    raise FileNotFoundError(f"Startup *.blend file not found:{blend}")

  print(f"[Blender] Startting Blender:{exe},{blend}")
  # GUIで起動
  subprocess.Popen([str(exe), str(blend)])
  # ポートが開くまで待つ
  if not is_server_ready(HOST, PORT, BOOT_TIMEOUT_SEC):
    raise TimeoutError(f"Server not ready at {HOST}:{PORT} within {BOOT_TIMEOUT_SEC}s.")

  print("[Blender] Server is ready")

def send_concat(files):
  """ 複数ペイロードを結合して1回の送信で実行させる """
  parts = []
  for p in files:
    t = Path(p).read_text(encoding="utf-8").rstrip()
    parts.append(t)

  payload = "\nprint('--- payload separator ---')\n".join(parts) + "\n"
  print(f"[Blender] Sending {len(files)} payload(s) to {HOST}:{PORT}.")

  with socket.create_connection((HOST, PORT), timeout=3.0) as s:
    s.sendall(payload.encode("utf-8"))
    try:
      s.settimeout(2.0)
      resp = s.recv(65536)
      print(resp.encode("utf-8", errors="replace"))
    except Exception:
      pass
  print(f"[Blender] done.")

def main():
  files = sys.argv[1:]
  if not files:
    print("usege: send_to_blender.py <file1.py> <file2.py> ...", file=sys.stderr)
    sys.exit(2)
  ensure_blender_running()
  send_concat(files)

if __name__ == "__main__" :
  main()

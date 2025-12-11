import bpy
import socket
import select
import sys, io, traceback

HOST = "127.0.0.1"
PORT = 5000
BUFSISE = 65535

# 状態管理
SERVER_STATUS = {"running": False, "host": HOST, "port": PORT, "clients": 0, "last": ""}

# ソケット準備(非ブロッキング)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
server.setblocking(False)

SERVER_STATUS["running"] = True
SERVER_STATUS["last"] = f"Listening on {HOST}:{PORT}"
print(f"[Blender] {SERVER_STATUS['last']}")

# 接続中のクライアント管理
clients = []

# stdout/stderrをソケットへ返すラッパー(printを送信側に表示)
class SocketWriter(io.TextIOBase):
  def __init__(self, sock): self.sock = sock
  def write(self, s):
    if not isinstance(s, (bytes, bytearray)):
      s = s.encode('utf-8', errors="replace")
    try: self.sock.sendall(s)
    except Exception: pass  # クライアント側が受信を閉じている場合などは無視
    return len(s)
  def flush(self): pass

# メイン受信ループ(UI非ブロッキング/タイマー駆動)
def handle_socket():
  """UIを止めずに定期呼び出される受信ループ"""
  try:
    # 新規接続(ノンブロッキング)
    try:
      conn, addr = server.accept()
      conn.setblocking(False)
      clients.append(conn)
      SERVER_STATUS["clients"] = len(clients)
      SERVER_STATUS["last"] = f"[Blender] New client: {addr}"
      print(f"[Blender] {SERVER_STATUS['last']}")
    except BlockingIOError:
      pass

    # 受信処理
    if clients:
      # 読み取り可能ソケットを識別
      readable, _, _ = select.select(clients, [], [], 0)
      for s in readable:
        try:
          data = s.recv(BUFSISE)
        except BlockingIOError:
          data = b""

        if not data:
          # 切断
          try:
            print("[Blender] client disconnected...")
            clients.remove(s)
            s.close()
          except Exception:
            pass
          SERVER_STATUS["clients"] = len(clients)
          SERVER_STATUS["last"] = f"[Blender] Client disconnected."
          print(f"[Blender] {SERVER_STATUS['last']}")
          _redraw_view3d()
          continue

        # 受信ペイロードはPythonスクリプト文字列(末尾改行OK 送信側で付ける想定)
        code = data.decode("utf-8", errors="replace").strip("\r\n")
        SERVER_STATUS["last"] = f"[Blender] Received {len(data)} bytes."
        print(f"[Blender] {SERVER_STATUS['last']}")
        _redraw_view3d()
        # 出力をソケットにリダイレクト
        old_out, old_err = sys.stdout, sys.stderr
        out = SocketWriter(s)
        sys.stdout, sys.stderr = out, out

        # 受け取ったコードを実行
        try:
          exec(code, {"bpy": bpy})
          try: s.sendall(b"\nOK\n")
          except Exception: pass
        except Exception as e:
          err_msg = f"ERROR:{e}\n"
          try:
            s.sendall(err_msg.encode("utf-8", errors="replace"))
          except Exception:
            pass
          traceback.print_exc()
        finally:
          sys.stdout, sys.stderr = old_out, old_err

  except Exception as e:
    print(f"[Blender] Socket loop error:{e}")

  # 0.1秒後再度呼び出し(Noneを返すと停止)
  return 0.1

def _redraw_view3d():
  # Nパネルの表示更新用にView3Dを再描画
  for area in bpy.context.window.screen.areas:
    if area.type == 'VIEW_3D':
      area.tag_redraw()

# Nパネルの表示更新処理
class BLENDER_TCP_ServerStatus(bpy.types.Panel):
  bl_idname = "BLENDER_TCP_ServerStatus"
  bl_label = "Blender TCP Server"
  bl_space_type = "VIEW_3D"
  bl_region_type = "UI"
  bl_category = "VSCode_to_Blend"
  def draw(self, context):
    layout = self.layout
    running = "LISTENING" if SERVER_STATUS["running"] else "STOPPED"
    layout.label(text=f"Status: {running}")
    layout.label(text=f"Host: {SERVER_STATUS['host']}:{SERVER_STATUS['port']}")
    layout.label(text=f"Clients: {SERVER_STATUS['clients']}")
    layout.label(text=f"Status: {SERVER_STATUS['last']}")

# タイマー登録＆開始
def register():
  bpy.utils.register_class(BLENDER_TCP_ServerStatus)
  bpy.app.timers.register(handle_socket, first_interval=0.1)

register()
print(f"[Blender] Socket server listening on {HOST}:{PORT}")

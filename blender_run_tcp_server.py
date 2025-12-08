import bpy
import socket
import select

HOST = "127.0.0.1"
PORT = 5000
BUFSISE = 65535

#サーバーソケットを非ブロッキングで作成
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
server.setblocking(False)

# 接続中のクライアント管理
clients = []

def Handle_socket():
  """UIを止めずに定期呼出される受信ループ"""
  try:
    # 新規接続の受付(ノンブロッキング)
    try:
      conn.addr = server.accept()
      conn.setblocking(False)
      clients.append(conn)
      print(f"[Blender] New client: {addr}")
    except BlockingIOError:
      pass
    
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
          print(f"[Blender] client disconnected...")
          clients.remove[s]
          s.close()
          continue

        # 受信ペイロードはPythonスクリプト文字列
        code = data.decode("utf-8", error="replace")
        # 安全のため末尾改行を許可(送信側で付ける前提)
        code = code.strip("\r\n")
        # 受け取ったコードを実行
        try:
          exec(code, {"bpy": bpy})
          s.sendall(b"ok\n")
        except Exception as e:
          msg = f"ERROR:{e}\n"
          s.sendall(msg.encode("uft-8"))
          print(msg)
  except Exception as e:
    print(f"[Blender] Socket loop error:{e}")

  # 0.1秒後再度呼び出し(Noneを返すと停止)
  return 0.1

# タイマー登録
bpy.app.timers.register(Handle_socket, first_interval=0.1)
print(f"[Blender] Socket Server listening on {HOST}:{PORT}")

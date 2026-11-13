import asyncio
import websockets
import json
import os

clients = {}

async def signaling_handler(websocket):
    client_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")
            
            if action == "register":
                client_id = data.get("id")
                clients[client_id] = websocket
                print(f"[+] Dispositivo registrado: {client_id}")
                await websocket.send(json.dumps({"status": "registered", "id": client_id}))
                
            elif action in ["offer", "answer", "candidate"]:
                target_id = data.get("target")
                if target_id in clients:
                    print(f"[+] Enrutando {action} de [{client_id}] hacia [{target_id}]")
                    await clients[target_id].send(message)
                else:
                    print(f"[-] Error: El destino {target_id} no está conectado.")
                    # 🛡️ NUEVO: Avisar al Admin que el Agente no está en línea
                    if action == "offer":
                        await websocket.send(json.dumps({
                            "action": "error", 
                            "message": "El ID del Agente no está conectado a Render. Asegúrate de que su .exe esté abierto."
                        }))
                    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if client_id in clients:
            del clients[client_id]
            print(f"[-] Dispositivo desconectado: {client_id}")

async def main():
    port = int(os.environ.get("PORT", 8765))
    print(f"Escuchando en el puerto {port}...")
    async with websockets.serve(signaling_handler, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import websockets
import json
import os

# Diccionario en memoria para rastrear quién está conectado
# Formato: {"ID_DEL_USUARIO": objeto_websocket}
clients = {}

async def signaling_handler(websocket):
    client_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")
            
            # 1. Registro de un nuevo ejecutable (Admin o Agent)
            if action == "register":
                client_id = data.get("id")
                clients[client_id] = websocket
                print(f"[+] Dispositivo registrado: {client_id}")
                await websocket.send(json.dumps({"status": "registered", "id": client_id}))
                
            # 2. Enrutamiento de datos WebRTC (Ofertas de video, respuestas y red)
            elif action in ["offer", "answer", "candidate"]:
                target_id = data.get("target")
                if target_id in clients:
                    print(f"[+] Enrutando {action} de [{client_id}] hacia [{target_id}]")
                    # Reenviamos el paquete exacto al destino
                    await clients[target_id].send(message)
                else:
                    print(f"[+] Error: El destino {target_id} no está conectado.")
                    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Limpieza cuando alguien cierra el .exe
        if client_id in clients:
            del clients[client_id]
            print(f"[+] Dispositivo desconectado: {client_id}")

async def main():
    print("=============================================")
    print(" REMOT Server - Infraestructura Propia ")
    print("=============================================")
    
    # Render asigna el puerto en la variable 'PORT'. Si no existe, usa 8765 para pruebas locales.
    port = int(os.environ.get("PORT", 8765))
    print(f"Escuchando en el puerto {port}...")
    
    # Inicia el servidor en todas las interfaces
    async with websockets.serve(signaling_handler, "0.0.0.0", port):
        await asyncio.Future() # Mantiene el servidor corriendo infinitamente

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import json
import os
import websockets
import traceback

# Diccionario global para almacenar los clientes conectados: { "ID": websocket }
clients = {}

async def signaling_handler(websocket):
    client_id = None
    try:
        # Bucle principal de escucha para cada cliente
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action")
                
                # 1. REGISTRO DE CLIENTE (Agente o Admin)
                if action == "register":
                    client_id = data.get("id")
                    if client_id:
                        clients[client_id] = websocket
                        print(f"[SERVER] 🟢 Cliente registrado: {client_id} | Total conectados: {len(clients)}")
                        await websocket.send(json.dumps({"action": "registered"}))
                    else:
                        print("[SERVER] ⚠️ Intento de registro sin ID.")
                        
                # 2. ENRUTAMIENTO DE SEÑALIZACIÓN WEBRTC
                elif action in ["offer", "answer", "candidate"]:
                    target_id = data.get("target")
                    target_ws = clients.get(target_id)
                    
                    if target_ws:
                        # Reenvía el mensaje intacto al destinatario
                        print(f"[SERVER] 🔄 Enrutando '{action}' hacia {target_id}")
                        await target_ws.send(message)
                    else:
                        # Si el Agente/Admin no existe o se desconectó
                        print(f"[SERVER] ⚠️ Destino {target_id} no encontrado para acción: {action}")
                        await websocket.send(json.dumps({
                            "action": "error", 
                            "message": f"El usuario {target_id} no está en línea."
                        }))
                        
            except json.JSONDecodeError:
                print("[SERVER-ERROR] ❌ Mensaje recibido no es un JSON válido.")
            except Exception as e:
                print(f"[SERVER-ERROR] ❌ Error interno procesando mensaje de {client_id}: {e}")
                traceback.print_exc()
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"[SERVER] 🔌 Conexión cerrada (Code: {e.code}) para el cliente {client_id}")
    except Exception as e:
        print(f"[SERVER-FATAL] 💥 Error inesperado en el socket de {client_id}: {e}")
    finally:
        # 3. LIMPIEZA AUTOMÁTICA AL DESCONECTAR
        if client_id in clients:
            del clients[client_id]
            print(f"[SERVER] 🔴 Cliente eliminado: {client_id} | Restantes: {len(clients)}")

async def main():
    print("=======================================")
    print(" REMOT Server - Nube Global (Render)   ")
    print("=======================================")
    
    # Render asigna el puerto en la variable 'PORT'. Si no existe, usa 8765 para pruebas locales.
    port = int(os.environ.get("PORT", 8765))
    print(f"Escuchando en el puerto {port}...")
    
    # 0.0.0.0 es obligatorio en la nube para permitir conexiones externas[cite: 7]
    async with websockets.serve(signaling_handler, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

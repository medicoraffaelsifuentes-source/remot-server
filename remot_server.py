import os
# ... (deja el resto de tu código de remot_server.py igual arriba) ...

async def main():
    print("=======================================")
    print(" REMOT Server - Nube Global (Render)   ")
    print("=======================================")
    
    # Render asigna el puerto en la variable 'PORT'. Si no existe, usa 8765 para pruebas locales.
    port = int(os.environ.get("PORT", 8765))
    
    print(f"Escuchando en el puerto {port}...")
    
    # 0.0.0.0 es obligatorio en la nube para escuchar conexiones externas
    async with websockets.serve(signaling_handler, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
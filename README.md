# 🤖 Jolly — Asistente Virtual de Escritorio Autónomo (Cyber-Pet)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-Workflow_Orchestration-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?style=for-the-badge&logo=ollama&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**Jolly** es una mascota virtual y asistente de escritorio 100 % local y privado con estética **Cyber-Holográfica**. Combina una interfaz gráfica transparente en **Python (Tkinter)** con seguimiento ocular, estados emocionales reactivos y síntesis de voz offline en español, conectada a un flujo inteligente en **n8n**, memoria persistente en **PostgreSQL** e inferencia local mediante **Ollama** (`qwen2.5:3b`).

---

## ✨ Características Principales

* **Interfaz Cyber-Pet Holográfica:** Ventana flotante sin bordes (`always-on-top`) dibujada en Tkinter Canvas con visor LED curvo, seguimiento dinámico del cursor, parpadeo natural, partículas orbitales al procesar y ecualizador de voz animado.
* **Estados Emocionales Reactivos:** Cambia automáticamente de paleta neón y expresión facial según la respuesta del modelo (`feliz`, `pensando`, `sorprendido`, `cansado`, `neutral`).
* **Voz Offline en Español:** Síntesis de voz nativa mediante Windows SAPI (`System.Speech`) sin depender de APIs externas ni consumo de nube, con opción de silenciar desde el menú contextual (clic derecho).
* **Memoria Conversacional y Gestión de Notas:** Recuerda el contexto de la charla y ejecuta herramientas (*Tool Calling*) en PostgreSQL (`Guardar_Nota` y `Consultar_Notas`) únicamente bajo solicitud explícita.
* **Sincronización Horaria Local:** Estandarizado a la zona horaria `America/Bogota` (UTC-5) en todos los servicios contenerizados y en el contexto dinámico del agente.
* **Privacidad Total (Local-First):** Toda la inferencia del modelo, el historial de conversación y la base de datos corren localmente dentro de contenedores Docker.

---

## 🏗️ Arquitectura del Sistema

```text
+-----------------------------------+        HTTP POST (JSON)        +-----------------------------------+
|      Frontend (mascota_jolly)     | -----------------------------> |        Orquestador (n8n)          |
|  - Python / Tkinter Cyber-HUD     |                                |  - Webhook (/webhook/jolly)       |
|  - Seguimiento ocular & animaciones| <----------------------------- |  - AI Agent + Contexto Horario    |
|  - Voz offline (Windows SAPI)     |   JSON { "texto", "emocion" }  |  - Sanitizador JS (Nodo Code)     |
+-----------------------------------+                                +-----------------+-----------------+
                                                                                       |
                                                        +------------------------------+------------------------------+
                                                        |                                                             |
                                                        v                                                             v
                                        +-------------------------------+                             +-------------------------------+
                                        |       Ollama (Local LLM)      |                             |     PostgreSQL (Docker)       |
                                        |  - Modelo: qwen2.5:3b         |                             |  - n8n_chat_histories         |
                                        |  - Tool Calling nativo        |                             |  - notas_jolly                |
                                        +-------------------------------+                             +-------------------------------+
```

---

## 📂 Estructura del Repositorio

```text
jolly-desktop-assistant/
├── mascota_jolly.py             # Aplicación principal con consola de depuración
├── mascota_jolly.pyw            # Versión silenciosa sin ventana de terminal (Windows)
├── jolly.ico                    # Ícono personalizado para acceso directo en escritorio
├── jolly_workflow.json          # Flujo exportado de n8n (Webhook, AI Agent, Code, Tools)
├── schema.sql                   # Esquema limpio de tablas en PostgreSQL
├── docker-compose.example.yml   # Infraestructura contenerizada (n8n, PostgreSQL, Ollama)
├── .env.example                 # Plantilla de variables de entorno
└── README.md                    # Documentación del proyecto
```

---

## 🚀 Instalación y Despliegue

### 1. Levantar la infraestructura con Docker
Clona el repositorio, configura tus credenciales locales y levanta los servicios:

```bash
git clone https://github.com/icaro98007/jolly-desktop-assistant.git
cd jolly-desktop-assistant
cp .env.example .env
cp docker-compose.example.yml docker-compose.yml
docker compose up -d
```

### 2. Descargar el modelo en Ollama
Descarga el modelo `qwen2.5:3b` dentro del contenedor de Ollama:

```bash
docker exec -it ollama ollama pull qwen2.5:3b
```

### 3. Importar el flujo en n8n
1. Abre `http://localhost:6789` en tu navegador.
2. Crea un nuevo flujo, haz clic en el menú superior derecho (`...`) → **Import from File** y selecciona `jolly_workflow.json`.
3. Asocia tus credenciales locales de **PostgreSQL** (`postgres_jolly`) y **Ollama** (`http://ollama:11434`).
4. Activa el interruptor **Publish / Active** en la esquina superior derecha.

### 4. Ejecutar a Jolly en Windows
Instala las dependencias de Python y lanza la mascota en modo silencioso:

```bash
python -m pip install requests pillow
pythonw mascota_jolly.pyw
```

---

## 💬 Ejemplos de Uso

| Intención | Ejemplo de Mensaje | Acción del Agente |
| :--- | :--- | :--- |
| **Charla / Consulta** | *"Hola Jolly, ¿qué fecha y hora es hoy?"* | Responde con personalidad usando la hora local (`America/Bogota`) sin tocar la BD. |
| **Guardar Nota** | *"Anota que mañana debo revisar los respaldos."* | Invoca la herramienta `Guardar_Nota` e inserta el registro en `notas_jolly`. |
| **Consultar Notas** | *"¿Qué notas tengo guardadas?"* | Invoca `Consultar_Notas` y resume los pendientes almacenados. |

---

## 🛠️ Controles en el Escritorio

* **Clic izquierdo + arrastrar:** Mover a Jolly libremente por cualquier monitor.
* **Enter / Botón `➤`:** Enviar mensaje al núcleo local.
* **Clic derecho sobre Jolly:** Abrir menú rápido para silenciar/activar voz o cerrar la aplicación.

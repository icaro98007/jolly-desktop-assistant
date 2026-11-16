# 🤖 Jolly - Asistente Virtual de Escritorio Autónomo

Asistente de escritorio flotante con interfaz gráfica en Python (Tkinter), voz offline en español (Windows SAPI), orquestación local mediante **n8n**, memoria persistente y gestión de notas en **PostgreSQL**, e inferencia 100 % local con **Ollama**.

## 🏗️ Arquitectura
- **Frontend (mascota_jolly.py):** Ventana transparente siempre visible con animaciones procedurales, estados emocionales y síntesis de voz local mediante PowerShell.
- **Orquestador (jolly_workflow.json):** Flujo en n8n con Webhook, AI Agent, nodo Code para sanitización de respuestas JSON y soporte de Tool Calling.
- **Cerebro Local:** Ollama ejecutando qwen2.5:3b con soporte nativo de herramientas.
- **Persistencia (schema.sql):** PostgreSQL en Docker (postgres_jolly) almacenando historial de conversación (
8n_chat_histories) y notas (
otas_jolly).

## 🚀 Requisitos
- Python 3.10+ (equests)
- Docker Desktop (contenedores 
8n_local, postgres_jolly y ollama)
- Modelo qwen2.5:3b descargado en Ollama

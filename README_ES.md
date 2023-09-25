# Haly AI Slack Bot

Un ChatBot impulsado por GPT que puede responder preguntas sobre tu organización utilizando búsqueda semántica.

## Características

- Responde a las preguntas de los usuarios en tiempo real.
- Utiliza la API de OpenAI para generar respuestas.
- Se integra con Slack para proporcionar respuestas directamente en los canales de chat.

## Instalación

1. Clona este repositorio.
2. Instala las dependencias con `pip install -r requirements.txt`.
3. Configura las variables de entorno necesarias (ver sección de Configuración).
4. Ejecuta el bot con `python main.py`.

## Configuración

Necesitarás las siguientes variables de entorno:

- `SLACK_BOT_TOKEN`: El token de tu bot de Slack.
- `SLACK_SIGNING_SECRET`: El secreto de firma de tu aplicación Slack.
- `OPENAI_API_KEY`: Tu llave API de OpenAI.

## Licencia

Este proyecto está licenciado bajo la Licencia GNU Affero General Public License v3.0. Consulta el archivo [LICENSE](LICENSE) para más detalles.

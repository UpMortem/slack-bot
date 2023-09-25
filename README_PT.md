# Haly AI Slack Bot

Um chatbot alimentado por GPT que pode responder perguntas sobre sua organização usando pesquisa semântica.

## Características

- Responde às perguntas dos usuários em tempo real.
- Usa a API OpenAI para gerar respostas.
- Integra-se ao Slack para fornecer respostas diretamente nos canais de chat.

## Instalação

1. Clone este repositório.
2. Instale as dependências com `pip install -r requirements.txt`.
3. Configure as variáveis de ambiente necessárias (veja a seção de Configuração).
4. Execute o bot com `python main.py`.

## Configuração

Você precisará das seguintes variáveis de ambiente:

- `SLACK_BOT_TOKEN`: O token do seu bot Slack.
- `SLACK_SIGNING_SECRET`: O segredo de assinatura do seu aplicativo Slack.
- `OPENAI_API_KEY`: Sua chave API OpenAI.

## Licença

Este projeto está licenciado sob a Licença GNU Affero General Public License v3.0. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

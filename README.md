# Flamengo Tickets Bot

Bot em Python para monitorar ingressos em:

    https://ingressos.flamengo.com.br

Funcionalidades:

- Faz login na plataforma com sessão autenticada.
- Lista os jogos disponíveis (campeonato, times, data/hora, event id).
- Você escolhe qual jogo quer monitorar.
- Você escolhe um ou mais setores (ou TODOS).
- Fica consultando a disponibilidade de ingressos.
- Ao encontrar ingresso disponível no setor escolhido:
  - tenta adicionar ao carrinho (até um limite configurado),
  - envia alerta no Telegram com os detalhes.

## Estrutura básica do projeto

flamengo-tickets-bot/
├── main.py
├── requirements.txt
└── flamengo_tickets/
    ├── logging_config.py
    ├── config.py
    ├── domain/...
    ├── http/...
    ├── flamengo/...
    ├── telegram/...
    └── recaptcha/...

(O código já está organizado em módulos: domínio, HTTP, Flamengo, Telegram, reCAPTCHA.)

## Dependências

Instale com:

    pip install -r requirements.txt

Requer:

- Python 3.10+
- requests
- beautifulsoup4
- colorlog
- python-dotenv

## Configuração rápida

Crie um arquivo .env na raiz com:

    FLA_EMAIL=seu_email_ou_cpf
    FLA_PASSWORD=sua_senha

    TELEGRAM_BOT_TOKEN=seu_bot_token
    TELEGRAM_CHAT_ID=seu_chat_id

    POLL_INTERVAL_SECONDS=10
    MAX_CART_TICKETS=3
    REQUEST_MAX_RETRIES=3
    REQUEST_BACKOFF_BASE=1.0
    REQUEST_TIMEOUT_SECONDS=30

Principais:

- FLA_EMAIL / FLA_PASSWORD: login da plataforma de ingressos.
- TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID: dados do bot e chat no Telegram.
- POLL_INTERVAL_SECONDS: intervalo entre consultas de disponibilidade.
- MAX_CART_TICKETS: máximo de ingressos que o bot tenta colocar no carrinho.

## Como rodar

Na raiz do projeto:

    python main.py

Fluxo:

1) Login automático na plataforma.
2) Carrega as partidas disponíveis e mostra uma lista numerada.
3) Você escolhe o número da partida que quer monitorar.
4) Carrega os setores daquele evento e mostra uma lista:
   - você pode escolher vários (ex: "1,3,5") ou "0" para TODOS.
5) O bot entra em loop:
   - chama /buy/get-available-tickets para o event selecionado,
   - procura setores monitorados com active=true,
   - quando encontra:
       - obtém recaptcha_token via função get_recaptcha_token(...),
       - faz POST /buy/book-multiple-tickets,
       - atualiza cart_total,
       - envia alerta no Telegram com detalhes do ingresso.
6) Para automaticamente quando o carrinho chega em MAX_CART_TICKETS
   (ou você interrompe com Ctrl+C).

## reCAPTCHA (2Captcha)

O projeto inclui um solver usando **2Captcha** em `flamengo_tickets/recaptcha/solver.py`.

Para funcionar, defina a variável:

- `APIKEY_2CAPTCHA` (sua chave do 2Captcha)

Sem isso, o bot/API consegue detectar disponibilidade, mas não consegue reservar (porque o booking exige `recaptcha_token`).

## Logs

- Configuração em: flamengo_tickets/logging_config.py
- Uso: from flamengo_tickets.logging_config import logger

Características:

- Logs em console (coloridos) e em arquivo: logs/app.log
- Mensagens detalhadas de:
  - Requests (URL, tentativa, tempo, bytes, status).
  - Decisão de retry e backoff.
  - Parsing iniciado/finalizado (e contagem de itens).
  - Booking e envio de alertas (Telegram).
  - Erros sempre com tipo da exceção + mensagem.

---

# API Flask (para integrar com Front-end)

Além do modo CLI (`main.py`), o projeto agora inclui uma **API REST em Flask** (pasta `flamengo_api/`) para:

- Gerenciar várias contas do Flamengo (múltiplas sessões/cookies).
- Listar jogos (eventos) e setores.
- Iniciar/parar monitoramentos em background.
- Expor status do monitoramento (e reservas realizadas).
- Configurar e testar notificações (Telegram ou EvolutionAPI/WhatsApp).

## Variáveis de ambiente (API)

Crie um `.env` (ou variáveis no servidor) com pelo menos:

- `CRED_FERNET_KEY` **(obrigatório)**: chave para criptografar senhas das contas no banco.
  - Gere com:
    - `python -c "from flamengo_api.services.credentials import generate_key; print(generate_key())"`
- `API_KEY` (opcional): se definido, a API exige header `X-API-Key`.
- `APP_DB_PATH` (opcional): caminho do SQLite (default `data/app.db`).

Configurações HTTP (opcionais):

- `REQUEST_MAX_RETRIES` (default 3)
- `REQUEST_BACKOFF_BASE` (default 1.0)
- `REQUEST_TIMEOUT_SECONDS` (default 30)

## Como rodar a API

Instale dependências:

    pip install -r requirements.txt

Suba a API:

    python run_api.py

A API expõe endpoints em `http://localhost:5000/api/v1/...`

## Notas

- As sessões (cookies) ficam em memória. Se reiniciar o servidor, será necessário fazer login novamente pela API.
- O monitoramento roda em threads (background) e retorna status via endpoints.

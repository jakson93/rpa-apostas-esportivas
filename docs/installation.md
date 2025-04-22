# Guia de Instalação e Uso

Este documento fornece instruções detalhadas para instalar, configurar e utilizar o sistema de automação RPA para apostas esportivas.

## Requisitos do Sistema

- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- Navegador web (Chrome, Firefox ou Edge)
- Conta no Telegram
- Conta no Supabase
- Conta no site de apostas [Bolsa de Aposta](https://bolsadeaposta.bet.br/dsbook/euro/sport/horseracing)

## Instalação

### 1. Clone o Repositório

```bash
git clone [URL_DO_REPOSITORIO]
cd rpa_apostas_esportivas
```

### 2. Crie e Ative um Ambiente Virtual

**No Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**No Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais e configurações:

```
# Credenciais do Telegram
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
TELEGRAM_BOT_TOKEN=seu_bot_token
TELEGRAM_GROUP_ID=id_do_grupo_alvo

# Credenciais do Supabase
SUPABASE_URL=sua_url_supabase
SUPABASE_KEY=sua_chave_supabase

# Configurações de apostas
DEFAULT_STAKE=10
MAX_STAKE=100
MIN_STAKE=5

# Configurações do navegador
BROWSER_TYPE=chrome
HEADLESS=false

# Configurações da aplicação
DEBUG_MODE=false
LOG_LEVEL=INFO
```

## Configuração do Telegram

### 1. Obtenha as Credenciais da API do Telegram

1. Acesse [my.telegram.org](https://my.telegram.org/auth)
2. Faça login com sua conta do Telegram
3. Clique em "API Development Tools"
4. Crie um novo aplicativo preenchendo os campos necessários
5. Anote o `api_id` e `api_hash` gerados

### 2. Crie um Bot do Telegram

1. Abra o Telegram e procure por "@BotFather"
2. Inicie uma conversa e envie o comando `/newbot`
3. Siga as instruções para criar um novo bot
4. Anote o token do bot fornecido

### 3. Obtenha o ID do Grupo

1. Adicione o bot ao grupo onde as apostas serão compartilhadas
2. Use um dos métodos a seguir para obter o ID do grupo:
   - Envie uma mensagem no grupo e acesse `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
   - Ou use o bot [@getidsbot](https://t.me/getidsbot) no grupo

## Configuração do Supabase

### 1. Crie uma Conta no Supabase

1. Acesse [supabase.com](https://supabase.com/) e crie uma conta
2. Crie um novo projeto

### 2. Configure o Banco de Dados

1. No painel do Supabase, vá para a seção "SQL Editor"
2. Execute o seguinte SQL para criar as tabelas necessárias:

```sql
-- Habilita a extensão uuid-ossp para gerar UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de apostas
CREATE TABLE IF NOT EXISTS bets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    race TEXT NOT NULL,
    horse_name TEXT NOT NULL,
    odds NUMERIC NOT NULL,
    stake NUMERIC,
    bet_type TEXT NOT NULL DEFAULT 'win',
    raw_message TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    result JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Tabela de logs
CREATE TABLE IF NOT EXISTS logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_type TEXT NOT NULL,
    description TEXT NOT NULL,
    bet_id UUID REFERENCES bets(id),
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para melhorar a performance
CREATE INDEX IF NOT EXISTS idx_bets_status ON bets(status);
CREATE INDEX IF NOT EXISTS idx_bets_created_at ON bets(created_at);
CREATE INDEX IF NOT EXISTS idx_logs_action_type ON logs(action_type);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(created_at);
CREATE INDEX IF NOT EXISTS idx_logs_bet_id ON logs(bet_id);
```

### 3. Obtenha as Credenciais do Supabase

1. No painel do Supabase, vá para "Settings" > "API"
2. Copie a "URL" e a "anon/public key"
3. Adicione essas informações ao arquivo `.env`

## Uso do Sistema

### 1. Inicie a Aplicação

```bash
python -m src.main
```

### 2. Configure a Interface Gráfica

1. Na aba "Configurações", preencha:
   - Credenciais do Telegram
   - Credenciais do Supabase
   - Configurações do navegador
2. Clique em "Salvar Configurações"
3. Clique em "Testar Conexões" para verificar se tudo está funcionando

### 3. Configure as Apostas

1. Na aba "Apostas", defina:
   - Stake padrão
   - Stake mínimo e máximo
   - Outras configurações avançadas
2. Clique em "Salvar Configurações"

### 4. Inicie a Automação

1. Na barra de ferramentas, clique em "Iniciar"
2. O sistema começará a monitorar o grupo do Telegram
3. Quando uma nova aposta for detectada, o sistema irá:
   - Extrair as informações relevantes
   - Salvar a aposta no banco de dados
   - Realizar a aposta automaticamente no site

### 5. Monitore os Logs

1. Na aba "Logs", você pode acompanhar todas as ações do sistema
2. Clique em "Atualizar Logs" para ver as informações mais recentes

## Formato das Mensagens de Aposta

O sistema é capaz de reconhecer diferentes formatos de mensagens de aposta. Exemplos:

### Formato 1 (Recomendado)
```
Corrida: Royal Ascot - Race 3
Cavalo: Flying Thunder
Odds: 2.5
Stake: 10
Tipo: win
```

### Formato 2
```
Aposta: Royal Ascot - Race 3 - Flying Thunder @ 2.5
```

### Formato 3
```
Corrida Royal Ascot - Race 3: Flying Thunder (2.5)
```

## Solução de Problemas

### O sistema não detecta as apostas

1. Verifique se as credenciais do Telegram estão corretas
2. Confirme se o bot tem acesso ao grupo
3. Verifique se o formato das mensagens está sendo reconhecido

### Falha ao realizar apostas

1. Verifique se as credenciais do site de apostas estão corretas
2. Confirme se o saldo da conta é suficiente
3. Verifique os logs para identificar o erro específico

### Problemas de conexão com o Supabase

1. Verifique se a URL e a chave do Supabase estão corretas
2. Confirme se as tabelas foram criadas corretamente
3. Verifique se há restrições de firewall ou rede

## Manutenção

### Logs

Os logs são armazenados em:
- Arquivo local: `logs/app.log`
- Banco de dados: tabela `logs` no Supabase

### Screenshots

Screenshots das apostas são salvas em:
- Diretório: `screenshots/`

### Backup

Recomenda-se fazer backup regular do banco de dados Supabase para evitar perda de dados.

## Considerações de Segurança

- Nunca compartilhe suas credenciais do Telegram ou Supabase
- Mantenha o arquivo `.env` seguro e fora do controle de versão
- Use uma conta dedicada para o sistema de apostas
- Defina limites de stake para evitar apostas acidentais de valores altos

## Suporte

Para obter suporte ou relatar problemas, entre em contato através de:
- [Email de Suporte]
- [Repositório de Issues]

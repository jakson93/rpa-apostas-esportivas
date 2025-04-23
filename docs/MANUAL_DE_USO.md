# Manual de Uso - RPA Apostas Esportivas

## Introdução

Este manual descreve como configurar e utilizar o sistema RPA de Apostas Esportivas, que foi transformado de um ambiente de simulação para uso real. O sistema é capaz de monitorar mensagens do Telegram contendo informações sobre apostas, extrair os dados relevantes e processá-los.

## Pré-requisitos

- Python 3.8 ou superior
- Conexão com a internet
- Credenciais do Telegram (API ID, API Hash, Bot Token)
- ID do grupo ou canal do Telegram a ser monitorado

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/jakson93/rpa-apostas-esportivas.git
cd rpa-apostas-esportivas
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env` com suas credenciais:
```
# Credenciais do Telegram
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
TELEGRAM_BOT_TOKEN=seu_bot_token
TELEGRAM_GROUP_ID=id_do_grupo_alvo

# Credenciais do Supabase (opcional)
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
DEBUG_MODE=true
LOG_LEVEL=INFO
```

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

- `src/`: Código-fonte principal
  - `assets/`: Recursos estáticos
  - `browser/`: Módulo para automação do navegador
  - `config/`: Configurações da aplicação
  - `database/`: Módulo para interação com o banco de dados
  - `gui/`: Interface gráfica do usuário
  - `telegram/`: Módulo para integração com o Telegram
  - `utils/`: Utilitários diversos
  - `main.py`: Ponto de entrada da aplicação

- `docs/`: Documentação
- `logs/`: Arquivos de log
- `data/`: Armazenamento local (criado automaticamente quando necessário)

## Funcionalidades Principais

### 1. Integração com o Telegram

O sistema se conecta ao Telegram usando a biblioteca Telethon e monitora mensagens em um grupo ou canal específico. Quando uma mensagem contendo informações de aposta é detectada, o sistema extrai os dados relevantes e os processa.

### 2. Extração de Dados de Apostas

O sistema utiliza expressões regulares e análise de texto para extrair informações de apostas das mensagens do Telegram. Os dados extraídos incluem:

- Nome da corrida
- Nome do cavalo
- Odds (cotação)
- Stake (valor da aposta, opcional)
- Tipo de aposta (win, place, show, etc.)

### 3. Armazenamento de Dados

O sistema pode armazenar os dados das apostas de duas formas:

- **Supabase**: Se as credenciais do Supabase estiverem configuradas corretamente, os dados serão armazenados no banco de dados Supabase.
- **Armazenamento Local**: Se o Supabase não estiver disponível ou as credenciais não estiverem configuradas, o sistema utilizará automaticamente o armazenamento local em arquivos JSON.

### 4. Processamento de Apostas

O sistema adiciona as apostas extraídas a uma fila para processamento. O módulo de navegador pode então processar essas apostas, realizando as operações necessárias na plataforma de apostas.

## Como Usar

### Iniciar a Aplicação

Para iniciar a aplicação, execute:

```bash
cd src
python main.py
```

### Monitorar Mensagens do Telegram

O sistema começará a monitorar automaticamente as mensagens do grupo ou canal do Telegram configurado. Não é necessária nenhuma ação adicional.

### Visualizar Logs

Os logs da aplicação são armazenados no diretório `logs/`. Você pode visualizá-los para acompanhar o funcionamento do sistema e identificar possíveis problemas.

### Verificar Apostas Processadas

Se estiver usando o armazenamento local, as apostas processadas serão armazenadas em `data/bets.json`. Se estiver usando o Supabase, você pode acessar os dados através da interface do Supabase.

## Solução de Problemas

### Problemas de Conexão com o Telegram

- Verifique se as credenciais do Telegram estão corretas no arquivo `.env`.
- Certifique-se de que o bot tem permissão para acessar o grupo ou canal configurado.
- Verifique os logs para identificar possíveis erros de conexão.

### Problemas de Extração de Dados

- O sistema está configurado para reconhecer vários formatos de mensagens de apostas, mas pode não reconhecer todos os formatos.
- Se o sistema não estiver reconhecendo corretamente as mensagens, você pode adicionar novos padrões de expressão regular no arquivo `src/telegram/parser.py`.

### Problemas de Armazenamento

- Se estiver tendo problemas com o Supabase, o sistema utilizará automaticamente o armazenamento local.
- Verifique se o diretório `data/` existe e tem permissões de escrita.

## Personalização

### Adicionar Novos Padrões de Mensagens

Para adicionar novos padrões de mensagens, edite o arquivo `src/telegram/parser.py` e adicione novos padrões à lista `PATTERNS` na classe `MessageParser`.

### Configurar Stake Padrão

Você pode configurar o stake padrão no arquivo `.env` através da variável `DEFAULT_STAKE`.

### Configurar Modo Debug

Para ativar o modo debug, configure a variável `DEBUG_MODE=true` no arquivo `.env`. Isso aumentará o nível de detalhamento dos logs.

## Considerações Finais

Este sistema foi projetado para ser robusto e funcionar mesmo em condições adversas, como falhas de conexão com o banco de dados. No entanto, é importante monitorar regularmente o funcionamento do sistema e verificar os logs para identificar possíveis problemas.

Para qualquer dúvida ou problema, entre em contato com o desenvolvedor ou consulte a documentação adicional no diretório `docs/`.

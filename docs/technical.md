# Documentação Técnica

Este documento fornece informações técnicas detalhadas sobre a arquitetura, estrutura e funcionamento do sistema de automação RPA para apostas esportivas.

## Arquitetura do Sistema

O sistema foi desenvolvido seguindo uma arquitetura modular, com separação clara de responsabilidades entre os diferentes componentes. A arquitetura geral é composta por:

### 1. Módulo do Telegram
Responsável por monitorar mensagens em grupos específicos, extrair informações de apostas e encaminhá-las para processamento.

### 2. Interface Gráfica (GUI)
Permite ao usuário configurar credenciais, definir parâmetros de apostas e monitorar o funcionamento do sistema.

### 3. Módulo de Banco de Dados
Gerencia a persistência de dados utilizando o Supabase como backend, armazenando apostas, logs e outras informações relevantes.

### 4. Módulo de Automação do Navegador
Realiza a interação com o site de apostas, executando operações como login, navegação, busca de corridas/cavalos e realização de apostas.

### 5. Módulo Principal
Integra todos os componentes, gerenciando o fluxo de dados e a comunicação entre os módulos.

## Estrutura de Diretórios

```
rpa_apostas_esportivas/
├── src/
│   ├── telegram/         # Módulo para interação com a API do Telegram
│   │   ├── __init__.py
│   │   ├── monitor.py    # Monitoramento de mensagens
│   │   ├── parser.py     # Extração de dados de apostas
│   │   └── manager.py    # Gerenciamento de sessões e filas
│   │
│   ├── gui/              # Interface gráfica para configuração
│   │   ├── __init__.py
│   │   ├── app.py        # Ponto de entrada da GUI
│   │   └── main_window.py # Interface principal
│   │
│   ├── database/         # Integração com Supabase
│   │   ├── __init__.py
│   │   ├── supabase_client.py # Cliente para interação com Supabase
│   │   └── schemas.py    # Esquemas de dados
│   │
│   ├── browser/          # Automação de navegador
│   │   ├── __init__.py
│   │   ├── automation.py # Interação com o site de apostas
│   │   └── manager.py    # Gerenciamento de sessões
│   │
│   ├── utils/            # Funções utilitárias
│   │   ├── __init__.py
│   │   └── validators.py # Validadores de entrada
│   │
│   ├── config/           # Configurações do sistema
│   │   ├── __init__.py
│   │   └── settings.py   # Carregamento de configurações
│   │
│   ├── __init__.py
│   └── main.py           # Ponto de entrada principal
│
├── tests/                # Testes automatizados
├── docs/                 # Documentação
│   ├── installation.md   # Guia de instalação e uso
│   └── technical.md      # Documentação técnica
│
├── logs/                 # Diretório para armazenamento de logs
├── screenshots/          # Diretório para armazenamento de screenshots
├── requirements.txt      # Dependências do projeto
├── .env.example          # Exemplo de arquivo de variáveis de ambiente
└── README.md             # Visão geral do projeto
```

## Fluxo de Dados

O fluxo de dados no sistema segue o seguinte padrão:

1. **Entrada de Dados**:
   - Mensagens recebidas em um grupo do Telegram
   - Configurações definidas pelo usuário na interface gráfica

2. **Processamento**:
   - Extração de informações de apostas das mensagens
   - Validação e normalização dos dados
   - Armazenamento no banco de dados

3. **Execução**:
   - Automação do navegador para acessar o site de apostas
   - Busca da corrida e do cavalo especificados
   - Realização da aposta com o stake definido

4. **Feedback**:
   - Registro de logs no banco de dados e em arquivo
   - Captura de screenshots para verificação
   - Atualização do status da aposta

## Detalhes dos Módulos

### Módulo do Telegram

#### `monitor.py`
Implementa a classe `TelegramMonitor` que se conecta à API do Telegram e monitora mensagens em um grupo específico. Utiliza a biblioteca Telethon para interação com a API.

#### `parser.py`
Contém a classe `MessageParser` que implementa diferentes estratégias para extrair informações de apostas de mensagens de texto. Utiliza expressões regulares e heurísticas para identificar padrões.

#### `manager.py`
Implementa a classe `TelegramManager` que gerencia a sessão do Telegram e coordena a comunicação entre o monitor de mensagens e o sistema de apostas. Utiliza filas assíncronas para processamento.

### Interface Gráfica

#### `main_window.py`
Implementa a interface principal utilizando PyQt5, com abas para configurações, apostas e logs. Permite ao usuário configurar todos os aspectos do sistema.

#### `app.py`
Ponto de entrada para a interface gráfica, inicializa a aplicação PyQt5 e exibe a janela principal.

### Módulo de Banco de Dados

#### `supabase_client.py`
Implementa a classe `SupabaseClient` que gerencia a conexão com o Supabase e fornece métodos para salvar apostas, atualizar status, registrar logs e obter estatísticas.

#### `schemas.py`
Define os esquemas de dados utilizados no sistema, incluindo classes `Bet` e `LogEntry` com métodos para conversão entre objetos Python e formato compatível com o banco de dados.

### Módulo de Automação do Navegador

#### `automation.py`
Implementa a classe `BrowserAutomation` que utiliza Selenium para interagir com o site de apostas, realizando operações como login, navegação, busca de corridas/cavalos e realização de apostas.

#### `manager.py`
Implementa a classe `BrowserManager` que gerencia sessões do navegador e processa a fila de apostas. Utiliza threads para processamento paralelo.

### Módulo Principal

#### `main.py`
Implementa a classe `Application` que integra todos os componentes do sistema, gerenciando o fluxo de dados e a comunicação entre os módulos. Utiliza asyncio para operações assíncronas.

#### `settings.py`
Carrega as configurações do sistema a partir de variáveis de ambiente e fornece acesso centralizado a essas configurações.

## Tratamento de Erros

O sistema implementa tratamento de erros em vários níveis:

1. **Validação de Entrada**:
   - Validação de credenciais e parâmetros na interface gráfica
   - Validação de formato de mensagens no parser do Telegram

2. **Tratamento de Exceções**:
   - Captura e registro de exceções em todos os módulos
   - Tentativas de recuperação automática quando possível

3. **Logging**:
   - Registro detalhado de eventos e erros em arquivo e banco de dados
   - Diferentes níveis de log (INFO, WARNING, ERROR, DEBUG)

4. **Screenshots**:
   - Captura de screenshots antes e depois de cada aposta para verificação

## Segurança

O sistema implementa as seguintes medidas de segurança:

1. **Armazenamento Seguro de Credenciais**:
   - Utilização de variáveis de ambiente para credenciais
   - Não armazenamento de senhas em texto plano

2. **Validação de Dados**:
   - Validação de todas as entradas do usuário
   - Sanitização de dados antes de interagir com APIs externas

3. **Limites de Apostas**:
   - Configuração de stake mínimo e máximo
   - Validação de valores de aposta

## Extensibilidade

O sistema foi projetado para ser facilmente extensível:

1. **Arquitetura Modular**:
   - Separação clara de responsabilidades
   - Interfaces bem definidas entre módulos

2. **Configuração Flexível**:
   - Parâmetros configuráveis via interface gráfica
   - Suporte a diferentes navegadores e formatos de mensagem

3. **Pontos de Extensão**:
   - Possibilidade de adicionar novos parsers para diferentes formatos de mensagem
   - Suporte a diferentes sites de apostas com mínimas modificações

## Desempenho e Escalabilidade

O sistema foi otimizado para desempenho e escalabilidade:

1. **Processamento Assíncrono**:
   - Utilização de asyncio para operações de I/O
   - Processamento paralelo de apostas

2. **Filas de Processamento**:
   - Utilização de filas para gerenciar o fluxo de apostas
   - Controle de concorrência para evitar sobrecarga

3. **Persistência Eficiente**:
   - Índices otimizados no banco de dados
   - Armazenamento seletivo de informações

## Considerações Futuras

Possíveis melhorias e extensões para o sistema:

1. **Integração com Mais Sites de Apostas**:
   - Suporte a múltiplos sites de apostas
   - Comparação de odds entre diferentes plataformas

2. **Análise de Dados**:
   - Implementação de dashboard para análise de desempenho
   - Algoritmos de aprendizado de máquina para otimização de apostas

3. **Notificações**:
   - Envio de notificações por e-mail ou Telegram
   - Alertas para eventos importantes (apostas realizadas, erros críticos)

4. **Automação Avançada**:
   - Suporte a estratégias de apostas mais complexas
   - Integração com fontes de dados externas para tomada de decisão

"""
Módulo para monitoramento e extração de dados do Telegram.

Este módulo é responsável por conectar-se à API do Telegram,
monitorar mensagens em um grupo específico e extrair informações
relevantes sobre apostas esportivas.
"""
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel
import re
import asyncio
from loguru import logger

from ..config.settings import (
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_GROUP_ID,
)
from ..database.supabase_client import SupabaseClient


class TelegramMonitor:
    """
    Classe para monitorar mensagens do Telegram e extrair informações de apostas.
    """

    def __init__(self, db_client=None):
        """
        Inicializa o monitor do Telegram.

        Args:
            db_client: Cliente de banco de dados para armazenar as apostas.
        """
        self.api_id = TELEGRAM_API_ID
        self.api_hash = TELEGRAM_API_HASH
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.group_id = TELEGRAM_GROUP_ID
        self.db_client = db_client or SupabaseClient()
        self.client = None
        self.is_running = False
        self.bet_handlers = []

    async def start(self):
        """
        Inicia o cliente do Telegram e começa a monitorar mensagens.
        """
        if not all([self.api_id, self.api_hash, self.group_id]):
            logger.error("Credenciais do Telegram não configuradas corretamente.")
            return False

        try:
            # Inicializa o cliente do Telegram
            self.client = TelegramClient('telegram_session', self.api_id, self.api_hash)
            await self.client.start(bot_token=self.bot_token)
            
            # Registra o handler para mensagens
            self.client.add_event_handler(
                self._message_handler,
                events.NewMessage(chats=int(self.group_id))
            )
            
            logger.info(f"Monitor do Telegram iniciado. Monitorando grupo {self.group_id}")
            self.is_running = True
            
            # Mantém o cliente rodando
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar o monitor do Telegram: {e}")
            return False
        
        return True

    def add_bet_handler(self, handler):
        """
        Adiciona um handler para processar apostas extraídas.
        
        Args:
            handler: Função que será chamada quando uma nova aposta for extraída.
                    Deve aceitar um parâmetro (dicionário com dados da aposta).
        """
        self.bet_handlers.append(handler)

    async def _message_handler(self, event):
        """
        Handler para processar novas mensagens recebidas.
        
        Args:
            event: Evento de nova mensagem do Telegram.
        """
        try:
            message_text = event.message.text
            logger.debug(f"Nova mensagem recebida: {message_text[:50]}...")
            
            # Tenta extrair informações de aposta da mensagem
            bet_data = self._extract_bet_data(message_text)
            
            if bet_data:
                logger.info(f"Nova aposta detectada: {bet_data['horse_name']} - {bet_data['race']}")
                
                # Salva a aposta no banco de dados
                if self.db_client:
                    await self.db_client.save_bet(bet_data)
                
                # Notifica os handlers registrados
                for handler in self.bet_handlers:
                    await handler(bet_data)
        
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    def _extract_bet_data(self, message_text):
        """
        Extrai informações de aposta de uma mensagem.
        
        Args:
            message_text: Texto da mensagem a ser analisada.
            
        Returns:
            dict: Dicionário com informações da aposta ou None se não for uma aposta válida.
        """
        # Implementação básica de extração - deve ser adaptada ao formato real das mensagens
        try:
            # Exemplo de padrão para extração (deve ser adaptado ao formato real)
            pattern = r"Corrida:\s*(.+?)\s*\n.*?Cavalo:\s*(.+?)\s*\n.*?Odds:\s*(\d+\.?\d*)"
            match = re.search(pattern, message_text, re.DOTALL)
            
            if match:
                race = match.group(1).strip()
                horse_name = match.group(2).strip()
                odds = float(match.group(3).strip())
                
                # Extrai stake se disponível, ou usa None para usar o padrão depois
                stake_match = re.search(r"Stake:\s*(\d+\.?\d*)", message_text)
                stake = float(stake_match.group(1)) if stake_match else None
                
                # Extrai tipo de aposta se disponível
                bet_type_match = re.search(r"Tipo:\s*(.+?)(?:\n|$)", message_text)
                bet_type = bet_type_match.group(1).strip() if bet_type_match else "win"
                
                return {
                    "race": race,
                    "horse_name": horse_name,
                    "odds": odds,
                    "stake": stake,
                    "bet_type": bet_type,
                    "raw_message": message_text,
                    "status": "pending",
                    "created_at": None  # Será preenchido pelo banco de dados
                }
        
        except Exception as e:
            logger.error(f"Erro ao extrair dados da aposta: {e}")
        
        return None

    async def stop(self):
        """
        Para o monitor do Telegram.
        """
        if self.client:
            await self.client.disconnect()
            self.is_running = False
            logger.info("Monitor do Telegram parado.")


# Função para iniciar o monitor em um processo separado
async def start_telegram_monitor(bet_queue=None):
    """
    Inicia o monitor do Telegram em um processo separado.
    
    Args:
        bet_queue: Fila para comunicação com outros processos.
        
    Returns:
        TelegramMonitor: Instância do monitor iniciado.
    """
    from ..database.supabase_client import SupabaseClient
    
    db_client = SupabaseClient()
    monitor = TelegramMonitor(db_client)
    
    if bet_queue:
        async def queue_handler(bet_data):
            await bet_queue.put(bet_data)
        
        monitor.add_bet_handler(queue_handler)
    
    # Inicia o monitor em uma task separada
    asyncio.create_task(monitor.start())
    
    return monitor

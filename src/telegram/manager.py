"""
Módulo para gerenciamento de sessões e filas de apostas do Telegram.

Este módulo é responsável por gerenciar a sessão do cliente Telegram
e coordenar a comunicação entre o monitor de mensagens e o sistema de apostas.
"""
import asyncio
from typing import Optional, List, Callable, Awaitable
from loguru import logger

from .monitor import TelegramMonitor
from .parser import MessageParser, BetData
from ..database.supabase_client import SupabaseClient


class TelegramManager:
    """
    Classe para gerenciar a sessão do Telegram e coordenar o fluxo de apostas.
    """
    
    def __init__(self):
        """Inicializa o gerenciador do Telegram."""
        self.db_client = SupabaseClient()
        self.monitor = TelegramMonitor(self.db_client)
        self.bet_queue = asyncio.Queue()
        self.callbacks: List[Callable[[BetData], Awaitable[None]]] = []
        self._processing_task = None
    
    async def start(self):
        """
        Inicia o gerenciador do Telegram, incluindo o monitor e o processador de filas.
        
        Returns:
            bool: True se iniciado com sucesso, False caso contrário.
        """
        # Adiciona handler para enviar apostas para a fila
        self.monitor.add_bet_handler(self._handle_new_bet)
        
        # Inicia o monitor do Telegram
        monitor_task = asyncio.create_task(self.monitor.start())
        
        # Inicia o processador de filas
        self._processing_task = asyncio.create_task(self._process_bet_queue())
        
        logger.info("Gerenciador do Telegram iniciado com sucesso.")
        return True
    
    async def _handle_new_bet(self, message_data):
        """
        Handler para processar novas mensagens de aposta.
        
        Args:
            message_data: Dados da mensagem recebida.
        """
        if isinstance(message_data, dict) and "raw_message" in message_data:
            # Se já for um dicionário de aposta, apenas coloca na fila
            await self.bet_queue.put(message_data)
        else:
            # Tenta analisar a mensagem para extrair dados da aposta
            message_text = message_data.get("text", "") if isinstance(message_data, dict) else str(message_data)
            bet_data = MessageParser.parse_message(message_text)
            
            if bet_data:
                logger.info(f"Nova aposta detectada e adicionada à fila: {bet_data.horse_name} - {bet_data.race}")
                await self.bet_queue.put(bet_data.to_dict())
    
    async def _process_bet_queue(self):
        """
        Processa a fila de apostas continuamente.
        """
        logger.info("Iniciando processador de fila de apostas")
        
        while True:
            try:
                # Aguarda uma nova aposta na fila
                bet_data = await self.bet_queue.get()
                
                # Converte para objeto BetData se for um dicionário
                if isinstance(bet_data, dict):
                    bet_obj = BetData(
                        race=bet_data.get("race", ""),
                        horse_name=bet_data.get("horse_name", ""),
                        odds=bet_data.get("odds", 0.0),
                        stake=bet_data.get("stake"),
                        bet_type=bet_data.get("bet_type", "win"),
                        raw_message=bet_data.get("raw_message", ""),
                        status=bet_data.get("status", "pending")
                    )
                else:
                    bet_obj = bet_data
                
                # Notifica todos os callbacks registrados
                for callback in self.callbacks:
                    try:
                        await callback(bet_obj)
                    except Exception as e:
                        logger.error(f"Erro ao executar callback para aposta: {e}")
                
                # Marca como processado na fila
                self.bet_queue.task_done()
                
            except asyncio.CancelledError:
                logger.info("Processador de fila de apostas cancelado")
                break
            except Exception as e:
                logger.error(f"Erro ao processar aposta da fila: {e}")
    
    def register_bet_callback(self, callback: Callable[[BetData], Awaitable[None]]):
        """
        Registra um callback para ser chamado quando uma nova aposta for processada.
        
        Args:
            callback: Função assíncrona que será chamada com o objeto BetData.
        """
        self.callbacks.append(callback)
        logger.debug(f"Novo callback registrado. Total: {len(self.callbacks)}")
    
    async def stop(self):
        """
        Para o gerenciador do Telegram, incluindo o monitor e o processador de filas.
        """
        # Para o monitor
        await self.monitor.stop()
        
        # Cancela a tarefa de processamento
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Gerenciador do Telegram parado com sucesso.")


# Função para criar e iniciar o gerenciador em um contexto assíncrono
async def create_telegram_manager() -> TelegramManager:
    """
    Cria e inicia um gerenciador do Telegram.
    
    Returns:
        TelegramManager: Instância do gerenciador iniciado.
    """
    manager = TelegramManager()
    await manager.start()
    return manager

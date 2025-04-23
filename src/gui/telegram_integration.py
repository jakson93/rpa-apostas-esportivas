"""
Módulo para processamento de mensagens do Telegram e integração com a interface gráfica.

Este módulo contém funções para receber mensagens reais do Telegram
e atualizar a interface gráfica com as apostas recebidas.
"""
import asyncio
import threading
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

# Importa o gerenciador do Telegram
from ..telegram.manager import TelegramManager, create_telegram_manager
from ..telegram.parser import BetData

class TelegramIntegration(QObject):
    """
    Classe para integração entre o Telegram e a interface gráfica.
    """
    
    # Sinal emitido quando uma nova aposta é recebida
    bet_received = pyqtSignal(object)
    
    def __init__(self):
        """Inicializa a integração com o Telegram."""
        super().__init__()
        self.telegram_manager = None
        self.event_loop = None
        self.running = False
        self.telegram_task = None
    
    def start(self):
        """Inicia a integração com o Telegram."""
        # Cria um novo event loop para o Telegram
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        
        # Inicia o módulo do Telegram em uma thread separada
        self.telegram_task = self.event_loop.create_task(self.start_async())
        
        # Executa o event loop em uma thread separada
        threading.Thread(target=self._run_event_loop, daemon=True).start()
        
        return True
    
    async def start_async(self):
        """Inicia a integração com o Telegram de forma assíncrona."""
        try:
            self.running = True
            
            # Cria e inicia o gerenciador do Telegram
            self.telegram_manager = await create_telegram_manager()
            
            # Registra o callback para processar apostas
            self.telegram_manager.register_bet_callback(self._handle_bet)
            
            return True
        
        except Exception as e:
            print(f"Erro ao iniciar a integração com o Telegram: {e}")
            self.running = False
            return False
    
    async def _handle_bet(self, bet_data):
        """
        Manipula uma nova aposta recebida do Telegram.
        
        Args:
            bet_data: Dados da aposta (objeto BetData ou dicionário).
        """
        # Emite o sinal com os dados da aposta
        self.bet_received.emit(bet_data)
    
    def _run_event_loop(self):
        """Executa o event loop do asyncio em uma thread separada."""
        self.event_loop.run_forever()
    
    def stop(self):
        """Para a integração com o Telegram."""
        self.running = False
        
        # Para o módulo do Telegram
        if self.telegram_manager:
            asyncio.run_coroutine_threadsafe(self.telegram_manager.stop(), self.event_loop)
        
        # Para o event loop
        if self.event_loop:
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)

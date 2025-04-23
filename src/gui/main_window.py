import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFormLayout, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QGroupBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QSplitter,
    QStyleFactory, QAction
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime

from .telegram_integration import TelegramIntegration

class ThemeManager:
    """
    Gerenciador de temas para a aplicação.
    """
    
    LIGHT_THEME = {
        "background": "#FFFFFF",
        "text": "#000000",
        "accent": "#2979FF",
        "success": "#4CAF50",
        "error": "#F44336",
        "card": "#F5F5F5",
        "border": "#E0E0E0"
    }
    
    DARK_THEME = {
        "background": "#121212",
        "text": "#FFFFFF",
        "accent": "#2979FF",
        "success": "#4CAF50",
        "error": "#F44336",
        "card": "#1E1E1E",
        "border": "#333333"
    }
    
    @staticmethod
    def apply_theme(app, is_dark=False):
        """
        Aplica o tema selecionado à aplicação.
        
        Args:
            app: Instância do QApplication
            is_dark: Se True, aplica o tema escuro; caso contrário, aplica o tema claro
        """
        theme = ThemeManager.DARK_THEME if is_dark else ThemeManager.LIGHT_THEME
        
        # Define a paleta de cores
        if is_dark:
            app.setStyle(QStyleFactory.create("Fusion"))
            
            # Cria uma paleta escura
            palette = app.palette()
            palette.setColor(palette.Window, QColor(theme["background"]))
            palette.setColor(palette.WindowText, QColor(theme["text"]))
            palette.setColor(palette.Base, QColor(theme["card"]))
            palette.setColor(palette.AlternateBase, QColor(theme["border"]))
            palette.setColor(palette.ToolTipBase, QColor(theme["text"]))
            palette.setColor(palette.ToolTipText, QColor(theme["background"]))
            palette.setColor(palette.Text, QColor(theme["text"]))
            palette.setColor(palette.Button, QColor(theme["card"]))
            palette.setColor(palette.ButtonText, QColor(theme["text"]))
            palette.setColor(palette.BrightText, Qt.red)
            palette.setColor(palette.Link, QColor(theme["accent"]))
            palette.setColor(palette.Highlight, QColor(theme["accent"]))
            palette.setColor(palette.HighlightedText, QColor(theme["background"]))
            
            app.setPalette(palette)
            
            # Define o estilo das folhas
            app.setStyleSheet(f"""
                QToolTip {{ color: {theme["text"]}; background-color: {theme["card"]}; border: 1px solid {theme["border"]}; }}
                QGroupBox {{ border: 1px solid {theme["border"]}; border-radius: 5px; margin-top: 1ex; }}
                QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }}
                QTabWidget::pane {{ border: 1px solid {theme["border"]}; }}
                QTabBar::tab {{ background: {theme["card"]}; border: 1px solid {theme["border"]}; padding: 5px; }}
                QTabBar::tab:selected {{ background: {theme["accent"]}; }}
                QHeaderView::section {{ background-color: {theme["card"]}; color: {theme["text"]}; padding: 4px; border: 1px solid {theme["border"]}; }}
                QTableWidget {{ gridline-color: {theme["border"]}; }}
                QTableWidget QTableCornerButton::section {{ background: {theme["card"]}; border: 1px solid {theme["border"]}; }}
            """)
        else:
            app.setStyle(QStyleFactory.create("Fusion"))
            app.setPalette(app.style().standardPalette())
            
            # Define o estilo das folhas para o tema claro
            app.setStyleSheet(f"""
                QGroupBox {{ border: 1px solid {theme["border"]}; border-radius: 5px; margin-top: 1ex; }}
                QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }}
                QTabWidget::pane {{ border: 1px solid {theme["border"]}; }}
                QTabBar::tab {{ background: {theme["card"]}; border: 1px solid {theme["border"]}; padding: 5px; }}
                QTabBar::tab:selected {{ background: {theme["accent"]}; color: white; }}
                QHeaderView::section {{ background-color: {theme["card"]}; padding: 4px; border: 1px solid {theme["border"]}; }}
                QTableWidget {{ gridline-color: {theme["border"]}; }}
                QTableWidget QTableCornerButton::section {{ background: {theme["card"]}; border: 1px solid {theme["border"]}; }}
            """)
        
        return theme

class NotificationSystem:
    """
    Sistema de notificações para alertar sobre eventos importantes.
    """
    
    def __init__(self, parent=None):
        self.parent = parent
        self.notifications = []
    
    def add_notification(self, title, message, type_="info"):
        """
        Adiciona uma nova notificação.
        
        Args:
            title: Título da notificação
            message: Mensagem da notificação
            type_: Tipo da notificação ('info', 'success', 'warning', 'error')
        """
        import datetime
        
        notification = {
            "title": title,
            "message": message,
            "type": type_,
            "timestamp": datetime.datetime.now(),
            "read": False
        }
        
        self.notifications.append(notification)
        
        # Exibe a notificação
        self.show_notification(notification)
        
        return notification
    
    def show_notification(self, notification):
        """
        Exibe uma notificação na interface.
        
        Args:
            notification: Dicionário com os dados da notificação
        """
        if self.parent:
            icon = QMessageBox.Information
            
            if notification["type"] == "success":
                icon = QMessageBox.Information
            elif notification["type"] == "warning":
                icon = QMessageBox.Warning
            elif notification["type"] == "error":
                icon = QMessageBox.Critical
            
            msg_box = QMessageBox(self.parent)
            msg_box.setIcon(icon)
            msg_box.setWindowTitle(notification["title"])
            msg_box.setText(notification["message"])
            msg_box.setStandardButtons(QMessageBox.Ok)
            
            # Exibe a notificação de forma não bloqueante
            msg_box.show()
    
    def mark_as_read(self, index):
        """
        Marca uma notificação como lida.
        
        Args:
            index: Índice da notificação
        """
        if 0 <= index < len(self.notifications):
            self.notifications[index]["read"] = True
    
    def get_unread_count(self):
        """
        Retorna o número de notificações não lidas.
        
        Returns:
            Número de notificações não lidas
        """
        return sum(1 for n in self.notifications if not n["read"])
    
    def get_all_notifications(self):
        """
        Retorna todas as notificações.
        
        Returns:
            Lista de notificações
        """
        return self.notifications

class NotificationsWidget(QWidget):
    """
    Widget para exibir e gerenciar notificações.
    """
    
    def __init__(self, notification_system, parent=None):
        super().__init__(parent)
        self.notification_system = notification_system
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface do widget de notificações."""
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Centro de Notificações")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Tabela de notificações
        self.notifications_table = QTableWidget(0, 3)
        self.notifications_table.setHorizontalHeaderLabels([
            "Hora", "Título", "Mensagem"
        ])
        self.notifications_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.notifications_table)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.clicked.connect(self.refresh_notifications)
        
        self.mark_read_button = QPushButton("Marcar como Lido")
        self.mark_read_button.clicked.connect(self.mark_selected_as_read)
        
        self.clear_button = QPushButton("Limpar Tudo")
        self.clear_button.clicked.connect(self.clear_notifications)
        
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.mark_read_button)
        buttons_layout.addWidget(self.clear_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Carrega as notificações iniciais
        self.refresh_notifications()
    
    def refresh_notifications(self):
        """Atualiza a exibição de notificações."""
        # Limpa a tabela
        self.notifications_table.setRowCount(0)
        
        # Obtém todas as notificações
        notifications = self.notification_system.get_all_notifications()
        
        # Adiciona as notificações à tabela
        for i, notification in enumerate(notifications):
            row = self.notifications_table.rowCount()
            self.notifications_table.insertRow(row)
            
            # Formata a hora
            timestamp = notification["timestamp"].strftime("%H:%M:%S")
            
            # Adiciona os dados à tabela
            self.notifications_table.setItem(row, 0, QTableWidgetItem(timestamp))
            self.notifications_table.setItem(row, 1, QTableWidgetItem(notification["title"]))
            self.notifications_table.setItem(row, 2, QTableWidgetItem(notification["message"]))
            
            # Define a cor da linha com base no tipo de notificação
            for col in range(3):
                item = self.notifications_table.item(row, col)
                if notification["type"] == "success":
                    item.setBackground(QColor(200, 255, 200))  # Verde claro
                elif notification["type"] == "warning":
                    item.setBackground(QColor(255, 255, 200))  # Amarelo claro
                elif notification["type"] == "error":
                    item.setBackground(QColor(255, 200, 200))  # Vermelho claro
                
                # Texto em cinza para notificações lidas
                if notification["read"]:
                    item.setForeground(QColor(150, 150, 150))
    
    def mark_selected_as_read(self):
        """Marca as notificações selecionadas como lidas."""
        selected_rows = set()
        for item in self.notifications_table.selectedItems():
            selected_rows.add(item.row())
        
        for row in selected_rows:
            self.notification_system.mark_as_read(row)
        
        self.refresh_notifications()
    
    def clear_notifications(self):
        """Limpa todas as notificações."""
        self.notification_system.notifications = []
        self.refresh_notifications()

class TelegramMonitorWidget(QWidget):
    """
    Widget para monitoramento em tempo real das apostas recebidas do Telegram.
    """
    
    def __init__(self, notification_system=None, parent=None):
        super().__init__(parent)
        self.notification_system = notification_system
        self.telegram_integration = TelegramIntegration()
        self.init_ui()
        
        # Conecta o sinal de aposta recebida ao método de atualização
        self.telegram_integration.bet_received.connect(self.on_bet_received)
        
        # Inicia a integração com o Telegram
        self.telegram_integration.start()
    
    def init_ui(self):
        """Inicializa a interface do widget de monitoramento do Telegram."""
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Apostas Recebidas do Telegram")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Área de texto para exibição das mensagens
        self.telegram_feed = QTextEdit()
        self.telegram_feed.setReadOnly(True)
        layout.addWidget(self.telegram_feed)
        
        self.setLayout(layout)
    
    def on_bet_received(self, bet_data):
        """
        Manipula uma nova aposta recebida do Telegram.
        
        Args:
            bet_data: Dados da aposta (objeto BetData ou dicionário).
        """
        current_text = self.telegram_feed.toPlainText()
        
        # Formata a mensagem com os dados da aposta
        now = datetime.now().strftime("%H:%M:%S")
        
        # Verifica se bet_data é um dicionário ou um objeto BetData
        if isinstance(bet_data, dict):
            race = bet_data.get("race", "")
            horse_name = bet_data.get("horse_name", "")
            odds = bet_data.get("odds", 0.0)
            stake = bet_data.get("stake", "")
            bet_type = bet_data.get("bet_type", "win")
        else:
            race = bet_data.race
            horse_name = bet_data.horse_name
            odds = bet_data.odds
            stake = bet_data.stake
            bet_type = bet_data.bet_type
        
        new_message = f"[{now}] Nova aposta recebida:\n"
        new_message += f"Corrida: {race}\n"
        new_message += f"Cavalo: {horse_name}\n"
        new_message += f"Odds: {odds}\n"
        new_message += f"Stake: {stake}\n"
        new_message += f"Tipo: {bet_type}\n\n"
        
        # Adiciona a nova mensagem no topo
        self.telegram_feed.setText(new_message + current_text)
        
        # Adiciona uma notificação
        if self.notification_system:
            self.notification_system.add_notification(
                "Nova Aposta Recebida",
                f"Recebida aposta para {horse_name} na corrida {race}",
                "info"
            )
        
        # Aciona a automação para a bolsa de apostas
        self.trigger_betting_automation(bet_data)
    
    def trigger_betting_automation(self, bet_data):
        """
        Aciona a automação para a bolsa de apostas.
        
        Args:
            bet_data: Dados da aposta (objeto BetData ou dicionário).
        """
        # Aqui você deve implementar a chamada para o módulo de automação da bolsa de apostas
        # Por exemplo:
        from ..browser.manager import get_browser_manager
        
        try:
            browser_manager = get_browser_manager()
            
            # Verifica se bet_data é um dicionário ou um objeto BetData
            if isinstance(bet_data, dict):
                # Converte para o formato esperado pelo browser_manager
                from ..database.schemas import Bet
                bet = Bet(
                    race=bet_data.get("race", ""),
                    horse_name=bet_data.get("horse_name", ""),
                    odds=bet_data.get("odds", 0.0),
                    stake=bet_data.get("stake"),
                    bet_type=bet_data.get("bet_type", "win"),
                    raw_message=bet_data.get("raw_message", ""),
                    status="pending",
                    created_at=datetime.now()
                )
            else:
                # Já é um objeto BetData, converte para Bet
                from ..database.schemas import Bet
                bet = Bet(
                    race=bet_data.race,
                    horse_name=bet_data.horse_name,
                    odds=bet_data.odds,
                    stake=bet_data.stake,
                    bet_type=bet_data.bet_type,
                    raw_message=bet_data.raw_message,
                    status="pending",
                    created_at=datetime.now()
                )
            
            # Adiciona a aposta à fila do navegador
            browser_manager.add_bet_to_queue(bet)
            
            # Adiciona uma notificação
            if self.notification_system:
                self.notification_system.add_notification(
                    "Automação Acionada",
                    f"Aposta para {bet.horse_name} adicionada à fila de automação",
                    "success"
                )
        except Exception as e:
            # Adiciona uma notificação de erro
            if self.notification_system:
                self.notification_system.add_notification(
                    "Erro na Automação",
                    f"Erro ao acionar automação: {str(e)}",
                    "error"
                )

class BetTrackingWidget(QWidget):
    """
    Widget para rastreamento de apostas processadas.
    """
    
    def __init__(self, notification_system=None):
        super().__init__()
        self.notification_system = notification_system
        self.init_ui()
        
        # Timer para atualizar o rastreamento de apostas
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_bet_tracking)
        self.update_timer.start(15000)  # Atualiza a cada 15 segundos
    
    def init_ui(self):
        """Inicializa a interface do widget de rastreamento de apostas."""
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Rastreamento de Apostas")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Tabela de apostas
        self.bets_table = QTableWidget(0, 7)
        self.bets_table.setHorizontalHeaderLabels([
            "ID", "Data/Hora", "Corrida", "Cavalo", "Odds", "Stake", "Status"
        ])
        self.bets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.bets_table)
        
        # Botões de filtro
        filter_layout = QHBoxLayout()
        
        self.all_button = QPushButton("Todas")
        self.all_button.clicked.connect(lambda: self.filter_bets("all"))
        
        self.success_button = QPushButton("Sucesso")
        self.success_button.clicked.connect(lambda: self.filter_bets("success"))
        
        self.pending_button = QPushButton("Pendentes")
        self.pending_button.clicked.connect(lambda: self.filter_bets("pending"))
        
        self.error_button = QPushButton("Erro")
        self.error_button.clicked.connect(lambda: self.filter_bets("error"))
        
        filter_layout.addWidget(self.all_button)
        filter_layout.addWidget(self.success_button)
        filter_layout.addWidget(self.pending_button)
        filter_layout.addWidget(self.error_button)
        
        layout.addLayout(filter_layout)
        
        self.setLayout(layout)
        
        # Filtro atual
        self.current_filter = "all"
        
        # Carrega as apostas iniciais
        self.update_bet_tracking()
    
    def update_bet_tracking(self):
        """Atualiza o rastreamento de apostas."""
        try:
            # Obtém as apostas do banco de dados ou armazenamento local
            from ..database.supabase_client import SupabaseClient
            import asyncio
            
            # Cria uma função assíncrona para obter as apostas
            async def get_bets():
                client = SupabaseClient()
                
                if self.current_filter == "all":
                    return await client.get_all_bets()
                elif self.current_filter == "success":
                    return await client.get_bets_by_status("completed")
                elif self.current_filter == "pending":
                    return await client.get_bets_by_status("pending")
                elif self.current_filter == "error":
                    return await client.get_bets_by_status("failed")
                else:
                    return await client.get_all_bets()
            
            # Executa a função assíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            bets = loop.run_until_complete(get_bets())
            loop.close()
            
            # Atualiza a tabela
            self.update_table(bets)
        
        except Exception as e:
            # Adiciona uma notificação de erro
            if self.notification_system:
                self.notification_system.add_notification(
                    "Erro no Rastreamento",
                    f"Erro ao atualizar rastreamento de apostas: {str(e)}",
                    "error"
                )
    
    def update_table(self, bets):
        """
        Atualiza a tabela com as apostas.
        
        Args:
            bets: Lista de apostas.
        """
        # Limpa a tabela
        self.bets_table.setRowCount(0)
        
        # Adiciona as apostas à tabela
        for bet in bets:
            row = self.bets_table.rowCount()
            self.bets_table.insertRow(row)
            
            # Formata a data/hora
            created_at = bet.get("created_at", "")
            if isinstance(created_at, str):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    created_at = dt.strftime("%d/%m/%Y %H:%M:%S")
                except:
                    pass
            
            # Adiciona os dados à tabela
            self.bets_table.setItem(row, 0, QTableWidgetItem(str(bet.get("id", ""))))
            self.bets_table.setItem(row, 1, QTableWidgetItem(str(created_at)))
            self.bets_table.setItem(row, 2, QTableWidgetItem(str(bet.get("race", ""))))
            self.bets_table.setItem(row, 3, QTableWidgetItem(str(bet.get("horse_name", ""))))
            self.bets_table.setItem(row, 4, QTableWidgetItem(str(bet.get("odds", ""))))
            self.bets_table.setItem(row, 5, QTableWidgetItem(str(bet.get("stake", ""))))
            self.bets_table.setItem(row, 6, QTableWidgetItem(str(bet.get("status", ""))))
            
            # Define a cor da linha com base no status
            status = bet.get("status", "")
            color = None
            
            if status == "completed":
                color = QColor(200, 255, 200)  # Verde claro
            elif status == "pending":
                color = QColor(255, 255, 200)  # Amarelo claro
            elif status == "failed":
                color = QColor(255, 200, 200)  # Vermelho claro
            
            if color:
                for col in range(7):
                    self.bets_table.item(row, col).setBackground(color)
    
    def filter_bets(self, filter_type):
        """
        Filtra as apostas por tipo.
        
        Args:
            filter_type: Tipo de filtro ('all', 'success', 'pending', 'error').
        """
        self.current_filter = filter_type
        self.update_bet_tracking()

class SettingsWidget(QWidget):
    """
    Widget para configurações da aplicação.
    """
    
    def __init__(self, notification_system=None):
        super().__init__()
        self.notification_system = notification_system
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface do widget de configurações."""
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Configurações")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Formulário de configurações
        form_layout = QFormLayout()
        
        # Configurações do Telegram
        telegram_group = QGroupBox("Configurações do Telegram")
        telegram_layout = QFormLayout()
        
        self.api_id_input = QLineEdit()
        self.api_hash_input = QLineEdit()
        self.bot_token_input = QLineEdit()
        self.group_id_input = QLineEdit()
        
        telegram_layout.addRow("API ID:", self.api_id_input)
        telegram_layout.addRow("API Hash:", self.api_hash_input)
        telegram_layout.addRow("Bot Token:", self.bot_token_input)
        telegram_layout.addRow("Group ID:", self.group_id_input)
        
        telegram_group.setLayout(telegram_layout)
        form_layout.addRow(telegram_group)
        
        # Configurações de apostas
        betting_group = QGroupBox("Configurações de Apostas")
        betting_layout = QFormLayout()
        
        self.default_stake_input = QDoubleSpinBox()
        self.default_stake_input.setRange(1, 1000)
        self.default_stake_input.setValue(10)
        self.default_stake_input.setSingleStep(1)
        
        self.max_stake_input = QDoubleSpinBox()
        self.max_stake_input.setRange(1, 1000)
        self.max_stake_input.setValue(100)
        self.max_stake_input.setSingleStep(10)
        
        self.min_stake_input = QDoubleSpinBox()
        self.min_stake_input.setRange(1, 1000)
        self.min_stake_input.setValue(5)
        self.min_stake_input.setSingleStep(1)
        
        betting_layout.addRow("Stake Padrão:", self.default_stake_input)
        betting_layout.addRow("Stake Máximo:", self.max_stake_input)
        betting_layout.addRow("Stake Mínimo:", self.min_stake_input)
        
        betting_group.setLayout(betting_layout)
        form_layout.addRow(betting_group)
        
        # Configurações do navegador
        browser_group = QGroupBox("Configurações do Navegador")
        browser_layout = QFormLayout()
        
        self.browser_type_input = QComboBox()
        self.browser_type_input.addItems(["chrome", "firefox", "edge"])
        
        self.headless_input = QCheckBox()
        
        browser_layout.addRow("Tipo de Navegador:", self.browser_type_input)
        browser_layout.addRow("Modo Headless:", self.headless_input)
        
        browser_group.setLayout(browser_layout)
        form_layout.addRow(browser_group)
        
        # Configurações da aplicação
        app_group = QGroupBox("Configurações da Aplicação")
        app_layout = QFormLayout()
        
        self.debug_mode_input = QCheckBox()
        
        self.log_level_input = QComboBox()
        self.log_level_input.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_input.setCurrentText("INFO")
        
        app_layout.addRow("Modo Debug:", self.debug_mode_input)
        app_layout.addRow("Nível de Log:", self.log_level_input)
        
        app_group.setLayout(app_layout)
        form_layout.addRow(app_group)
        
        layout.addLayout(form_layout)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Carregar")
        self.load_button.clicked.connect(self.load_settings)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_settings)
        
        buttons_layout.addWidget(self.load_button)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Carrega as configurações iniciais
        self.load_settings()
    
    def load_settings(self):
        """Carrega as configurações do arquivo .env."""
        try:
            from ..config.settings import get_config
            
            config = get_config()
            
            # Configurações do Telegram
            self.api_id_input.setText(str(config["telegram"]["api_id"] or ""))
            self.api_hash_input.setText(str(config["telegram"]["api_hash"] or ""))
            self.bot_token_input.setText(str(config["telegram"]["bot_token"] or ""))
            self.group_id_input.setText(str(config["telegram"]["group_id"] or ""))
            
            # Configurações de apostas
            self.default_stake_input.setValue(float(config["betting"]["default_stake"] or 10))
            self.max_stake_input.setValue(float(config["betting"]["max_stake"] or 100))
            self.min_stake_input.setValue(float(config["betting"]["min_stake"] or 5))
            
            # Configurações do navegador
            self.browser_type_input.setCurrentText(str(config["browser"]["type"] or "chrome"))
            self.headless_input.setChecked(bool(config["browser"]["headless"]))
            
            # Configurações da aplicação
            self.debug_mode_input.setChecked(bool(config["app"]["debug"]))
            self.log_level_input.setCurrentText(str(config["app"]["log_level"] or "INFO"))
            
            # Adiciona uma notificação
            if self.notification_system:
                self.notification_system.add_notification(
                    "Configurações Carregadas",
                    "As configurações foram carregadas com sucesso.",
                    "success"
                )
        
        except Exception as e:
            # Adiciona uma notificação de erro
            if self.notification_system:
                self.notification_system.add_notification(
                    "Erro ao Carregar Configurações",
                    f"Erro ao carregar configurações: {str(e)}",
                    "error"
                )
    
    def save_settings(self):
        """Salva as configurações no arquivo .env."""
        try:
            import os
            from dotenv import load_dotenv
            
            # Carrega o arquivo .env atual
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
            load_dotenv(env_path)
            
            # Prepara as novas configurações
            new_env = f"""# Credenciais do Telegram
TELEGRAM_API_ID={self.api_id_input.text()}
TELEGRAM_API_HASH={self.api_hash_input.text()}
TELEGRAM_BOT_TOKEN={self.bot_token_input.text()}
TELEGRAM_GROUP_ID={self.group_id_input.text()}

# Credenciais do Supabase
SUPABASE_URL={os.getenv("SUPABASE_URL", "sua_url_supabase")}
SUPABASE_KEY={os.getenv("SUPABASE_KEY", "sua_chave_supabase")}

# Configurações de apostas
DEFAULT_STAKE={self.default_stake_input.value()}
MAX_STAKE={self.max_stake_input.value()}
MIN_STAKE={self.min_stake_input.value()}

# Configurações do navegador
BROWSER_TYPE={self.browser_type_input.currentText()}
HEADLESS={"true" if self.headless_input.isChecked() else "false"}

# Configurações da aplicação
DEBUG_MODE={"true" if self.debug_mode_input.isChecked() else "false"}
LOG_LEVEL={self.log_level_input.currentText()}
"""
            
            # Salva as novas configurações
            with open(env_path, "w") as f:
                f.write(new_env)
            
            # Adiciona uma notificação
            if self.notification_system:
                self.notification_system.add_notification(
                    "Configurações Salvas",
                    "As configurações foram salvas com sucesso.",
                    "success"
                )
        
        except Exception as e:
            # Adiciona uma notificação de erro
            if self.notification_system:
                self.notification_system.add_notification(
                    "Erro ao Salvar Configurações",
                    f"Erro ao salvar configurações: {str(e)}",
                    "error"
                )

class MainWindow(QMainWindow):
    """
    Janela principal da aplicação.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface da janela principal."""
        # Configura a janela
        self.setWindowTitle("RPA Apostas Esportivas")
        self.setGeometry(100, 100, 1200, 800)
        
        # Cria o sistema de notificações
        self.notification_system = NotificationSystem(self)
        
        # Cria o widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Cria as abas
        tabs = QTabWidget()
        
        # Aba de Dashboard
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_tab)
        
        # Adiciona widgets à aba de Dashboard
        dashboard_layout.addWidget(TelegramMonitorWidget(self.notification_system))
        dashboard_layout.addWidget(BetTrackingWidget(self.notification_system))
        
        # Aba de Configurações
        settings_tab = SettingsWidget(self.notification_system)
        
        # Aba de Notificações
        notifications_tab = NotificationsWidget(self.notification_system)
        
        # Adiciona as abas ao widget de abas
        tabs.addTab(dashboard_tab, "Dashboard")
        tabs.addTab(settings_tab, "Configurações")
        tabs.addTab(notifications_tab, "Notificações")
        
        # Adiciona o widget de abas ao layout principal
        main_layout.addWidget(tabs)
        
        # Configura o tema
        app = QApplication.instance()
        ThemeManager.apply_theme(app, is_dark=False)
        
        # Exibe uma notificação de boas-vindas
        self.notification_system.add_notification(
            "Bem-vindo",
            "Bem-vindo ao RPA de Apostas Esportivas!",
            "info"
        )

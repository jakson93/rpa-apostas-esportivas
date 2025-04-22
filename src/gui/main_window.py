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

class StatisticsChart(QWidget):
    """
    Widget para exibir gráficos estatísticos.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Dados iniciais
        self.received_data = [0]
        self.success_data = [0]
        self.error_data = [0]
        self.time_labels = [0]
        self.current_time = 0
        
        # Timer para atualizar o gráfico
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_chart)
        self.update_timer.start(5000)  # Atualiza a cada 5 segundos
    
    def init_ui(self):
        """Inicializa a interface do widget de gráficos estatísticos."""
        layout = QVBoxLayout()
        
        # Cria a figura do matplotlib
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        # Adiciona o canvas ao layout
        layout.addWidget(self.canvas)
        
        # Adiciona botões para alternar entre tipos de gráficos
        buttons_layout = QHBoxLayout()
        
        self.line_button = QPushButton("Gráfico de Linha")
        self.line_button.clicked.connect(lambda: self.change_chart_type("line"))
        
        self.bar_button = QPushButton("Gráfico de Barras")
        self.bar_button.clicked.connect(lambda: self.change_chart_type("bar"))
        
        self.pie_button = QPushButton("Gráfico de Pizza")
        self.pie_button.clicked.connect(lambda: self.change_chart_type("pie"))
        
        buttons_layout.addWidget(self.line_button)
        buttons_layout.addWidget(self.bar_button)
        buttons_layout.addWidget(self.pie_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Tipo de gráfico padrão
        self.chart_type = "line"
        
        # Desenha o gráfico inicial
        self.draw_chart()
    
    def update_chart(self):
        """Atualiza os dados do gráfico com valores simulados."""
        import random
        
        # Incrementa o tempo
        self.current_time += 5
        self.time_labels.append(self.current_time)
        
        # Limita o número de pontos no gráfico
        if len(self.time_labels) > 12:
            self.time_labels = self.time_labels[-12:]
            self.received_data = self.received_data[-12:]
            self.success_data = self.success_data[-12:]
            self.error_data = self.error_data[-12:]
        
        # Gera novos dados aleatórios
        last_received = self.received_data[-1] if self.received_data else 0
        last_success = self.success_data[-1] if self.success_data else 0
        last_error = self.error_data[-1] if self.error_data else 0
        
        # Adiciona de 0 a 3 novas apostas
        new_bets = random.randint(0, 3)
        new_received = last_received + new_bets
        
        # Distribui entre sucesso e erro
        new_success = last_success + random.randint(0, new_bets)
        new_error = new_received - new_success
        
        self.received_data.append(new_received)
        self.success_data.append(new_success)
        self.error_data.append(new_error)
        
        # Redesenha o gráfico
        self.draw_chart()
    
    def draw_chart(self):
        """Desenha o gráfico com base no tipo selecionado."""
        self.figure.clear()
        
        if self.chart_type == "line":
            self.draw_line_chart()
        elif self.chart_type == "bar":
            self.draw_bar_chart()
        elif self.chart_type == "pie":
            self.draw_pie_chart()
        
        self.canvas.draw()
    
    def draw_line_chart(self):
        """Desenha um gráfico de linha."""
        ax = self.figure.add_subplot(111)
        
        # Desenha as linhas
        ax.plot(self.time_labels, self.received_data, 'b-', label='Recebidas')
        ax.plot(self.time_labels, self.success_data, 'g-', label='Sucesso')
        ax.plot(self.time_labels, self.error_data, 'r-', label='Erro')
        
        # Configura o gráfico
        ax.set_title('Apostas ao Longo do Tempo')
        ax.set_xlabel('Tempo (s)')
        ax.set_ylabel('Número de Apostas')
        ax.legend()
        
        # Ajusta o layout
        self.figure.tight_layout()
    
    def draw_bar_chart(self):
        """Desenha um gráfico de barras."""
        ax = self.figure.add_subplot(111)
        
        # Posições das barras
        x = np.arange(len(self.time_labels))
        width = 0.25
        
        # Desenha as barras
        ax.bar(x - width, self.received_data, width, label='Recebidas', color='blue')
        ax.bar(x, self.success_data, width, label='Sucesso', color='green')
        ax.bar(x + width, self.error_data, width, label='Erro', color='red')
        
        # Configura o gráfico
        ax.set_title('Comparação de Apostas')
        ax.set_xlabel('Tempo')
        ax.set_ylabel('Número de Apostas')
        ax.set_xticks(x)
        ax.set_xticklabels([str(t) for t in self.time_labels])
        ax.legend()
        
        # Ajusta o layout
        self.figure.tight_layout()
    
    def draw_pie_chart(self):
        """Desenha um gráfico de pizza."""
        ax = self.figure.add_subplot(111)
        
        # Dados para o gráfico de pizza (último ponto)
        success = self.success_data[-1] if self.success_data else 0
        error = self.error_data[-1] if self.error_data else 0
        
        # Se não houver dados, mostra um gráfico vazio
        if success == 0 and error == 0:
            ax.text(0.5, 0.5, 'Sem dados disponíveis', 
                   horizontalalignment='center', verticalalignment='center')
            return
        
        # Desenha o gráfico de pizza
        labels = ['Sucesso', 'Erro']
        sizes = [success, error]
        colors = ['green', 'red']
        explode = (0.1, 0)  # explode a primeira fatia
        
        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90)
        
        # Configura o gráfico
        ax.set_title('Distribuição de Apostas')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Ajusta o layout
        self.figure.tight_layout()
    
    def change_chart_type(self, chart_type):
        """
        Altera o tipo de gráfico.
        
        Args:
            chart_type: Tipo de gráfico ('line', 'bar', 'pie')
        """
        self.chart_type = chart_type
        self.draw_chart()

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
    
    def __init__(self, notification_system=None):
        super().__init__()
        self.notification_system = notification_system
        self.init_ui()
        
        # Timer para simular atualizações em tempo real
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_telegram_feed)
        self.update_timer.start(10000)  # Atualiza a cada 10 segundos
    
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
        
        # Carrega mensagens iniciais
        self.update_telegram_feed()
    
    def update_telegram_feed(self):
        """Atualiza o feed de mensagens do Telegram."""
        # Aqui seria implementada a lógica real de obtenção das mensagens
        # Esta é uma simulação para demonstração
        
        current_text = self.telegram_feed.toPlainText()
        
        # Adiciona novas mensagens no topo
        import random
        import datetime
        
        # Decide se vai adicionar uma nova mensagem
        if random.random() < 0.7:  # 70% de chance de adicionar uma nova mensagem
            # Gera uma nova mensagem aleatória
            races = ["Royal Ascot - Race 3", "Cheltenham - Race 5", "Epsom - Race 2", 
                    "Newmarket - Race 4", "Ascot - Race 1"]
            horses = ["Flying Thunder", "Dark Horse", "Lucky Strike", "Silver Bullet", 
                     "Golden Touch", "Night Rider", "Fast Lane", "Victory Lap"]
            odds = [1.8, 2.1, 2.5, 3.0, 3.2, 4.0, 4.5, 5.0]
            
            race = random.choice(races)
            horse = random.choice(horses)
            odd = random.choice(odds)
            now = datetime.datetime.now().strftime("%H:%M:%S")
            
            new_message = f"[{now}] Nova aposta recebida:\n"
            new_message += f"Corrida: {race}\n"
            new_message += f"Cavalo: {horse}\n"
            new_message += f"Odds: {odd}\n"
            new_message += f"Stake: 10\n"
            new_message += f"Tipo: win\n\n"
            
            # Adiciona a nova mensagem no topo
            self.telegram_feed.setText(new_message + current_text)
            
            # Adiciona uma notificação
            if self.notification_system:
                self.notification_system.add_notification(
                    "Nova Aposta Recebida",
                    f"Recebida aposta para {horse} na corrida {race}",
                    "info"
                )

class BetTrackingWidget(QWidget):
    """
    Widget para rastreamento de apostas processadas.
    """
    
    def __init__(self, notification_system=None):
        super().__init__()
        self.notification_system = notification_system
        self.init_ui()
        
        # Timer para simular atualizações em tempo real
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
        
        self.error_button = QPushButton("Erro")
        self.error_button.clicked.connect(lambda: self.filter_bets("error"))
        
        filter_layout.addWidget(self.all_button)
        filter_layout.addWidget(self.success_button)
        filter_layout.addWidget(self.error_button)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        self.setLayout(layout)
        
        # Carrega dados iniciais
        self.update_bet_tracking()
    
    def update_bet_tracking(self):
        """Atualiza o rastreamento de apostas."""
        # Aqui seria implementada a lógica real de obtenção das apostas
        # Esta é uma simulação para demonstração
        
        # Preserva o filtro atual
        current_filter = getattr(self, "current_filter", "all")
        
        # Decide se vai adicionar uma nova aposta
        import random
        if random.random() < 0.5:  # 50% de chance de adicionar uma nova aposta
            # Adiciona uma nova aposta aleatória
            import datetime
            
            # Dados de exemplo
            races = ["Royal Ascot - Race 3", "Cheltenham - Race 5", "Epsom - Race 2", 
                    "Newmarket - Race 4", "Ascot - Race 1"]
            horses = ["Flying Thunder", "Dark Horse", "Lucky Strike", "Silver Bullet", 
                     "Golden Touch", "Night Rider", "Fast Lane", "Victory Lap"]
            odds = [1.8, 2.1, 2.5, 3.0, 3.2, 4.0, 4.5, 5.0]
            stakes = [5, 10, 15, 20, 25, 50]
            statuses = ["Sucesso", "Erro"]
            
            # Gera uma nova aposta aleatória
            bet_id = f"{self.bets_table.rowCount() + 1:03d}"
            now = datetime.datetime.now().strftime("%H:%M:%S")
            race = random.choice(races)
            horse = random.choice(horses)
            odd = random.choice(odds)
            stake = random.choice(stakes)
            status = random.choice(statuses)
            
            # Adiciona a nova aposta à tabela
            row = self.bets_table.rowCount()
            self.bets_table.insertRow(row)
            
            # Preenche os dados da nova aposta
            self.bets_table.setItem(row, 0, QTableWidgetItem(bet_id))
            self.bets_table.setItem(row, 1, QTableWidgetItem(now))
            self.bets_table.setItem(row, 2, QTableWidgetItem(race))
            self.bets_table.setItem(row, 3, QTableWidgetItem(horse))
            self.bets_table.setItem(row, 4, QTableWidgetItem(str(odd)))
            self.bets_table.setItem(row, 5, QTableWidgetItem(str(stake)))
            
            status_item = QTableWidgetItem(status)
            if status == "Sucesso":
                status_item.setForeground(QColor("green"))
            else:
                status_item.setForeground(QColor("red"))
            self.bets_table.setItem(row, 6, status_item)
            
            # Adiciona uma notificação
            if self.notification_system:
                if status == "Sucesso":
                    self.notification_system.add_notification(
                        "Aposta Realizada com Sucesso",
                        f"Aposta em {horse} na corrida {race} foi realizada com sucesso",
                        "success"
                    )
                else:
                    self.notification_system.add_notification(
                        "Erro ao Realizar Aposta",
                        f"Falha ao realizar aposta em {horse} na corrida {race}",
                        "error"
                    )
        
        # Aplica o filtro atual
        self.filter_bets(current_filter)
    
    def filter_bets(self, filter_type):
        """
        Filtra as apostas exibidas na tabela.
        
        Args:
            filter_type: Tipo de filtro (all, success, error)
        """
        self.current_filter = filter_type
        
        for row in range(self.bets_table.rowCount()):
            status_item = self.bets_table.item(row, 6)
            if status_item is None:
                continue
                
            status = status_item.text()
            
            if filter_type == "all":
                self.bets_table.setRowHidden(row, False)
            elif filter_type == "success" and status == "Sucesso":
                self.bets_table.setRowHidden(row, False)
            elif filter_type == "error" and status == "Erro":
                self.bets_table.setRowHidden(row, False)
            else:
                self.bets_table.setRowHidden(row, True)

class DashboardTab(QWidget):
    """
    Aba de dashboard para monitoramento de apostas.
    """
    
    def __init__(self, notification_system=None):
        super().__init__()
        self.notification_system = notification_system
        self.init_ui()
        
        # Timer para atualizar estatísticas
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(5000)  # Atualiza a cada 5 segundos
    
    def init_ui(self):
        """Inicializa a interface da aba de dashboard."""
        layout = QVBoxLayout()
        
        # Cabeçalho com logo e título
        header_layout = QHBoxLayout()
        
        # Logo da Bolsa de Aposta
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               "assets", "images", "bolsa_de_aposta_logo.svg")
        
        logo_label = QLabel()
        logo_pixmap = QPixmap(logo_path)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setMaximumWidth(150)
        logo_label.setScaledContents(True)
        
        # Título do Dashboard
        dashboard_title = QLabel("Dashboard de Monitoramento")
        dashboard_title.setFont(QFont("Arial", 18, QFont.Bold))
        dashboard_title.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(dashboard_title, 1)  # Stretch factor 1
        
        layout.addLayout(header_layout)
        
        # Estatísticas gerais
        stats_group = QGroupBox("Estatísticas Gerais")
        stats_layout = QHBoxLayout()
        
        # Apostas recebidas
        received_box = QGroupBox("Apostas Recebidas")
        received_layout = QVBoxLayout()
        self.received_count = QLabel("0")
        self.received_count.setFont(QFont("Arial", 24, QFont.Bold))
        self.received_count.setAlignment(Qt.AlignCenter)
        received_layout.addWidget(self.received_count)
        received_box.setLayout(received_layout)
        
        # Apostas com sucesso
        success_box = QGroupBox("Apostas com Sucesso")
        success_layout = QVBoxLayout()
        self.success_count = QLabel("0")
        self.success_count.setFont(QFont("Arial", 24, QFont.Bold))
        self.success_count.setAlignment(Qt.AlignCenter)
        self.success_count.setStyleSheet("color: green;")
        success_layout.addWidget(self.success_count)
        success_box.setLayout(success_layout)
        
        # Apostas com erro
        error_box = QGroupBox("Apostas com Erro")
        error_layout = QVBoxLayout()
        self.error_count = QLabel("0")
        self.error_count.setFont(QFont("Arial", 24, QFont.Bold))
        self.error_count.setAlignment(Qt.AlignCenter)
        self.error_count.setStyleSheet("color: red;")
        error_layout.addWidget(self.error_count)
        error_box.setLayout(error_layout)
        
        stats_layout.addWidget(received_box)
        stats_layout.addWidget(success_box)
        stats_layout.addWidget(error_box)
        stats_group.setLayout(stats_layout)
        
        layout.addWidget(stats_group)
        
        # Gráfico estatístico
        self.chart_widget = StatisticsChart()
        layout.addWidget(self.chart_widget)
        
        # Splitter para dividir a tela entre monitoramento do Telegram e rastreamento de apostas
        splitter = QSplitter(Qt.Horizontal)
        
        # Widget de monitoramento do Telegram
        self.telegram_widget = TelegramMonitorWidget(self.notification_system)
        splitter.addWidget(self.telegram_widget)
        
        # Widget de rastreamento de apostas
        self.tracking_widget = BetTrackingWidget(self.notification_system)
        splitter.addWidget(self.tracking_widget)
        
        # Define tamanhos iniciais
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter, 1)  # Stretch factor 1
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Atualizar Dashboard")
        self.refresh_button.clicked.connect(self.refresh_dashboard)
        
        self.export_button = QPushButton("Exportar Dados")
        self.export_button.clicked.connect(self.export_data)
        
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Inicializa estatísticas
        self.update_statistics()
    
    def update_statistics(self):
        """Atualiza as estatísticas do dashboard."""
        # Aqui seria implementada a lógica real de obtenção das estatísticas
        # Esta é uma simulação para demonstração
        
        import random
        
        # Incrementa os contadores aleatoriamente
        current_received = int(self.received_count.text())
        current_success = int(self.success_count.text())
        current_error = int(self.error_count.text())
        
        # Adiciona de 0 a 2 novas apostas
        new_bets = random.randint(0, 2)
        if new_bets > 0:
            current_received += new_bets
            
            # Distribui entre sucesso e erro
            new_success = random.randint(0, new_bets)
            new_error = new_bets - new_success
            
            current_success += new_success
            current_error += new_error
        
        # Atualiza os contadores
        self.received_count.setText(str(current_received))
        self.success_count.setText(str(current_success))
        self.error_count.setText(str(current_error))
    
    def refresh_dashboard(self):
        """Atualiza todos os componentes do dashboard."""
        self.update_statistics()
        self.telegram_widget.update_telegram_feed()
        self.tracking_widget.update_bet_tracking()
        self.chart_widget.update_chart()
        
        QMessageBox.information(self, "Dashboard", "Dashboard atualizado com sucesso!")
    
    def export_data(self):
        """Exporta os dados do dashboard para um arquivo CSV."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Dados", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    # Escreve o cabeçalho
                    headers = ["ID", "Data/Hora", "Corrida", "Cavalo", "Odds", "Stake", "Status"]
                    f.write(','.join(headers) + '\n')
                    
                    # Escreve os dados da tabela de rastreamento
                    table = self.tracking_widget.bets_table
                    for row in range(table.rowCount()):
                        if not table.isRowHidden(row):
                            row_data = []
                            for col in range(table.columnCount()):
                                item = table.item(row, col)
                                if item is not None:
                                    # Escapa vírgulas nos valores
                                    value = item.text().replace(',', ';')
                                    row_data.append(value)
                                else:
                                    row_data.append("")
                            f.write(','.join(row_data) + '\n')
                
                QMessageBox.information(self, "Exportação", f"Dados exportados com sucesso para {file_path}")
                
                # Adiciona uma notificação
                if self.notification_system:
                    self.notification_system.add_notification(
                        "Dados Exportados",
                        f"Os dados foram exportados com sucesso para {os.path.basename(file_path)}",
                        "success"
                    )
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar dados: {e}")
                
                # Adiciona uma notificação de erro
                if self.notification_system:
                    self.notification_system.add_notification(
                        "Erro na Exportação",
                        f"Falha ao exportar dados: {str(e)}",
                        "error"
                    )

class ConfigTab(QWidget):
    """
    Aba de configurações da aplicação.
    """
    
    def __init__(self, notification_system=None):
        super().__init__()
        self.notification_system = notification_system
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface da aba de configurações."""
        layout = QVBoxLayout()
        
        # Grupo de configurações do Telegram
        telegram_group = QGroupBox("Configurações do Telegram")
        telegram_layout = QFormLayout()
        
        self.api_id_input = QLineEdit()
        self.api_hash_input = QLineEdit()
        self.bot_token_input = QLineEdit()
        self.group_id_input = QLineEdit()
        
        telegram_layout.addRow("API ID:", self.api_id_input)
        telegram_layout.addRow("API Hash:", self.api_hash_input)
        telegram_layout.addRow("Bot Token:", self.bot_token_input)
        telegram_layout.addRow("ID do Grupo:", self.group_id_input)
        
        telegram_group.setLayout(telegram_layout)
        
        # Grupo de configurações do Supabase
        supabase_group = QGroupBox("Configurações do Supabase")
        supabase_layout = QFormLayout()
        
        self.supabase_url_input = QLineEdit()
        self.supabase_key_input = QLineEdit()
        
        supabase_layout.addRow("URL:", self.supabase_url_input)
        supabase_layout.addRow("Chave:", self.supabase_key_input)
        
        supabase_group.setLayout(supabase_layout)
        
        # Grupo de configurações do navegador
        browser_group = QGroupBox("Configurações do Navegador")
        browser_layout = QFormLayout()
        
        self.browser_type_combo = QComboBox()
        self.browser_type_combo.addItems(["Chrome", "Firefox", "Edge"])
        
        self.headless_check = QCheckBox("Modo Headless")
        
        browser_layout.addRow("Navegador:", self.browser_type_combo)
        browser_layout.addRow("", self.headless_check)
        
        browser_group.setLayout(browser_layout)
        
        # Grupo de configurações da interface
        ui_group = QGroupBox("Configurações da Interface")
        ui_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Tema Claro", "Tema Escuro"])
        self.theme_combo.currentIndexChanged.connect(self.theme_changed)
        
        self.notifications_check = QCheckBox("Ativar Notificações")
        self.notifications_check.setChecked(True)
        
        self.mobile_check = QCheckBox("Otimizar para Dispositivos Móveis")
        
        ui_layout.addRow("Tema:", self.theme_combo)
        ui_layout.addRow("", self.notifications_check)
        ui_layout.addRow("", self.mobile_check)
        
        ui_group.setLayout(ui_layout)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Salvar Configurações")
        self.save_button.clicked.connect(self.save_config)
        
        self.test_button = QPushButton("Testar Conexões")
        self.test_button.clicked.connect(self.test_connections)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.test_button)
        
        # Adiciona os widgets ao layout principal
        layout.addWidget(telegram_group)
        layout.addWidget(supabase_group)
        layout.addWidget(browser_group)
        layout.addWidget(ui_group)
        layout.addLayout(buttons_layout)
        
        # Adiciona espaço em branco no final
        layout.addStretch()
        
        self.setLayout(layout)
    
    def theme_changed(self, index):
        """
        Manipula a mudança de tema.
        
        Args:
            index: Índice do tema selecionado
        """
        # Aqui seria implementada a lógica real de mudança de tema
        # Esta é uma simulação para demonstração
        
        # Emite um sinal para a janela principal
        window = self.window()
        if hasattr(window, "change_theme"):
            window.change_theme(index == 1)  # True para tema escuro
    
    def save_config(self):
        """Salva as configurações."""
        # Aqui seria implementada a lógica real de salvamento das configurações
        QMessageBox.information(self, "Configurações", "Configurações salvas com sucesso!")
        
        # Adiciona uma notificação
        if self.notification_system and self.notifications_check.isChecked():
            self.notification_system.add_notification(
                "Configurações Salvas",
                "As configurações foram salvas com sucesso",
                "success"
            )
    
    def test_connections(self):
        """Testa as conexões com as APIs."""
        # Aqui seria implementada a lógica real de teste das conexões
        QMessageBox.information(self, "Teste de Conexões", "Todas as conexões estão funcionando corretamente!")
        
        # Adiciona uma notificação
        if self.notification_system and self.notifications_check.isChecked():
            self.notification_system.add_notification(
                "Conexões Testadas",
                "Todas as conexões estão funcionando corretamente",
                "success"
            )

class BettingTab(QWidget):
    """
    Aba de configurações de apostas.
    """
    
    def __init__(self, notification_system=None):
        super().__init__()
        self.notification_system = notification_system
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface da aba de apostas."""
        layout = QVBoxLayout()
        
        # Grupo de configurações de apostas
        betting_group = QGroupBox("Configurações de Apostas")
        betting_layout = QFormLayout()
        
        self.default_stake_spin = QDoubleSpinBox()
        self.default_stake_spin.setRange(1, 1000)
        self.default_stake_spin.setValue(10)
        self.default_stake_spin.setSingleStep(1)
        
        self.min_stake_spin = QDoubleSpinBox()
        self.min_stake_spin.setRange(1, 100)
        self.min_stake_spin.setValue(5)
        self.min_stake_spin.setSingleStep(1)
        
        self.max_stake_spin = QDoubleSpinBox()
        self.max_stake_spin.setRange(10, 10000)
        self.max_stake_spin.setValue(100)
        self.max_stake_spin.setSingleStep(10)
        
        betting_layout.addRow("Stake Padrão:", self.default_stake_spin)
        betting_layout.addRow("Stake Mínimo:", self.min_stake_spin)
        betting_layout.addRow("Stake Máximo:", self.max_stake_spin)
        
        betting_group.setLayout(betting_layout)
        
        # Grupo de configurações avançadas
        advanced_group = QGroupBox("Configurações Avançadas")
        advanced_layout = QFormLayout()
        
        self.auto_login_check = QCheckBox("Login Automático")
        self.auto_login_check.setChecked(True)
        
        self.retry_count_spin = QSpinBox()
        self.retry_count_spin.setRange(1, 10)
        self.retry_count_spin.setValue(3)
        
        advanced_layout.addRow("", self.auto_login_check)
        advanced_layout.addRow("Tentativas de Retry:", self.retry_count_spin)
        
        advanced_group.setLayout(advanced_layout)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Salvar Configurações")
        self.save_button.clicked.connect(self.save_config)
        
        buttons_layout.addWidget(self.save_button)
        
        # Adiciona os widgets ao layout principal
        layout.addWidget(betting_group)
        layout.addWidget(advanced_group)
        layout.addLayout(buttons_layout)
        
        # Adiciona espaço em branco no final
        layout.addStretch()
        
        self.setLayout(layout)
    
    def save_config(self):
        """Salva as configurações de apostas."""
        # Aqui seria implementada a lógica real de salvamento das configurações
        QMessageBox.information(self, "Configurações de Apostas", "Configurações de apostas salvas com sucesso!")
        
        # Adiciona uma notificação
        if self.notification_system:
            self.notification_system.add_notification(
                "Configurações de Apostas Salvas",
                "As configurações de apostas foram salvas com sucesso",
                "success"
            )

class LogTab(QWidget):
    """
    Aba de visualização de logs.
    """
    
    def __init__(self, notification_system=None):
        super().__init__()
        self.notification_system = notification_system
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface da aba de logs."""
        layout = QVBoxLayout()
        
        # Área de texto para exibição de logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Atualizar Logs")
        self.refresh_button.clicked.connect(self.refresh_logs)
        
        self.clear_button = QPushButton("Limpar Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        
        self.export_button = QPushButton("Exportar Logs")
        self.export_button.clicked.connect(self.export_logs)
        
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.export_button)
        
        # Adiciona os widgets ao layout principal
        layout.addWidget(self.log_text)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Carrega os logs iniciais
        self.refresh_logs()
    
    def refresh_logs(self):
        """Atualiza a exibição de logs."""
        try:
            # Aqui seria implementada a lógica real de carregamento de logs
            import datetime
            now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            self.log_text.setText(f"Logs carregados em {now}\n\n" +
                                 "INFO: Sistema iniciado\n" +
                                 "INFO: Conectado ao Telegram\n" +
                                 "INFO: Conectado ao Supabase\n" +
                                 "INFO: Navegador inicializado\n" +
                                 "INFO: Aguardando apostas...\n" +
                                 f"INFO: Dashboard atualizado em {now}\n" +
                                 "INFO: Nova aposta recebida do Telegram\n" +
                                 "INFO: Processando aposta...\n" +
                                 "INFO: Aposta realizada com sucesso\n" +
                                 "INFO: Dados salvos no Supabase")
        except Exception as e:
            self.log_text.setText(f"Erro ao carregar logs: {e}")
            
            # Adiciona uma notificação de erro
            if self.notification_system:
                self.notification_system.add_notification(
                    "Erro nos Logs",
                    f"Falha ao carregar logs: {str(e)}",
                    "error"
                )
    
    def clear_logs(self):
        """Limpa a exibição de logs."""
        self.log_text.clear()
    
    def export_logs(self):
        """Exporta os logs para um arquivo de texto."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Logs", "", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.log_text.toPlainText())
                
                QMessageBox.information(self, "Exportação", f"Logs exportados com sucesso para {file_path}")
                
                # Adiciona uma notificação
                if self.notification_system:
                    self.notification_system.add_notification(
                        "Logs Exportados",
                        f"Os logs foram exportados com sucesso para {os.path.basename(file_path)}",
                        "success"
                    )
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar logs: {e}")
                
                # Adiciona uma notificação de erro
                if self.notification_system:
                    self.notification_system.add_notification(
                        "Erro na Exportação",
                        f"Falha ao exportar logs: {str(e)}",
                        "error"
                    )

class StatusThread(QThread):
    """
    Thread para monitorar o status do sistema.
    """
    status_update = pyqtSignal(str, str)  # (status_type, message)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
    
    def run(self):
        """Executa o monitoramento de status."""
        self.running = True
        while self.running:
            # Aqui seria implementada a lógica real de monitoramento
            # Por exemplo, verificar se o bot do Telegram está conectado
            # e se o navegador está funcionando corretamente
            
            # Simulação de status para demonstração
            self.status_update.emit("telegram", "Conectado")
            self.status_update.emit("browser", "Pronto")
            self.status_update.emit("database", "Conectado")
            
            # Aguarda 5 segundos antes da próxima verificação
            self.sleep(5)
    
    def stop(self):
        """Para o monitoramento de status."""
        self.running = False

class MainWindow(QMainWindow):
    """
    Janela principal da aplicação.
    """
    
    def __init__(self):
        super().__init__()
        
        # Inicializa o sistema de notificações
        self.notification_system = NotificationSystem(self)
        
        # Inicializa a interface
        self.init_ui()
        
        # Inicializa a thread de status
        self.status_thread = StatusThread(self)
        self.status_thread.status_update.connect(self.update_status)
        self.status_thread.start()
        
        # Tema padrão (claro)
        self.is_dark_theme = False
    
    def init_ui(self):
        """Inicializa a interface da janela principal."""
        self.setWindowTitle("RPA Apostas Esportivas - Bolsa de Aposta")
        self.setGeometry(100, 100, 1200, 900)
        
        # Widget central com layout principal
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Widget de abas
        self.tabs = QTabWidget()
        
        # Cria as abas
        self.dashboard_tab = DashboardTab(self.notification_system)
        self.config_tab = ConfigTab(self.notification_system)
        self.betting_tab = BettingTab(self.notification_system)
        self.log_tab = LogTab(self.notification_system)
        self.notifications_tab = NotificationsWidget(self.notification_system)
        
        # Adiciona as abas ao widget de abas
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.config_tab, "Configurações")
        self.tabs.addTab(self.betting_tab, "Apostas")
        self.tabs.addTab(self.log_tab, "Logs")
        self.tabs.addTab(self.notifications_tab, "Notificações")
        
        # Adiciona o widget de abas ao layout principal
        main_layout.addWidget(self.tabs)
        
        # Define o widget central
        self.setCentralWidget(central_widget)
        
        # Barra de status
        self.statusBar().showMessage("Pronto")
        
        # Adiciona widgets permanentes à barra de status
        self.telegram_status = QLabel("Telegram: Desconectado")
        self.browser_status = QLabel("Navegador: Inativo")
        self.database_status = QLabel("Banco de Dados: Desconectado")
        
        self.statusBar().addPermanentWidget(self.telegram_status)
        self.statusBar().addPermanentWidget(self.browser_status)
        self.statusBar().addPermanentWidget(self.database_status)
        
        # Barra de ferramentas
        toolbar = self.addToolBar("Controles")
        toolbar.setIconSize(Qt.QSize(24, 24))
        
        # Ações da barra de ferramentas
        start_action = QAction("Iniciar", self)
        start_action.triggered.connect(self.start_automation)
        toolbar.addAction(start_action)
        
        stop_action = QAction("Parar", self)
        stop_action.triggered.connect(self.stop_automation)
        toolbar.addAction(stop_action)
        
        toolbar.addSeparator()
        
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        toolbar.addAction(dashboard_action)
        
        settings_action = QAction("Configurações", self)
        settings_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        toolbar.addAction(settings_action)
        
        export_action = QAction("Exportar Dados", self)
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Ação para alternar o tema
        self.theme_action = QAction("Tema Escuro", self)
        self.theme_action.setCheckable(True)
        self.theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(self.theme_action)
        
        # Menu principal
        menu_bar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menu_bar.addMenu("Arquivo")
        
        export_menu_action = QAction("Exportar Dados", self)
        export_menu_action.triggered.connect(self.export_data)
        file_menu.addAction(export_menu_action)
        
        export_logs_action = QAction("Exportar Logs", self)
        export_logs_action.triggered.connect(self.log_tab.export_logs)
        file_menu.addAction(export_logs_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Visualizar
        view_menu = menu_bar.addMenu("Visualizar")
        
        theme_menu_action = QAction("Tema Escuro", self)
        theme_menu_action.setCheckable(True)
        theme_menu_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_menu_action)
        
        view_menu.addSeparator()
        
        for i, tab_name in enumerate(["Dashboard", "Configurações", "Apostas", "Logs", "Notificações"]):
            tab_action = QAction(tab_name, self)
            tab_action.triggered.connect(lambda checked, index=i: self.tabs.setCurrentIndex(index))
            view_menu.addAction(tab_action)
        
        # Menu Ajuda
        help_menu = menu_bar.addMenu("Ajuda")
        
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Adiciona uma notificação de boas-vindas
        self.notification_system.add_notification(
            "Bem-vindo ao RPA Apostas Esportivas",
            "O sistema foi iniciado com sucesso e está pronto para uso",
            "info"
        )
    
    def update_status(self, status_type, message):
        """
        Atualiza o status na barra de status.
        
        Args:
            status_type: Tipo de status (telegram, browser, database)
            message: Mensagem de status
        """
        if status_type == "telegram":
            self.telegram_status.setText(f"Telegram: {message}")
        elif status_type == "browser":
            self.browser_status.setText(f"Navegador: {message}")
        elif status_type == "database":
            self.database_status.setText(f"Banco de Dados: {message}")
    
    def start_automation(self):
        """Inicia a automação de apostas."""
        # Aqui seria implementada a lógica real de inicialização da automação
        QMessageBox.information(self, "Automação", "Iniciando automação de apostas...")
        self.statusBar().showMessage("Automação iniciada")
        
        # Atualiza o dashboard após iniciar a automação
        self.dashboard_tab.refresh_dashboard()
        
        # Adiciona uma notificação
        self.notification_system.add_notification(
            "Automação Iniciada",
            "A automação de apostas foi iniciada com sucesso",
            "success"
        )
    
    def stop_automation(self):
        """Para a automação de apostas."""
        # Aqui seria implementada a lógica real de parada da automação
        QMessageBox.information(self, "Automação", "Parando automação de apostas...")
        self.statusBar().showMessage("Automação parada")
        
        # Adiciona uma notificação
        self.notification_system.add_notification(
            "Automação Parada",
            "A automação de apostas foi interrompida",
            "warning"
        )
    
    def export_data(self):
        """Exporta os dados do dashboard."""
        # Redireciona para a função de exportação do dashboard
        self.dashboard_tab.export_data()
    
    def toggle_theme(self, checked):
        """
        Alterna entre os temas claro e escuro.
        
        Args:
            checked: Se True, ativa o tema escuro; caso contrário, ativa o tema claro
        """
        self.change_theme(checked)
        
        # Atualiza o texto da ação
        self.theme_action.setText("Tema Claro" if checked else "Tema Escuro")
    
    def change_theme(self, is_dark):
        """
        Muda o tema da aplicação.
        
        Args:
            is_dark: Se True, aplica o tema escuro; caso contrário, aplica o tema claro
        """
        self.is_dark_theme = is_dark
        
        # Aplica o tema
        app = QApplication.instance()
        ThemeManager.apply_theme(app, is_dark)
        
        # Atualiza o texto da ação
        self.theme_action.setText("Tema Claro" if is_dark else "Tema Escuro")
        self.theme_action.setChecked(is_dark)
        
        # Adiciona uma notificação
        theme_name = "escuro" if is_dark else "claro"
        self.notification_system.add_notification(
            "Tema Alterado",
            f"O tema da aplicação foi alterado para {theme_name}",
            "info"
        )
    
    def show_about(self):
        """Exibe a caixa de diálogo 'Sobre'."""
        QMessageBox.about(
            self,
            "Sobre RPA Apostas Esportivas",
            "<h1>RPA Apostas Esportivas</h1>"
            "<p>Versão 1.0</p>"
            "<p>Um sistema de automação para apostas esportivas utilizando RPA.</p>"
            "<p>Desenvolvido para Bolsa de Aposta.</p>"
            "<p>&copy; 2025 Todos os direitos reservados.</p>"
        )
    
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela."""
        # Para a thread de status
        self.status_thread.stop()
        self.status_thread.wait()
        
        # Aceita o evento de fechamento
        event.accept()

def run_gui():
    """
    Função principal para executar a interface gráfica.
    """
    app = QApplication(sys.argv)
    
    # Aplica o tema padrão (claro)
    ThemeManager.apply_theme(app, False)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

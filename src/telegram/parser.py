"""
Módulo para processamento de mensagens do Telegram e extração de padrões de apostas.

Este módulo contém funções e classes para analisar o conteúdo das mensagens
do Telegram e extrair informações estruturadas sobre apostas esportivas.
"""
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger


@dataclass
class BetData:
    """Classe para armazenar dados estruturados de uma aposta."""
    race: str
    horse_name: str
    odds: float
    stake: Optional[float] = None
    bet_type: str = "win"
    raw_message: str = ""
    status: str = "pending"
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte os dados da aposta para um dicionário."""
        return {
            "race": self.race,
            "horse_name": self.horse_name,
            "odds": self.odds,
            "stake": self.stake,
            "bet_type": self.bet_type,
            "raw_message": self.raw_message,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class MessageParser:
    """
    Classe para analisar mensagens e extrair informações de apostas.
    """
    
    # Padrões de expressões regulares para diferentes formatos de mensagens
    PATTERNS = [
        # Padrão 1: Formato estruturado com rótulos claros
        r"Corrida:\s*(.+?)\s*\n.*?Cavalo:\s*(.+?)\s*\n.*?Odds:\s*(\d+\.?\d*)",
        
        # Padrão 2: Formato mais compacto
        r"Aposta:\s*(.+?)\s*-\s*(.+?)\s*@\s*(\d+\.?\d*)",
        
        # Padrão 3: Formato alternativo
        r"Corrida\s*(.+?)\s*:\s*(.+?)\s*\((\d+\.?\d*)\)"
    ]
    
    @classmethod
    def parse_message(cls, message_text: str) -> Optional[BetData]:
        """
        Analisa uma mensagem e tenta extrair informações de aposta.
        
        Args:
            message_text: Texto da mensagem a ser analisada.
            
        Returns:
            BetData: Objeto com dados da aposta ou None se não for uma aposta válida.
        """
        for pattern in cls.PATTERNS:
            try:
                match = re.search(pattern, message_text, re.DOTALL)
                if match:
                    race = match.group(1).strip()
                    horse_name = match.group(2).strip()
                    odds = float(match.group(3).strip())
                    
                    # Extrai stake se disponível
                    stake_match = re.search(r"Stake:\s*(\d+\.?\d*)", message_text)
                    stake = float(stake_match.group(1)) if stake_match else None
                    
                    # Extrai tipo de aposta se disponível
                    bet_type_match = re.search(r"Tipo:\s*(.+?)(?:\n|$)", message_text)
                    bet_type = bet_type_match.group(1).strip() if bet_type_match else "win"
                    
                    return BetData(
                        race=race,
                        horse_name=horse_name,
                        odds=odds,
                        stake=stake,
                        bet_type=bet_type,
                        raw_message=message_text,
                        created_at=datetime.now()
                    )
            except Exception as e:
                logger.debug(f"Falha ao analisar com padrão {pattern}: {e}")
                continue
        
        # Tenta uma abordagem mais flexível se os padrões anteriores falharem
        try:
            # Busca por palavras-chave e proximidade
            if "cavalo" in message_text.lower() and "corrida" in message_text.lower():
                # Tenta encontrar o nome do cavalo
                horse_lines = [line for line in message_text.split('\n') if "cavalo" in line.lower()]
                race_lines = [line for line in message_text.split('\n') if "corrida" in line.lower()]
                odds_lines = [line for line in message_text.split('\n') if "odds" in line.lower() or "@" in line]
                
                if horse_lines and race_lines:
                    horse_name = horse_lines[0].split(":", 1)[1].strip() if ":" in horse_lines[0] else horse_lines[0].replace("cavalo", "", flags=re.IGNORECASE).strip()
                    race = race_lines[0].split(":", 1)[1].strip() if ":" in race_lines[0] else race_lines[0].replace("corrida", "", flags=re.IGNORECASE).strip()
                    
                    # Tenta extrair odds
                    odds = None
                    if odds_lines:
                        odds_text = odds_lines[0]
                        odds_match = re.search(r"(\d+\.?\d*)", odds_text)
                        if odds_match:
                            odds = float(odds_match.group(1))
                    
                    if horse_name and race and odds:
                        return BetData(
                            race=race,
                            horse_name=horse_name,
                            odds=odds,
                            raw_message=message_text,
                            created_at=datetime.now()
                        )
        except Exception as e:
            logger.error(f"Erro na análise flexível: {e}")
        
        return None


def is_bet_message(message_text: str) -> bool:
    """
    Verifica se uma mensagem contém informações de aposta.
    
    Args:
        message_text: Texto da mensagem a ser verificada.
        
    Returns:
        bool: True se a mensagem parece conter uma aposta, False caso contrário.
    """
    # Palavras-chave que indicam uma possível mensagem de aposta
    keywords = ["aposta", "corrida", "cavalo", "odds", "stake", "bet", "race", "horse"]
    
    # Verifica se pelo menos duas palavras-chave estão presentes
    keyword_count = sum(1 for keyword in keywords if keyword.lower() in message_text.lower())
    
    # Verifica se há pelo menos um número que pode ser odds
    has_number = bool(re.search(r"@\s*\d+\.?\d*|\d+\.?\d*\s*@|odds\s*\d+\.?\d*|\d+\.?\d*\s*odds", message_text.lower()))
    
    return keyword_count >= 2 and has_number

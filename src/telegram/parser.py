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
        r"Corrida\s*(.+?)\s*:\s*(.+?)\s*\((\d+\.?\d*)\)",
        
        # Padrão 4: Formato simples com nome do cavalo e odds
        r"(?:Apostar em|Bet on)?\s*(.+?)\s*(?:na corrida|in race)\s*(.+?)\s*(?:@|odds)\s*(\d+\.?\d*)",
        
        # Padrão 5: Formato inverso com corrida primeiro
        r"(?:Corrida|Race)\s*(.+?)\s*(?:cavalo|horse)\s*(.+?)\s*(?:@|odds)\s*(\d+\.?\d*)"
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
        # Registra a mensagem para depuração
        logger.debug(f"Analisando mensagem: {message_text[:100]}...")
        
        for pattern in cls.PATTERNS:
            try:
                match = re.search(pattern, message_text, re.DOTALL | re.IGNORECASE)
                if match:
                    # Dependendo do padrão, a ordem dos grupos pode variar
                    if "na corrida" in pattern or "in race" in pattern:
                        # Padrão 4: cavalo, corrida, odds
                        horse_name = match.group(1).strip()
                        race = match.group(2).strip()
                    else:
                        # Padrões 1, 2, 3, 5: corrida, cavalo, odds
                        race = match.group(1).strip()
                        horse_name = match.group(2).strip()
                    
                    odds = float(match.group(3).strip())
                    
                    # Extrai stake se disponível
                    stake_match = re.search(r"(?:Stake|stake|STAKE):\s*(\d+\.?\d*)", message_text, re.IGNORECASE)
                    stake = float(stake_match.group(1)) if stake_match else None
                    
                    # Extrai tipo de aposta se disponível
                    bet_type_match = re.search(r"(?:Tipo|tipo|TYPE|type):\s*(.+?)(?:\n|$)", message_text, re.IGNORECASE)
                    bet_type = bet_type_match.group(1).strip() if bet_type_match else "win"
                    
                    logger.info(f"Aposta extraída: {horse_name} na corrida {race} @ {odds}")
                    
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
            message_lower = message_text.lower()
            if ("cavalo" in message_lower or "horse" in message_lower) and ("corrida" in message_lower or "race" in message_lower):
                # Tenta encontrar o nome do cavalo
                horse_lines = [line for line in message_text.split('\n') 
                              if "cavalo" in line.lower() or "horse" in line.lower()]
                race_lines = [line for line in message_text.split('\n') 
                             if "corrida" in line.lower() or "race" in line.lower()]
                odds_lines = [line for line in message_text.split('\n') 
                             if "odds" in line.lower() or "@" in line]
                
                if horse_lines and race_lines:
                    # Extrai nome do cavalo
                    if ":" in horse_lines[0]:
                        horse_name = horse_lines[0].split(":", 1)[1].strip()
                    else:
                        horse_name = re.sub(r'(?:cavalo|horse)', '', horse_lines[0], flags=re.IGNORECASE).strip()
                    
                    # Extrai nome da corrida
                    if ":" in race_lines[0]:
                        race = race_lines[0].split(":", 1)[1].strip()
                    else:
                        race = re.sub(r'(?:corrida|race)', '', race_lines[0], flags=re.IGNORECASE).strip()
                    
                    # Tenta extrair odds
                    odds = None
                    if odds_lines:
                        odds_text = odds_lines[0]
                        odds_match = re.search(r"(\d+\.?\d*)", odds_text)
                        if odds_match:
                            odds = float(odds_match.group(1))
                    
                    if horse_name and race and odds:
                        logger.info(f"Aposta extraída (método flexível): {horse_name} na corrida {race} @ {odds}")
                        return BetData(
                            race=race,
                            horse_name=horse_name,
                            odds=odds,
                            raw_message=message_text,
                            created_at=datetime.now()
                        )
        except Exception as e:
            logger.error(f"Erro na análise flexível: {e}")
        
        # Última tentativa: busca por qualquer número que possa ser odds e texto próximo
        try:
            # Busca por padrões de odds (@X.XX)
            odds_matches = re.finditer(r'@\s*(\d+\.?\d*)', message_text)
            for odds_match in odds_matches:
                odds = float(odds_match.group(1))
                # Pega o contexto antes e depois do odds
                start_pos = max(0, odds_match.start() - 100)
                end_pos = min(len(message_text), odds_match.end() + 100)
                context = message_text[start_pos:end_pos]
                
                # Tenta identificar o nome do cavalo e da corrida no contexto
                words = re.split(r'[\s,.]', context)
                words = [w for w in words if len(w) > 2]  # Remove palavras muito curtas
                
                if len(words) >= 4:
                    # Assume que o nome do cavalo está próximo do odds
                    horse_name = " ".join(words[len(words)//2-2:len(words)//2])
                    race = " ".join(words[:2])
                    
                    logger.info(f"Aposta extraída (método de último recurso): {horse_name} na corrida {race} @ {odds}")
                    return BetData(
                        race=race,
                        horse_name=horse_name,
                        odds=odds,
                        raw_message=message_text,
                        created_at=datetime.now()
                    )
        except Exception as e:
            logger.error(f"Erro na análise de último recurso: {e}")
        
        logger.warning(f"Não foi possível extrair dados de aposta da mensagem: {message_text[:50]}...")
        return None


def is_bet_message(message_text: str) -> bool:
    """
    Verifica se uma mensagem contém informações de aposta.
    
    Args:
        message_text: Texto da mensagem a ser verificada.
        
    Returns:
        bool: True se a mensagem parece conter uma aposta, False caso contrário.
    """
    # Normaliza o texto para facilitar a busca
    text = message_text.lower()
    
    # Palavras-chave que indicam uma possível mensagem de aposta (português e inglês)
    keywords = [
        "aposta", "corrida", "cavalo", "odds", "stake", 
        "bet", "race", "horse", "win", "place", "show",
        "jockey", "hipódromo", "track", "pista", "jóquei"
    ]
    
    # Verifica se pelo menos duas palavras-chave estão presentes
    keyword_count = sum(1 for keyword in keywords if keyword in text)
    
    # Padrões que indicam odds
    odds_patterns = [
        r'@\s*\d+\.?\d*',           # @2.5
        r'\d+\.?\d*\s*@',           # 2.5@
        r'odds\s*\d+\.?\d*',        # odds 2.5
        r'\d+\.?\d*\s*odds',        # 2.5 odds
        r'odds:\s*\d+\.?\d*',       # odds: 2.5
        r'\(\s*\d+\.?\d*\s*\)',     # (2.5)
        r'cotação\s*\d+\.?\d*',     # cotação 2.5
        r'cota\s*\d+\.?\d*'         # cota 2.5
    ]
    
    # Verifica se há pelo menos um padrão de odds
    has_odds = any(re.search(pattern, text) for pattern in odds_patterns)
    
    # Verifica se a mensagem tem um comprimento mínimo
    min_length = len(text) > 10
    
    # Verifica se a mensagem tem um formato estruturado (linhas separadas)
    structured_format = '\n' in message_text
    
    # Verifica se a mensagem contém padrões específicos de apostas
    specific_patterns = any([
        "corrida:" in text,
        "cavalo:" in text,
        "aposta:" in text,
        "race:" in text,
        "horse:" in text,
        "bet:" in text
    ])
    
    # Combina os critérios
    is_bet = (
        (keyword_count >= 2 and has_odds) or  # Critério básico
        (keyword_count >= 1 and has_odds and specific_patterns) or  # Padrões específicos
        (structured_format and has_odds and keyword_count >= 1)  # Formato estruturado
    ) and min_length
    
    if is_bet:
        logger.info(f"Mensagem identificada como aposta: {message_text[:50]}...")
    else:
        logger.debug(f"Mensagem não identificada como aposta: {message_text[:50]}...")
    
    return is_bet

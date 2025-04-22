"""
Módulo de validadores para a interface gráfica.

Este módulo contém funções para validar entradas de usuário
na interface gráfica do sistema de automação de apostas.
"""
import re
from urllib.parse import urlparse


def is_valid_url(url):
    """
    Verifica se uma URL é válida.
    
    Args:
        url: String contendo a URL a ser validada.
        
    Returns:
        bool: True se a URL for válida, False caso contrário.
    """
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def is_valid_api_key(key):
    """
    Verifica se uma chave de API é válida.
    
    Args:
        key: String contendo a chave de API a ser validada.
        
    Returns:
        bool: True se a chave de API for válida, False caso contrário.
    """
    if not key:
        return False
    
    # Verifica se a chave tem pelo menos 20 caracteres e contém apenas caracteres válidos
    return len(key) >= 20 and bool(re.match(r'^[a-zA-Z0-9._-]+$', key))


def is_valid_telegram_api_id(api_id):
    """
    Verifica se um API ID do Telegram é válido.
    
    Args:
        api_id: String contendo o API ID a ser validado.
        
    Returns:
        bool: True se o API ID for válido, False caso contrário.
    """
    if not api_id:
        return False
    
    # API ID do Telegram é um número inteiro
    try:
        api_id_int = int(api_id)
        return api_id_int > 0
    except:
        return False


def is_valid_telegram_api_hash(api_hash):
    """
    Verifica se um API Hash do Telegram é válido.
    
    Args:
        api_hash: String contendo o API Hash a ser validado.
        
    Returns:
        bool: True se o API Hash for válido, False caso contrário.
    """
    if not api_hash:
        return False
    
    # API Hash do Telegram é uma string hexadecimal de 32 caracteres
    return len(api_hash) == 32 and bool(re.match(r'^[a-fA-F0-9]+$', api_hash))


def is_valid_telegram_bot_token(token):
    """
    Verifica se um token de bot do Telegram é válido.
    
    Args:
        token: String contendo o token a ser validado.
        
    Returns:
        bool: True se o token for válido, False caso contrário.
    """
    if not token:
        return False
    
    # Token de bot do Telegram segue o formato: 123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ
    return bool(re.match(r'^\d+:[a-zA-Z0-9_-]+$', token))


def is_valid_telegram_group_id(group_id):
    """
    Verifica se um ID de grupo do Telegram é válido.
    
    Args:
        group_id: String contendo o ID de grupo a ser validado.
        
    Returns:
        bool: True se o ID de grupo for válido, False caso contrário.
    """
    if not group_id:
        return False
    
    # ID de grupo do Telegram é um número inteiro, possivelmente negativo
    try:
        group_id_int = int(group_id)
        return True
    except:
        return False


def is_valid_stake(stake, min_stake=1, max_stake=10000):
    """
    Verifica se um valor de stake é válido.
    
    Args:
        stake: Valor de stake a ser validado.
        min_stake: Valor mínimo permitido.
        max_stake: Valor máximo permitido.
        
    Returns:
        bool: True se o stake for válido, False caso contrário.
    """
    try:
        stake_float = float(stake)
        return min_stake <= stake_float <= max_stake
    except:
        return False

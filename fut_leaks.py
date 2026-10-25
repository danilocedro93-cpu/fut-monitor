"""Monitor de vazamentos de FC Ultimate Team - versao hibrida.

1) Filtro gratuito por palavras-chave (pontuacao) descarta a maioria dos posts.
2) So os posts promissores vao para o Claude (barato) classificar.
3) Alertas chegam no Telegram.
Sem ANTHROPIC_API_KEY (ou se a API falhar), cai para o modo so palavras-chave.
"""
import json
import os
import re
from pathlib import Path

import anthropic
import feedparser
import requests
from bs4 import BeautifulSoup

# ----------------------------- CONFIGURACAO -----------------------------
REDDIT_FEEDS = [
    "https://www.reddit.com/r/fut/new/.rss",
    "https://www.reddit.com/r/EASportsFC/new/.rss",
    "https://www.reddit.com/r/fut/search.rss?q=leak&restrict_sr=1&sort=new",
]

# Canais publicos do Telegram (sem @). Ex.: ["nomedocanal"]
TELEGRAM_CHANNELS = []
# Canais em que voce mais confia (ganham pontos extras). Devem estar na lista acima.
TRUSTED_CHANNELS = []

STRONG = ["leak", "leaks", "leaked", "vazou", "vazamento", "vazado",
          "datamine", "datamined", "dataminer", "insider"]
CONTENT = ["sbc", "promo", "evolution", "evolutions", "evo", "upgrade",
           "objective", "objectives", "icon", "hero", "totw", "toty", "tots",
           "release date", "overall", "ovr", "rating", "ratings", "pack"]
NEGATIVE = ["how do i", "help", "anyone else", "rant", "meme", "clip",
            "glitch", "bug", "disconnect", "server issue", "my pack"]

PRE_SCORE = int(os.getenv("PRE_SCORE", "3"))        # minimo para ir ao Claude
MIN_SCORE = int(os.getenv("MIN_SCORE", "5"))        # alerta no modo sem IA
MIN_CONFIDENCE = int(os.getenv("MIN_CONFIDENCE", "6"))  # 0 a 10, alerta com IA
MAX_AI_PER_RUN = 15

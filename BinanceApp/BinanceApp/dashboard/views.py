from sqlite3.dbapi2 import Timestamp
from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from django.template import loader
from datetime import datetime
from .models import Log
# Create your views here.
def compare(e):
  return e["percent"]
binance_symbols = ["BTCUSDT", "SHIBUSDT", "ETHUSDT", "BUSDUSDT", "SANDUSDT", "SOLUSDT", "IOTXUSDT", "DOTUSDT",
"XRPUSDT", "BNBUSDT", "MANAUSDT", "ARPAUSDT", "ADAUSDT", "TRXUSDT", "AVAXUSDT", "AXSUSDT", "DOGEUSDT", "OMGUSDT", "LRCUSDT", "HOTUSDT",
"LUNAUSDT", "SLPUSDT", "FIDAUSDT", "MATICUSDT", "FTMUSDT", "FILUSDT", "ARUSDT", "BADGERUSDT", "USDCUSDT", "ATOMUSDT", "VETUSDT",
"BETAUSDT", "LINKUSDT", "CHZUSDT", "LTCUSDT", "CHRUSDT", "EOSUSDT", "SRMUSDT", "MKRUSDT", "EGLDUSDT", "C98USDT", "THETAUSDT", "IOSTUSDT", "BTTUSDT", "ICPUSDT",
"TLMUSDT", "ALGOUSDT", "ENJUSDT"]
def index(request):
    try:
        now = datetime.now()
        coins_1m = []
        coins_5m = []
        coins_15m = []
        coins_1h = []
        for symbol in binance_symbols:
            log = Log.objects.filter(symbol=symbol, interval="1m").order_by('-timestamp')[:2]
            if log.count() > 1:
                coins_1m.append({"symbol": symbol[0:-4], "volume": (round(log[0].volume, 2)), "percent": (round((log[0].volume - log[1].volume) * 100 / log[1].volume, 2))})
            log = Log.objects.filter(symbol=symbol, interval="5m").order_by('-timestamp')[:2]
            if log.count() > 1:
                coins_5m.append({"symbol": symbol[0:-4], "volume": (round(log[0].volume, 2)), "percent": (round((log[0].volume - log[1].volume) * 100 / log[1].volume, 2))})
            log = Log.objects.filter(symbol=symbol, interval="15m").order_by('-timestamp')[:2]
            if log.count() > 1:
                coins_15m.append({"symbol": symbol[0:-4], "volume": (round(log[0].volume, 2)), "percent": (round((log[0].volume - log[1].volume) * 100 / log[1].volume, 2))})
            log = Log.objects.filter(symbol=symbol, interval="1h").order_by('-timestamp')[:2]
            if log.count() > 1:
                coins_1h.append({"symbol": symbol[0:-4], "volume": (round(log[0].volume, 2)), "percent": (round((log[0].volume - log[1].volume) * 100 / log[1].volume, 2))})
        coins_1m.sort(reverse=True, key=compare)
        coins_5m.sort(reverse=True, key=compare)
        coins_15m.sort(reverse=True, key=compare)
        coins_1h.sort(reverse=True, key=compare)
        template = loader.get_template('index.html')
        context = {
            'coins_1m': coins_1m[0:20],
            'coins_5m': coins_5m[0:20],
            'coins_15m': coins_15m[0:20],
            'coins_1h': coins_1h[0:20],
            'date': now.strftime("%m/%d/%Y")
        }
    except Log.DoesNotExist:
        raise Http404("Sorry, try again when it finishes loading data...")
    return HttpResponse(template.render(context, request))
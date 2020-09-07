

from json2xml.utils import readfromstring
from json2xml import json2xml
from pandas import read_json
import requests
import argparse
import json
import sys


yahoo_api_request = 'https://apidojo-yahoo-finance-v1.p.rapidapi.com/{}/{}'


class AuthAction(argparse.Action):

    def __init__(self,option_strings,dest,help,default=None):
        # Come destinazione prendi la chiave query 
        super().__init__(option_strings,dest='auth',help=help, required=True, type=str)
        # Salva il nome della destinazione
        self.name = dest

    # Questo metodo converte direttamente la lista di codici in una stringa
    def __call__(self,parser,namespace,values,option_string=None):
        # Se query è nulla, ritorna un dizionario vuoto altrimenti ritorna il dizionario delle query
        query = (lambda auth: auth if auth is not None else {})(vars(namespace).get('auth'))
        # Aggiorna il dizionario con la nuova query formata dal nome e dal valore passato come argomento
        query.update({self.name: values})
        # Aggiorna il namespace
        setattr(namespace, 'auth', query)


class QueryAction(argparse.Action):

    def __init__(self,option_strings,dest,help):
        # Come destinazione prendi la chiave query 
        super().__init__(option_strings,dest='query',help=help, required=False, type=str)
        # Salva il nome della destinazione
        self.name = dest

    # Questo metodo converte direttamente la lista di codici in una stringa
    def __call__(self,parser,namespace,values,option_string=None):
        # Se la query è nulla, ritorna un dizionario vuoto altrimenti ritorna il dizionario delle query
        query = (lambda query: query if query is not None else {})(vars(namespace).get('query'))
        # Aggiorna il dizionario con la nuova query formata dal nome e dal valore passato come argomento
        query.update({self.name: values})
        # Aggiorna il namespace
        setattr(namespace, 'query', query)


def to_json(json_obj):
    # Estrai il risultato ed eventuali errori dal json
    result, error = (json_obj.pop(list(json_obj.keys())[-1])).values()
    # Assicurati non ci siano errori nel json
    assert error is None, Exception(error)
    # Ritorna il risultato sotto forma di stringa json
    return result


def to_txt(json_obj):
    # Costruisco la stringa json
    return json.dumps(to_json(json_obj))


def to_csv(json_obj):
    # Costruisco la stringa json
    json_str = to_txt(json_obj)
    # Converto la stringa json in csv
    return read_json(json_str).to_csv()


def to_xml(json_obj):
    # Costruisco la stringa json
    json_str = to_txt(json_obj)
    # Ottieni l'xml dalla stringa json
    data = readfromstring(json_str)
    # Costruisco l'xml
    return json2xml.Json2xml(data).to_xml()


def main():

    parser = argparse.ArgumentParser('Yahoo finance api query')
    # Crea un gruppo nel parser per i valori necessari per l'autenticazione
    auth = parser.add_argument_group('Auth')
    auth.add_argument('--host',dest='x-rapidapi-host',action=AuthAction,default='apidojo-yahoo-finance-v1.p.rapidapi.com',help='Insert host to request')
    auth.add_argument('--key',dest='x-rapidapi-key',action=AuthAction,help='Insert key')    
    # Crea dei subparsers
    subparsers = parser.add_subparsers(dest='Database')
    subparsers.required = True
    # Crea un sottogruppo contenente gli elementi per le richieste di Market
    market = subparsers.add_parser('market',help='Select market request')
    mchoice = market.add_mutually_exclusive_group()
    mchoice.add_argument('--summary',dest='request',action='store_const',const='get-summary',help='Get live summary information at the request time')
    mchoice.add_argument('--movers',dest='request',action='store_const',const='get-movers',help='Get live summary information at the request time')
    mchoice.add_argument('--quotes',dest='request',action='store_const',const='get-quotes',help='The quotes by symbols')
    mchoice.add_argument('--charts',dest='request',action='store_const',const='get-charts',help='Get data to draw chart for a specific symbol and its comparisons')
    mchoice.add_argument('--auto-complete',dest='request',action='store_const',const='auto-complete',help='Get auto complete suggestion for stocks')
    # Crea un sottogruppo contenente gli elementi per le richieste di Stock
    stock = subparsers.add_parser('stock',help='Select stock request')
    schoice = stock.add_mutually_exclusive_group()
    schoice.add_argument('--detail',dest='request',action='store_const',const='get-detail',help='Get detail information of each stock')
    schoice.add_argument('--histories',dest='request',action='store_const',const='get-histories',help='Get stock histories to draw chart')
    schoice.add_argument('--news',dest='request',action='store_const',const='get-news',help='Get latest news related to a symbol, the result may be empty if there is no news in that region')
    schoice.add_argument('--holders',dest='request',action='store_const',const='get-holders',help='Get holders tab information')
    schoice.add_argument('--financials',dest='request',action='store_const',const='get-financials',help='Get financials tab information')
    schoice.add_argument('--options',dest='request',action='store_const',const='get-options',help='Get options tab information')
    schoice.add_argument('--analysis',dest='request',action='store_const',const='get-analysis',help='Get analysis tab information')
    schoice.add_argument('--hist-data',dest='request',action='store_const',const='get-historical-data',help='Get historical data tab information')
    schoice.add_argument('--statistics',dest='request',action='store_const',const='get-statistics',help='Get statistics tab information')
    schoice.add_argument('--chart',dest='request',action='store_const',const='get-chart',help='Get data to draw full screen chart')
    schoice.add_argument('--newsfeed',dest='request',action='store_const',const='get-newsfeed',help='Get general latest newsfeed or specific newsfeed by symbol')
    schoice.add_argument('--timeseries',dest='request',action='store_const',const='get-timeseries',help='Get financial data quarterly for more detail ')
    schoice.add_argument('--summary',dest='request',action='store_const',const='get-summary',help='Get summary tab information')
    schoice.add_argument('--balance-sheet',dest='request',action='store_const',const='get-balance-sheet',help='Get data in Balance Sheet tab')
    schoice.add_argument('--profile',dest='request',action='store_const',const='get-profile',help='Get profile tab information')
    # Crea un gruppo per la query
    query = parser.add_argument_group('Query')
    query.add_argument('--region',dest='region',action=QueryAction,help='The main region to get summary information from')
    query.add_argument('--lang',dest='lang',action=QueryAction,help='The language codes')
    query.add_argument('--symbols',dest='symbols',action=QueryAction,help='The symbols separated by comma to get information')
    query.add_argument('--count',dest='count',action=QueryAction,help='The number of quotes to display in day gainers / losers / activies')
    query.add_argument('--symbol',dest='simbol',action=QueryAction,help='The main symbol to get data for drawing chart')
    query.add_argument('--start',dest='start',action=QueryAction,help='The offset to start to get quotes')
    #Crea un gruppo per gli output
    output = parser.add_mutually_exclusive_group(required=True)
    output.add_argument('--txt',dest='output',action='store_const',const=lambda resp: to_txt(resp),help='Text output format')
    output.add_argument('--json',dest='output',action='store_const',const=lambda resp: to_json(resp),help='JSON output format')
    output.add_argument('--csv',dest='output',action='store_const',const=lambda resp: to_csv(resp),help='CSV outputformat') 
    output.add_argument('--xml',dest='output',action='store_const',const=lambda resp: to_xml(resp),help='CSV outputformat')  
    # Parse args
    args = parser.parse_args()
    # Url per una specifica richiesta alle api
    url = yahoo_api_request.format(args.Database,args.request)

    # Effettuo la richiesta
    resp = requests.request("GET", url, headers=args.auth, params=args.query)
    # Controlla che la richiesta sia andata a buon fine
    assert resp.status_code == requests.codes.ok, ConnectionError('Request error')
    # Funzione lambda inserita come parametro da restituire
    output = args.output(resp.json())
    # Stampa il risultato nel formato richiesto
    sys.stdout.write(output)
    # Flush
    sys.stdout.flush()



if __name__ == '__main__':

    main()

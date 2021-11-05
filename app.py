from telebot import TeleBot
from TradeMethod.TradeBot import TradeBot
from TelegramAPI.telegramAPI import setMyCommands

app = TeleBot(__name__)

try:
    with open("./tele-key", "r") as f:

        tele_key = f.readline()
        tele_key = tele_key.strip()
    
    app.config['api_key'] = tele_key
    if app.get_me()['ok'] == False:
        raise Exception
except:
    valid = False
    print('Cannot load your Telegram bot token.')
    while not valid:
        print('Please insert your Telegram bot token. Once it is validated, this will not be asked again.')
        print('Token:')
        tele_key = input()

        app.config['api_key'] = tele_key
        if app.get_me()['ok'] == False:
            print('Account validation failed.')
        else:
            print('Success')
            valid = True

    with open("./tele-key", "w") as f:
        f.write(f"{tele_key}")

commands = [
    {'command' : 'status', 'description' : 'get trade bot status'},
    {'command' : 'vol_start', 'description' : 'start trading'},
    {'command' : 'vol_stop', 'description' : 'stop trading'},
    {'command' : 'vol_reset', 'description' : 'sell all the coins that the trade bot bought, and restart'},
    {'command' : 'vol_extend', 'description' : 'extend reset time, a scheduled time that the trade bot will sell'},
    {'command' : 'vol_hold', 'description' : 'hold trading'},
    {'command' : 'vol_release', 'description' : 'remove the hold'},
    {'command' : 'vol_set_tickers', 'description' : 'set a list of coins by their ticker names that the trade bot will invest on'},
    {'command' : 'vol_set_ratio', 'description' : 'set a ratio that you want to invest out of your current balance'},
    {'command' : 'buy', 'description' : 'buy a coin at a market order'},
    {'command' : 'sell', 'description' : 'sell a coin at a market order'},
    {'command' : 'random_game', 'description' : 'buy random coins'},
    {'command' : 'alert_off', 'description' : 'set alert off'},
    {'command' : 'alert_on', 'description' : 'set alert on'},
    {'command' : 'rand_add_exception', 'description' : 'add a coin on exception list that the random game will by'},
    {'command' : 'rand_remove_exception', 'description' : 'remove a coin on exception list that the random game will by'}
]

setMyCommands(app.config['api_key'], commands)

trade = TradeBot(
    method = 'telegram',
    tele_info = {'bot_token': tele_key, 'owner_id': None}
)

owner = None

@app.route('/start')
def start_command(message):
    chat_dest = message['chat']['id']
    global owner

    if owner == None:
        chat_type = message['chat']['type']
        if chat_type == 'group':
            name = ' '.join((message['chat']['title'], 'members'))
        elif chat_type == 'private':
            name = message['chat']['first_name']
        
        owner = chat_dest
        trade.tele_info['owner_id'] = chat_dest

        trade.alert_reset()
        trade.alert.start()

        msg = f'Hello {name}, you are now owner of this trade bot.'
    elif owner == chat_dest:
        msg = 'You are already my master.'
    else:
        msg = ownership_mismatch(message, '/start')
    app.send_message(chat_dest, msg)

@app.route('/status')
def status_command(message):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        try:
            st0 = '--------- VBS STATUS ---------'
            st1 = 'Tickers list: ' + ', '.join(trade.volatility.tickers)
            st2 = 'Betting Ratio: ' + str(trade.volatility.betting)
            st3 = 'Active: ' + str(trade.volatility.working)
            if trade.volatility.working:
                st4 = 'Reset Time: ' + trade.volatility.reset_time.strftime("%Y/%m/%d %H:%M")
                st5 = 'Hold: ' + str(trade.volatility.hold_tr)
                msg = '\n'.join((st0, st1, st2, st3, st4, st5))
            else:
                msg = '\n'.join((st0, st1, st2, st3))

            st6 = '\n--------- Random Game STATUS ---------'
            st7 = 'Random Game Exception List: ' + ', '.join(trade.rand_exception)
            msg = '\n'.join((msg, st6, st7))
        except:
            msg = 'Try again.'
    else:
        msg = ownership_mismatch(message, '/status')
    app.send_message(chat_dest, msg)

@app.route('/vol_start')
def vol_start_command(message):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        if trade.volatility.working:
            msg = 'Trade bot is already running.'
        else:
            trade.volatility.start()
            msg = "Trade bot is starting..."
    else:
        msg = ownership_mismatch(message, '/vol_start')
    app.send_message(chat_dest, msg)

@app.route('/vol_stop')
def vol_stop_command(message):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        global trade
        if not trade.volatility.working:
            msg = 'Trade bot is not running.'
        else:
            trade.volatility.end()
            trade.vol_reset()
            msg = "Stopping the trade bot..."
    else:
        msg = ownership_mismatch(message, '/vol_stop')
    app.send_message(chat_dest, msg)

@app.route('/vol_reset')
def vol_reset_command(message):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        if not trade.volatility.working:
            msg = 'Trade bot is not running.'
        else:
            msg = 'Reset requested...'
            trade.volatility.reset()
    else:
        msg = ownership_mismatch(message, '/vol_reset')
    app.send_message(chat_dest, msg)

@app.route('/vol_extend')
def vol_extend_command(message):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        if not trade.volatility.working:
            msg = 'Trade bot is not running.'
            app.send_message(chat_dest, msg)
        else:
            trade.volatility.extend()
    else:
        msg = ownership_mismatch(message, '/vol_extend')
        app.send_message(chat_dest, msg)

@app.route('/vol_hold')
def vol_hold_command(message):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        if not trade.volatility.working:
            msg = 'Trade bot is not running.'
            app.send_message(chat_dest, msg)
        else:
            trade.volatility.hold()
    else:
        msg = ownership_mismatch(message, '/vol_hold')
        app.send_message(chat_dest, msg)

@app.route('/vol_release')
def vol_release_command(message):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        if not trade.volatility.working:
            msg = 'Trade bot is not running.'
            app.send_message(chat_dest, msg)
        else:
            trade.volatility.release()
    else:
        msg = ownership_mismatch(message, '/vol_release')
        app.send_message(chat_dest, msg)

@app.route('/buy ?(.*)')
def buy_command(message, cmd):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        ls = cmd.split()
        if len(ls) != 2:
            msg = 'Received improper arguments.'
            app.send_message(chat_dest, msg)
        else:
            ticker = ls[0]
            price = float(ls[1])
            trade.buy(ticker, price)

    else:
        msg = ownership_mismatch(message, '/buy')
        app.send_message(chat_dest, msg)

@app.route('/sell ?(.*)')
def sell_command(message, cmd):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        ls = cmd.split()
        if len(ls) != 2:
            msg = 'Received improper arguments.'
            app.send_message(chat_dest, msg)
        else:
            ticker = ls[0]
            try:
                price = float(ls[1])
            except:
                price = ls[1].lower()
            trade.sell(ticker, price)

    else:
        msg = ownership_mismatch(message, '/sell')
        app.send_message(chat_dest, msg)

@app.route('/vol_set_tickers ?(.*)')
def vol_set_tickers_command(message, cmd):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        trade.volatility.set_tickers(cmd)
    else:
        msg = ownership_mismatch(message, '/vol_set_tickers')
        app.send_message(chat_dest, msg)

@app.route('/vol_set_ratio ?(.*)')
def vol_set_ratio_command(message, cmd):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        trade.volatility.set_ratio(cmd)
    else:
        msg = ownership_mismatch(message, '/vol_set_ratio')
        app.send_message(chat_dest, msg)

@app.route('/help')
def help_command(message):
    chat_dest = message['chat']['id']
    if owner == chat_dest:

        msg = '\n'.join((
            '/status - get trade bot status',
            '/vol_start - start trading',
            '/vol_stop - stop trading',
            '/vol_reset - sell all the coins that the trade bot bought, and restart',
            '/vol_extend - extend reset time, a scheduled time that the trade bot will sell',
            '/vol_hold - hold trading',
            '/vol_release - remove the hold',
            '/vol_set_tickers [ticker name 1] [ticker name 2] ... - set a list of coins by their ticker names that the trade bot will invest on',
            '/vol_set_ratio [ratio] - set a ratio that you want to invest out of your current balance',
            '/buy [ticker name] [price] - buy a coin at a market order',
            '/sell [ticker name] [price] - sell a coin at a market order',
            '/random_game [number of coins] [price] - buy random coins',
            '/alert_off - set alert off',
            '/alert_on - set alert on',
            '/rand_add_exception - add a coin on exception list that the random game will by',
            '/rand_remove_exception - remove a coin on exception list that the random game will by'
        ))
            
    else:
        msg = ownership_mismatch(message, '/help')
    app.send_message(chat_dest, msg)

@app.route('/random_game ?(.*)')
def random_game_command(message, cmd):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        ls = cmd.split()
        if len(ls) != 2:
            msg = 'Received improper arguments.'
            app.send_message(chat_dest, msg)
        else:
            k = int(ls[0])
            amount = float(ls[1])
            trade.random_game(k, amount)

    else:
        msg = ownership_mismatch(message, '/random_game')
        app.send_message(chat_dest, msg)

@app.route('/alert_off')
def alert_off_command(message):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        global trade
        if not trade.alert.working:
            msg = 'Alert off already'
        else:
            trade.alert.end()
            trade.alert_reset()
            msg = "Alert off"
    else:
        msg = ownership_mismatch(message, '/alert_off')
    app.send_message(chat_dest, msg)

@app.route('/alert_on')
def alert_on_command(message):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        if trade.alert.working:
            msg = 'Alert on already'
        else:
            trade.alert.start()
            msg = "Alert on"
    else:
        msg = ownership_mismatch(message, '/alert_on')
    app.send_message(chat_dest, msg)

@app.route('/rand_add_exception ?(.*)')
def rand_add_exception_command(message, cmd):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        trade.add_exception(cmd)
    else:
        msg = ownership_mismatch(message, '/rand_add_exception')
        app.send_message(chat_dest, msg)

@app.route('/rand_remove_exception ?(.*)')
def rand_remove_exception_command(message, cmd):
    chat_dest = message['chat']['id']
    if owner == chat_dest:
        trade.remove_exception(cmd)
    else:
        msg = ownership_mismatch(message, '/rand_remove_exception')
        app.send_message(chat_dest, msg)

def ownership_mismatch(message, command):
    msg = 'This bot does not belong to you.'
    if owner != None:
        username = message['from']['username']
        msg2 = f'@{username} attempted to access this trade bot.\nAttempted command: {command}'
        if message['chat']['type'] == 'group':
            group_title = message['chat']['title']
            msg2 = '\n'.join((msg2, 'Group name: ', group_title))
        app.send_message(owner, msg2)
    return msg


if __name__ == '__main__':
    app.poll()





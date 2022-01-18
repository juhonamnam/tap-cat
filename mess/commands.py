def get_commands(help_msg = False):
    commands = [
        {'command' : 'status', 'description' : 'get trade bot status'},
        {'command' : 'vol_start', 'description' : 'start trading'},
        {'command' : 'vol_stop', 'description' : 'stop trading'},
        {'command' : 'vol_reset', 'description' : 'sell all the coins that the trade bot bought, and restart'},
        {'command' : 'vol_extend', 'description' : 'extend reset time, a scheduled time that the trade bot will sell'},
        {'command' : 'vol_hold', 'description' : 'hold trading'},
        {'command' : 'vol_release', 'description' : 'remove the hold'},
        {'command' : 'vol_set_tickers{}'.format(' [ticker name 1] [ticker name 2]' if help_msg else ''), 'description' : 'set a list of coins by their ticker names that the trade bot will invest on'},
        {'command' : 'vol_set_ratio{}'.format(' [ratio]' if help_msg else ''), 'description' : 'set a ratio that you want to invest out of your current balance'},
        {'command' : 'buy{}'.format(' [ticker name] [price]' if help_msg else ''), 'description' : 'buy a coin at the market order'},
        {'command' : 'sell{}'.format(' [ticker name] [price]' if help_msg else ''), 'description' : 'sell a coin at the market order'},
        {'command' : 'sell_all', 'description' : 'sell all the coins at the market order'},
        {'command' : 'random_game{}'.format(' [number of coins] [price]' if help_msg else ''), 'description' : 'buy random coins'},
        {'command' : 'alert_off', 'description' : 'set alert off'},
        {'command' : 'alert_on', 'description' : 'set alert on'},
        {'command' : 'rand_add_exception{}'.format(' [ticker name]' if help_msg else ''), 'description' : 'add a coin on exception list that the random game will by'},
        {'command' : 'rand_remove_exception{}'.format(' [ticker name]' if help_msg else ''), 'description' : 'remove a coin on exception list that the random game will by'}
    ]
    return commands

help_msg = '\n'.join([ f'/{x["command"]} - {x["description"]}' for x in get_commands(help_msg = True) ])
class RandomGameException:
    def __init__(self) -> None:
        self.set = set()

    def add(self, ticker):
        self.set.add(ticker)

    def remove(self, ticker):
        self.set.remove(ticker)

    def __str__(self) -> str:
        return ', '.join(self.set)

    def paginate(self, offset, limit):
        pg_list = list(self.set)[offset * limit: offset * limit + limit]
        return {
            'list': pg_list,
            'paginate': {
                'total': len(self.set),
                'offset': offset,
                'limit': limit
            }
        }


random_game_exception = RandomGameException()

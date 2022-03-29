from .scaffold import Scaffold


class Blueprint(Scaffold):
    def __init__(self):
        super().__init__()
        self._blueprints = list()

    def register_blueprint(self, blueprint):
        self._blueprints.append(blueprint)

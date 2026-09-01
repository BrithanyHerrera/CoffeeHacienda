class FakeCursor:
    def __init__(self, handler):
        self.handler = handler
        self.result = None
        self.rowcount = 0
        self.lastrowid = None
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql, params=None):
        normalized = ' '.join(sql.split())
        self.calls.append((normalized, params))
        self.rowcount = 0
        # La auditoría es una preocupación transversal; los dobles de prueba
        # la aceptan sin consumir respuestas configuradas para la operación.
        if normalized.startswith('INSERT INTO tauditoria'):
            self.result = None
            return 1
        self.result = self.handler(normalized, params, self)
        return 1

    def fetchone(self):
        if isinstance(self.result, list):
            return self.result[0] if self.result else None
        return self.result

    def fetchall(self):
        if self.result is None:
            return []
        return self.result if isinstance(self.result, list) else [self.result]


class FakeConnection:
    def __init__(self, handler):
        self.cursor_instance = FakeCursor(handler)
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self, *args, **kwargs):
        return self.cursor_instance

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


def connection_with_results(*results):
    queue = list(results)

    def handler(sql, params, cursor):
        if not queue:
            raise AssertionError(f'No hay respuesta configurada para: {sql}')
        return queue.pop(0)

    return FakeConnection(handler)

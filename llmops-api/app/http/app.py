from injector import Injector
from internal.server import Http
from internal.router import Router

injector = Injector()

app = Http(__name__, router=injector.get(Router))

if __name__ == "__main__":
    app.run(debug=True)

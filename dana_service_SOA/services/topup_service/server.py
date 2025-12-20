import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

from services.topup_service.topup import topup_dana

class TopupService(ServiceBase):
    @rpc(Unicode, Unicode, _returns=Unicode)
    def topup(ctx, account_number, amount):
        """Endpoint untuk topup saldo (auth di FastAPI)."""
        return topup_dana(account_number, amount)

application = Application(
    [TopupService],
    'dana.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(application)

if __name__ == '__main__':
    server = make_server('0.0.0.0', 8002, wsgi_app)
    print("Topup Service berjalan di http://localhost:8002")
    print("WSDL: http://localhost:8002?wsdl")
    server.serve_forever()
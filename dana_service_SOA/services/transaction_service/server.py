import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

from services.transaction_service.transaction import transfer_dana

class TransactionService(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def transfer(ctx, sender_account_number, receiver_account_number, amount):
        """Endpoint untuk transfer (auth di FastAPI)."""
        return transfer_dana(sender_account_number, receiver_account_number, amount)

application = Application(
    [TransactionService],
    'dana.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(application)

if __name__ == '__main__':
    server = make_server('0.0.0.0', 8003, wsgi_app)
    print("Transaction Service berjalan di http://localhost:8003")
    print("WSDL: http://localhost:8003?wsdl")
    server.serve_forever()
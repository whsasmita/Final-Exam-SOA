import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

from services.account_service.endpoints import AccountService as EndpointsAdapter
from services.account_service.account import get_account_info

# instantiate adapter
endpoints = EndpointsAdapter()

class AccountService(ServiceBase):
    @rpc(Unicode, Unicode, _returns=Unicode)
    def login_user(ctx, username, password):
        """Login (auth di FastAPI, ini hanya untuk verifikasi ke DB)."""
        return endpoints.login_user(username, password)

    @rpc(Unicode, Unicode, _returns=Unicode)
    def register_user(ctx, username, password):
        """Register (auth di FastAPI, ini hanya untuk verifikasi ke DB)."""
        return endpoints.register_user(username, password)

    @rpc(Unicode, _returns=Unicode)
    def get_account_info(ctx, account_number):
        """Get account info tanpa JWT validation."""
        return get_account_info(account_number)

application = Application(
    [AccountService],
    'dana.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(application)

if __name__ == '__main__':
    server = make_server('0.0.0.0', 8001, wsgi_app)
    print("Account Service berjalan di http://localhost:8001")
    print("WSDL: http://localhost:8001?wsdl")
    server.serve_forever()
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from husky.settings import settings
from husky.rpc import ProxyPool

def get_rpc_client():
    transport = TSocket.TSocket(settings.PROXY_POOL_SERVER_HOST, settings.PROXY_POOL_LISTEN_PORT)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = ProxyPool.Client(protocol)
    transport.open()
    return transport, client
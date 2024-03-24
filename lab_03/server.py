from spyne import Application, rpc, ServiceBase, Integer, Unicode
from spyne import Iterable, AnyDict
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from db import Postgres
import os
import logging

logging.basicConfig(level=logging.INFO)


class Lab03RPCServer(ServiceBase):
    @rpc(_returns=AnyDict)
    def list_products(self):
        logging.info("Listing products")
        all_records_query = "select * from product order by create_date desc"
        data = Postgres().get_table(query=all_records_query)
        return data

    @rpc(Integer, _returns=AnyDict)
    def view_product(self, product_id):
        logging.info(f"Viewing product {product_id}")
        one_product_query = """select * from product where id=%s"""
        product = Postgres().get_one(query=one_product_query, params=(product_id,))
        return product


rpc_server = Application(
    [Lab03RPCServer],
    tns='edu.dis.lab03',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', int(os.environ.get('RPC_SERVER_PORT', 6000)), WsgiApplication(rpc_server))
    logging.info(f"Listening to '0.0.0.0:{os.environ.get('RPC_SERVER_PORT', 6000)}")
    logging.info(f"WSDL is at: http://localhost:{os.environ.get('RPC_SERVER_PORT', 6000)}/?wsdl")
    server.serve_forever()

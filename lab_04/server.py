from jsonrpcserver import method as rpc, serve, Success, Result
from db import Postgres
import os
import logging

logging.basicConfig(level=logging.INFO)


@rpc
def list_products() -> Result:
    logging.info("Listing products")
    all_records_query = """
        select 
        id, product_type, sku, model, description, rrp, 
        to_char(create_date, 'DD Mon YYYY') as create_date
        from product 
        order by create_date desc"""
    data = Postgres().get_table(query=all_records_query)
    logging.info(f"Retrieved: {data}")
    return Success(data)


@rpc
def view_product(product_id: int) -> Result:
    logging.info(f"Viewing product {product_id}")
    one_product_query = """
        select 
            id, product_type, sku, model, description, rrp, 
            to_char(create_date, 'DD Mon YYYY') as create_date
        from product 
        where id=%s"""
    product = Postgres().get_one(query=one_product_query, params=(product_id,))
    logging.info(f"Retrieved: {product}")
    return Success(product)


if __name__ == '__main__':
    serve(name='0.0.0.0', port=int(os.environ.get('RPC_SERVER_PORT')))

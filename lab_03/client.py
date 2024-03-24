from flask import Flask, current_app, render_template, request, redirect, url_for
import time
import os
from suds.client import Client
import logging


class Config:
    RPC_SERVER_HOST = os.environ.get('RPC_SERVER_HOST', '127.0.0.1')
    RPC_SERVER_PORT = os.environ.get('RPC_SERVER_PORT', 6000)


lab3 = Flask(__name__)
lab3.config.from_object(Config)
logging.basicConfig(level=logging.INFO)


def get_rpc() -> Client:
    url = f"""http://{current_app.config['RPC_SERVER_HOST']}:{current_app.config['RPC_SERVER_PORT']}?wsdl"""
    client = Client(url)
    logging.info(f"Client: {client}")
    return client


@lab3.route("/", methods=['GET'])
def lab_three_list():
    result = get_rpc().service.list_products()
    logging.info(f"Result: {result}")
    return render_template(
        template_name_or_list='lab_three_list.html',
        # error=error,
        columns=list(result.headers),
        data=result.data,
    )


@lab3.route("/<int:product_id>", methods=['GET'])
def lab_three_view(product_id: int):
    result = get_rpc().service.view_product(product_id)
    logging.info(f"Result: {result}")
    return render_template(
        template_name_or_list='lab_three_view.html',
        data=result,
    )


if __name__ == '__main__':
    lab3.run()

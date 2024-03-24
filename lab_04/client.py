from flask import Flask, current_app, render_template
from jsonrpcclient import request as rpc_request, parse as rpc_response, Ok
import requests
from requests.models import Response
import os
import logging


class Config:
    RPC_SERVER_HOST = os.environ.get('RPC_SERVER_HOST', '127.0.0.1')
    RPC_SERVER_PORT = os.environ.get('RPC_SERVER_PORT', 6000)


lab4 = Flask(__name__)
lab4.config.from_object(Config)
logging.basicConfig(level=logging.INFO)


def rpc(method: str, payload: dict = None):
    url = f"""http://{current_app.config['RPC_SERVER_HOST']}:{current_app.config['RPC_SERVER_PORT']}"""
    try:
        response = rpc_response(requests.post(url=url, json=rpc_request(method, payload)).json())
        assert isinstance(response, Ok)
        return response.result
    except AssertionError as ae:
        logging.error(str(ae))
    except Exception as e:
        logging.error(str(e))


@lab4.route("/", methods=['GET'])
def lab_four_list():
    result = rpc('list_products')
    logging.info(f"Result: {result}")
    return render_template(
        template_name_or_list='lab_four_list.html',
        # error=error,
        columns=result.get('headers', []),
        data=result.get('data', []),
    )


@lab4.route("/<int:product_id>", methods=['GET'])
def lab_four_view(product_id: int):
    result = rpc('view_product', {'product_id': product_id})
    logging.info(f"Result: {result}")
    return render_template(
        template_name_or_list='lab_four_view.html',
        data=result,
    )


if __name__ == '__main__':
    lab4.run()

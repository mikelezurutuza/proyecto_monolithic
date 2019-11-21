from flask import request, jsonify, abort
from flask import current_app as app

from .event_publisher import publish
from .models import Order
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
import json
from . import Session
from .orchestrator import get_orchestrator
from .state import OrderState

@app.route('/order/create', methods=['POST'])
def create_order():
    print('ORDER POST, LLAMANDO A PAYMENT Y DELIVERY')
    session = Session()
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json

    response = None
    try:      
        new_order =  Order(
            number_of_pieces = content['num_pieces'],
            description= 'eldefaultdaerror'
        )
        session.add(new_order) 
        session.commit()

        info = {}
        info['userId'] = content['userId']
        info['num_pieces'] = new_order.number_of_pieces
        info['orderId'] = new_order.id
        info['zip'] = content['zip']

        print(info, flush=True)

        orchestrator = get_orchestrator()
        order_state = OrderState(info['orderId'], info['num_pieces'], info['userId'])
        orchestrator.order_list.append(order_state)

        publish('payment_event_exchange','payment_reserve_queue',info)
        publish('delivery_event_exchange', 'delivery_create_event_queue', info)

        response = json.dumps(info)
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)

    session.close()
    return response


# Error Handling #######################################################################################################
@app.errorhandler(UnsupportedMediaType)
def unsupported_media_type_handler(e):
    return get_jsonified_error(e)


@app.errorhandler(BadRequest)
def bad_request_handler(e):
    return get_jsonified_error(e)


@app.errorhandler(NotFound)
def resource_not_found_handler(e):
    return get_jsonified_error(e)


@app.errorhandler(InternalServerError)
def server_error_handler(e):
    return get_jsonified_error(e)


def get_jsonified_error(e):
    traceback.print_tb(e.__traceback__)
    return jsonify({"error_code":e.code, "error_message": e.description}), e.code



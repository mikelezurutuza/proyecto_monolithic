from flask import request, jsonify, abort
from flask import current_app as app

from .models import Payment
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
from sqlalchemy.orm.exc import NoResultFound


@app.route('/payment/deposit', methods=['POST'])
def perform_deposit():
    session = Session()
    new_payment = None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    
    try:
        new_payment = Payment(
            userId=content['userId'],
            money=content['money'],
            reserved_money=0,
        )             
        try:           
            user = session.query(Payment).filter(Payment.userId == new_payment.userId).one()
            user.money += new_payment.money 
            print('pago    '+str(user.money), flush=True)
        except NoResultFound:     
            session.add(new_payment)    

        session.commit()
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)

    response = jsonify(new_payment.as_dict())
    session.close()
    return response


# Database clean #######################################################################################################
@app.route('/payment/clean_payment', methods=['GET'])
def clean_payments_database():
    session = Session()
    session.query(Payment).delete()
    session.close()
    return " filas eliminadas de payment"

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



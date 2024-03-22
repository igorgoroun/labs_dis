from flask import Flask, current_app, render_template, request, redirect, url_for
from db import database_classes
import time
import logging

lab2 = Flask(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)


def make_connections() -> dict:
    return {k: v() for k, v in database_classes.items()}


@lab2.route("/", methods=['GET', 'POST'])
def lab_two_page():
    error = None
    form = None
    columns = []
    result_table = dict()
    mysql_data = None
    postgres_data = None
    ts = time.time()
    db = None
    # встановлюємо звʼязок з базами
    try:
        connections = make_connections()
    except Exception as e:
        error = f"Cannot make connection to all databases: {str(e)}"
        connections = None

    if request.method == 'POST' and connections and error is None:
        form = request.form
        try:
            assert request.form.get('query')
            current_app.logger.debug(f'Query: {request.form.get("query")}')
            current_app.logger.debug(f"Database: {request.form.get('database_class')}")
            db = connections.get(request.form.get('database_class'))
            # execute user query
            db.cursor.execute(request.form.get('query'))
            db.connection.commit()
        except AssertionError:
            error = "Query is empty"
        except Exception as e:
            error = f"Something went wrong: {str(e)}"

    # загальний запит на всі дані
    all_records_query = "select * from product order by create_date desc"
    # завантажуємо дані з баз
    for mn, cl in database_classes.items():
        data = cl().load(all_records_query)
        result_table.update({mn: data})

    current_app.logger.debug(f"Result table: {result_table}")

    execution_time = (time.time() - ts) * 1000

    return render_template(
        template_name_or_list='lab_two_page.html',
        database_classes=database_classes,
        error=error,
        form=form,
        columns=columns,
        result_table=result_table,
        execution_time=execution_time,
        colspan=int(12/len(database_classes)),
    )


@lab2.route("/move/<string:source_db>/<int:source_id>", methods=['GET'])
def move_record(source_db: str, source_id: int):
    current_app.logger.debug(f"Source db: {source_db}, id: {source_id}")
    # підключаємо бази
    src_db = database_classes[source_db]()
    dest_db = database_classes[list(database_classes.keys()-[source_db])[0]]()
    current_app.logger.debug(f"Source db: {src_db}, Dest: {dest_db}")

    # готуємо запроси
    src_query = """select sku, model, description, rrp, product_type from product where id=%s"""
    delete_query = """delete from product where id=%s"""
    dest_query = """insert into product (sku, model, description, rrp, product_type) values (%s, %s, %s, %s, %s)"""

    try:
        with src_db.connection.cursor() as src_cursor:
            src_cursor.execute(src_query, (source_id,))
            src_data = src_cursor.fetchone()
            current_app.logger.debug(f"Source data: {tuple(src_data.values())}")
            src_cursor.execute(delete_query, (source_id,))
            with dest_db.connection.cursor() as dest_cursor:
                dest_cursor.execute(dest_query, tuple(src_data.values()))
                # комміт для створеного запис
                dest_db.connection.commit()
            # комміт транзакції для видаленого запису
            src_db.connection.commit()
    except Exception as e:
        src_db.connection.rollback()
        dest_db.connection.rollback()

    # назад на головну
    return redirect(url_for('lab_two_page'))


if __name__ == '__main__':
    lab2.run()

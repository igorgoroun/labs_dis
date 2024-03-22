from flask import Flask, current_app, render_template, request
from db import connection_classes
import time
import logging

lab = Flask(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)


@lab.route("/", methods=['GET', 'POST'])
def query_page():
    error = None
    form = None
    columns = []
    result_table = []
    ts = time.time()
    db = None

    if request.method == 'POST' and error is None:
        try:
            assert request.form.get('query')
            current_app.logger.debug(f'Query: {request.form.get("query")}')
            db_class = connection_classes.get(request.form.get('connection_class'))
            current_app.logger.debug(f"Connection: {db_class}")
            db = db_class()
            # execute user query
            db.cursor.execute(request.form.get('query'))
            db.connection.commit()
        except AssertionError as ae:
            error = 'Query is empty'
        except Exception as e:
            error = f"Something went wrong: {str(e)}"
        form = request.form

    if db is None:
        try:
            db = connection_classes.get('Psycopg')()
        except Exception as e:
            error = f"Cannot connect: {str(e)}"

    if error is None:
        columns_query = "SELECT column_name FROM information_schema.columns where table_name = 'product' order by ordinal_position;"
        db.cursor.execute(columns_query)
        columns = [c[0] for c in db.cursor.fetchall()]
        current_app.logger.debug(columns)
        # select everything from table
        db.cursor.execute("select * from product order by id desc")
        result_table = db.cursor.fetchall()
        current_app.logger.debug(f"result_table: {result_table}")

    execution_time = (time.time() - ts) * 1000

    return render_template(
        template_name_or_list='query_page.html',
        connection_classes=connection_classes,
        error=error,
        form=form,
        columns=columns,
        result_table=result_table,
        execution_time=execution_time
    )


if __name__ == '__main__':
    lab.run()

#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *
import pyodbc

logger = get_logger(__name__)


def get_all_pyodbc_drivers():
    return pyodbc.drivers()


def msql_get_list_of_dicts_for_cursor(cursor, want_decode=True):
    """
    из курсора получаем список словарей
    """
    columns = [column[0] for column in cursor.description]
    rows = [
        dict(line) for line in [zip(columns, row) for row in cursor.fetchall()]
    ]
    if want_decode and rows:
        rows = [deep_encode(_) for _ in rows]

    return rows


@my_timer
def mssql_create_connection(
    server="185.44.78.72",
    db_name="db",
    login="",
    password="",
    trusted_connection="yes",
    # trusted_connection = 'no',
    # connection_mode = 'cnxn_str',
    connection_mode="variables",
    json_with_vars="",
    # driver = '{SQL Server Native Client 11.0}', # working main
    driver="{ODBC Driver 17 for SQL Server}",  # working
):
    """

    возможные драйвера
        driver = '{MICROSOFT ACCESS DRIVER (*.mdb, *.accdb)}'
        driver = '{SQL Server}'
        driver = '{ODBC Driver 17 for SQL Server}' # working
        driver = '{SQL Server Native Client 11.0}', # working
    
    """
    fun = "mssql_create_connection"

    t_start = time.time()

    logger.debug2("[%s connection_mode=%s" % (fun, connection_mode))

    # я могу передавать переменные через json-строку
    real_variables = {}
    if json_with_vars:
        connection_mode = "variables"
        # real_variables = obj_from_json(json_with_vars)
        real_variables = eval(json_with_vars)
        # logger.debug('have json_with_vars=%s, so use real_variables=%s' % (json_with_vars, real_variables))
        for key, value in real_variables.items():
            if key == "server":
                server = value
            elif key == "db_name":
                db_name = value
            elif key == "login":
                login = value
            elif key == "password":
                password = value
            elif key == "trusted_connection":
                trusted_connection = value
            elif key == "connection_mode":
                connection_mode = value
            elif key == "driver":
                driver = value
            else:
                logger.critical("unknown variable %s" % key)
                os._exit(0)
        logger.debug("login=%s" % login)

    t = 1
    if t:
        print("all drivers:")
        show_list(get_all_pyodbc_drivers())

    repl = {
        "[driver]": driver,
        "[server]": server,
        "[db_name]": db_name,
        "[login]": login,
        "[password]": password,
    }

    if connection_mode == "cnxn_str":
        """
            cnxn = po.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
            server+';DATABASE='+database+';UID='+username+';PWD=' + password)
        """
        cnxn_str = (
            "[driver];"
            "Server=UKXXX00123,45600;"
            "Database=DB01;"
            "Trusted_Connection=yes;"
        )
        cnxn_str = '''Driver=[driver];Data Source=[server];Initial Catalog=[db_name];Persist Security Info=True;User ID=[login];Password="[password]"'''
        cnxn_str = no_probely(cnxn_str, repl)
        logger.debug("cnxn_str=%s" % cnxn_str)
        connection = pyodbc.connect(cnxn_str)

    elif connection_mode == "variables":

        kwargs = {
            "driver": driver,
            "host": server,
            "database": db_name,
            "trusted_connection": trusted_connection,
            # 'ansi':True,
        }
        if login:
            kwargs["user"] = login
        if password:
            kwargs["password"] = password
        logger.debug("kwargs=%s" % kwargs)

        # connection = pyodbc.connect(**kwargs)
        connection = try_execute_mssql_function(
            {"func": pyodbc.connect, "kwargs": kwargs}
        )
        # while True:
        #     try:
        #     connection = pyodbc.connect(**kwargs)
        #     break
    else:
        logger.critical("unknown connection_mode=%s" % connection_mode)

    duration = time.time() - t_start
    logger.debug1(
        "     +connection=%s in %.3f seconds]" % (connection, duration)
    )
    return connection
    return connection


def create_json_with_vars(vars):
    json_with_vars = json.dumps(vars)
    return json_with_vars


def try_execute_mssql_function(*args, **kwargs):
    _ = {
        "max_duration": 60 * 3,
        "message": "mssql not working",
    }
    kwargs.update(_)
    return try_execute_function(*args, **kwargs)


if __name__ == "__main__":
    t = 1
    if t:
        print("all drivers:")
        show_list(get_all_pyodbc_drivers())

    table = "BET"

    server = "185.44.78.72"
    db_name = "StartBetBot"
    login = "sa"
    password = "Omdf785- "
    trusted_connection = "yes"
    trusted_connection = "no"

    # Data Source=185.44.78.72;Initial Catalog=BF_ODDS;Persist Security Info=True;User ID=sa;Password='Omdf785- '
    t = 1
    if t:
        # база лайв-коней
        server = "185.44.78.72"
        db_name = "BF_ODDS"
        login = "sa"
        password = "Omdf785- "
        trusted_connection = "yes"
        trusted_connection = "no"
        table = "VALUE"

    _kwargs = {
        "server": server,
        "db_name": db_name,
        "login": login,
        "password": password,
        "trusted_connection": trusted_connection,
    }

    # default raw connection
    t = 0
    if t:
        _ = {
            "driver": "{ODBC Driver 17 for SQL Server}",  # working
            "user": "wrong user",
        }
        _kwargs.update(_)
        logger.debug("_kwargs=%s" % _kwargs)
        connection = pyodbc.connect(**_kwargs)
        logger.debug("connection=%s" % connection)
        os._exit(0)

    special = "explore_json_with_vars"
    special = ""

    if special == "explore_json_with_vars":
        json_with_vars = create_json_with_vars(_kwargs)
        json_with_vars = '{"password": "Omdf785- ", "login": "sa", "db_name": "BF_ODDS", "trusted_connection": "no", "server": "185.44.78.72"}'
        # json_with_vars = '{"password": "Omdf785- ", "login": "sa", "db_name": "BF_ODDS", "trusted_connection": "yes", "server": ".\SQLEXPRESS"}'
        logger.debug("json_with_vars = `%s`" % json_with_vars)

        t = 0
        if t:
            new_kwargs = obj_from_json(json_with_vars)
            logger.debug("new_kwargs = %s" % new_kwargs)

        _kwargs = {
            "json_with_vars": json_with_vars,
        }
        # os._exit(0)

    connection = mssql_create_connection(**_kwargs)
    logger.debug("connection=%s, start work with data" % connection)
    cursor = connection.cursor()
    wait_for_ok()

    t = 1
    if t:
        logger.info("Sample select query")
        cursor.execute("SELECT @@version;")
        row = cursor.fetchone()
        while row:
            logger.debug(row[0])
            row = cursor.fetchone()

    t = 0
    if t:
        sql = "exec pr_get_all_selections"
        sql = "exec [dbo].[pr_get_all_selections]"  # получить все селекшены
        sql = "exec [dbo].[pr_get_accounts]"  # получить аки - для дебага базы
        logger.info("execute procedure to get all bets")

        step = 0
        while True:
            step += 1
            t_start = time.time()
            cursor.execute(sql)
            rows = msql_get_list_of_dicts_for_cursor(cursor)
            # rows = cursor.fetchval()
            duration = time.time() - t_start
            logger.debug(
                "step %s, executed in %.3f seconds, got rows=%s"
                % (step, duration, rows)
            )

            if rows:
                m = (
                    "check betbugrer value - found %s items in %.3f seconds"
                    % (len(rows), duration)
                )
                logger.critical(m)
                inform_me_one(m)

                t = 1
                t = 0
                if t:
                    f = os.path.abspath("temp/rows.obj")
                    logger.debug("saving to %s" % f)
                    obj_to_file(rows, f)

                # inform_critical(m)
                # wait_for_ok()

            sleep_(1)

        os._exit(0)

    columns = [row.column_name for row in cursor.columns(table=table)]
    logger.debug("columns of %s = %s" % (table, columns))

    q = "SELECT TOP(2) * FROM %s" % table
    q = "SELECT * FROM %s" % table
    logger.debug("q=%s" % q)
    res = cursor.execute(q)
    logger.debug("res=%s" % res)
    # row = cursor.fetchone()
    # print(row)

    num_row = 0
    for row in cursor:
        num_row += 1
        logger.debug("num_row=%s row=%s" % (num_row, row))
        _ = {}
        for num in range(len(columns)):
            key = columns[num]
            value = row[num]
            _[key] = value
        show_dict(_)

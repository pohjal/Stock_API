import psycopg2
import os
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import json
import io


"""
Tiatokantahallintaa varten, kaikki SQL täällä.
"""
dbConfig = {}


def init():
    """
    Kaiken alku

    Alustaa salaukset ja sovelluksen tarvittavat tiedot
    """
    try:
        global dbConfig

        dbConfigFile = io.open('config/dbconfig.json', encoding="UTF-8")

        dbConfig = json.load(dbConfigFile)

        env_db_user = os.environ.get("DB_USER")
        env_db_pass = os.environ.get("DB_PASS")
        # db_name = os.environ["DB_NAME"]
        # db_port = os.environ["DB_PORT"]

        if not env_db_user is None:
            dbConfig['postgreSqlConfigs']['user'] = env_db_user
            print(f'Using db user name from env {env_db_user}')
        else:
            print(
                f'Using config file user name {dbConfig["postgreSqlConfigs"]["user"]}')
        if not env_db_pass is None:
            dbConfig['postgreSqlConfigs']['password'] = env_db_pass
            print(
                f'Using db password from environment with length {len(env_db_pass)}')
        else:
            print(f'Using config file db password')

        return True
    except Exception as error:
        print(f'Error while reading config files {error}')
        return False


def openDbCon():
    """
    Opens db connection
    """
    try:
        if dbConfig == {}:
            if not init():
                return {
                    'success': False
                }

        pool = SimpleConnectionPool(
            minconn=dbConfig['poolConfig']['poolSizeMin'],
            maxconn=dbConfig['poolConfig']['poolSizeMax'],
            **dbConfig['postgreSqlConfigs']
        )

        return {
            'connectionPool': pool,
            'success': True
        }
    except Exception as err:
        print(f'Something went wrong {err}')
        return {'success': False}


connection = openDbCon()
if connection['success']:
    pool = connection['connectionPool']


def querySql(sqlQuery):
    """
    Runs sql query
    """

    global pool
    try:
        con = pool.getconn()  # TODO better error handling
        cur = con.cursor(cursor_factory=RealDictCursor)
        cur.execute(sqlQuery)
        return cur.fetchall()
    except Exception as error:
        print(f"Ei saada yhteyttä tietokantaan koska {error}")
        return []
    finally:  # tämä suoritetaan aina lopuksi
        cur.close()
        con.close()
        pool.putconn(con)


def querySqlParams(sqlQuery, params, modify=False, insert=False):
    """
    Queries with params, also used for updates and inserts
    """

    global pool
    try:
        con = pool.getconn()
        cur = con.cursor(cursor_factory=RealDictCursor)
        cur.execute(sqlQuery, params)
        if not modify:
            return cur.fetchall()
        else:

            if insert:
                # haetaan viimeisimmän indeksi, ei näin tarvitse transaktiota
                lastIndex = cur.lastrowid
                con.commit()
                return lastIndex
            else:
                affectedCount = 0
                affectedCount = cur.rowcount
                con.commit()
                return affectedCount
    except Exception as error:
        print("Jokin meni pieleen: " + str(error))
        return None
    finally:
        cur.close()
        con.close()
        pool.putconn(con)


def getAllOffers():
    """
    Returns all offers from the database
    """

    sql = """
    SELECT *
    FROM order_table
    WHERE type = 'Offer'
    ORDER BY order_table.createdat DESC
    """

    return querySql(sql)


def getAllBids():
    """
    Returns all bids from the database
    """

    sql = """
    SELECT *
    FROM order_table
    WHERE type = 'Bid'
    ORDER BY order_table.createdat DESC
    """

    return querySql(sql)


def getAllTrades():
    try:
        sql = "SELECT * FROM trades"
        return querySql(sql)
    except Exception as error:
        print(f"Error retrieving trades: {error}")
        return None


def getSampleWithVariables(variable):
    """
    Palauttaa käyttäjän valintahistoriaa katsomisjärjestyksessä
    """

    sql = """
    SELECT *
    FROM testTable 
    WHERE "testColumn" = %s
    """

    # if one variable it needs to end with ","
    return querySqlParams(sql, (variable,))


def insert_order(data):
    
    price = data['price']
    quantity = data['quantity']
    order_type = data['type']
    
    sql = "INSERT INTO order_table (price, quantity, type) VALUES (%s, %s, %s)"
    return querySqlParams(sql, (price, quantity, order_type), modify=True, insert=True)


def get_last_order():
    try:
        sql = "SELECT * FROM order_table ORDER BY createdat DESC LIMIT 1"
        return querySql(sql)
    except Exception as error:
        print(f"Error retrieving the last order: {error}")
        return None


def insert_trade(traded_time, traded_price, traded_quantity):
    sql = "INSERT INTO trades (traded_time, traded_price, traded_quantity) VALUES (%s, %s, %s)"
    return querySqlParams(sql, (traded_time, traded_price, traded_quantity), modify=True, insert=True)


def delete_order(data):
    try:
        id = data['id']
        sql = "DELETE FROM order_table WHERE id = %s"
        result = querySqlParams(sql, (id,), modify=True)
        if result:
            return {"message": "Order deleted successfully"}, 200
        else:
            return {"error": "Order not found or could not be deleted"}, 404
    except KeyError:
        return {"error": "ID not provided in request data"}, 400

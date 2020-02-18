#!/usr/bin/env python3
import sys
import logging
import time, datetime
import cryptography
import configparser
import atexit
import signal

import redis
import mysql.connector

from lib.exceptions import *
from lib.libmysql import *

##Global Vars
tries = 0

##Config Parser
CONFIG = {'redis' : {}, 'mysql' : {}}
config = configparser.ConfigParser()
config.read('tdaemon.conf')

CONFIG['redis']['password'] = config['redis']['password']
CONFIG['redis']['timeout'] = int(config['redis']['timeout'])
CONFIG['redis']['host'] = config['redis']['host']
CONFIG['redis']['port'] = int(config['redis']['port'])
CONFIG['redis']['db'] = int(config['redis']['db'])

CONFIG['mysql']['host'] = config['mysql']['host']
CONFIG['mysql']['user'] = config['mysql']['user']
CONFIG['mysql']['password'] = config['mysql']['password']
CONFIG['mysql']['db'] = config['mysql']['db']


##Logger
logging.basicConfig(filename='transactiond.log', level=logging.INFO, format='%(processName)s(%(process)d):%(asctime)s:[%(levelname)s]: %(message)s')
logging.info("Service Started.")
#Remembre to shutdown the logger at any exit occurance with logging.shutdown()

##Redis
logging.info("Attempting To Connect To The Redis Server: " + config['redis']['host'] + ":" + config['redis']['port'] + ". DB: " + config['redis']['db'])
server = redis.Redis(host=CONFIG['redis']['host'], port=CONFIG['redis']['port'], db=CONFIG['redis']['db'], password=CONFIG['redis']['password'])

##SQL
logging.info("Attempting To Connect To The MYSQL Server: " + CONFIG['mysql']['host'] + " as " + CONFIG['mysql']['user'] + ". DB: " + CONFIG['mysql']['db'])
database = mysql.connector.connect(
  host = CONFIG['mysql']['host'],
  user = CONFIG['mysql']['user'],
  passwd = CONFIG['mysql']['password'],
  database = CONFIG['mysql']['db']
)

mysql_handler = Database(database)

##Functions##
def make(From, To, Amount):
    return mysql_handler.transfer(From, To, Amount)
    
def shutdown():
    logging.info('Service Stopped.')
    logging.shutdown()

##Initialize:
atexit.register(shutdown)
signal.signal(signal.SIGTERM, shutdown)

##Service Loop##
#Transaction format : "#from-#to:amount"
while True:
    try:
        time.sleep(4)
        if server.ping():
            _, transaction = server.blpop('transactions')
            transaction = transaction.decode()
            transaction = transaction.split(':')
            Amount = transaction[1]
            From = transaction[0].split('-')[0]
            To = transaction[0].split('-')[1]
            print(From, To, Amount)
            result = make(From[1:], To[1:], int(Amount))
            if not result:
                logging.info('Transfer Failed.(Insufficient Balance Or Wrong Card)')
            else:
                logging.info('Transfer Succeeded.')
        else:
            raise RedisHungError("Redis Server(redis.service) is Not Responding To A Ping Request.")

    except RedisHungError:
            logging.warning("Redis Server Is Hung. Retrying...", exc_info=True)
            pass

    except redis.exceptions.AuthenticationError:
            logging.error("Redis Authentication Failed. Trying With No Password...")
            server = redis.Redis(host='localhost', port=6379, db=0)
            pass

    except redis.exceptions.ConnectionError:
            if tries <= CONFIG['redis']['timeout']:
                logging.error("Redis Server Is Down. Retrying...", exc_info=True)
                tries += 1
                pass
            else:
                logging.error("Redis Server Timeout. Exiting.")
                logging.shutdown()
                sys.exit()
    except redis.exceptions.ResponseError:
        logging.warning("Transaction List Structure(Type) Wrong. Rebuilding...")
        server.delete('transactions')
        server.rpush('transactions', 'mint')        
        pass
    except IndexError:
        logging.info("Invalid Transaction. Discarded.")
        pass 


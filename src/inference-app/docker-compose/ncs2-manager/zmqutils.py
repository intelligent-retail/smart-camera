#!/usr/bin/env python3
import zmq
import numpy as np
import logging as log
import socket


def pub(zmq_address: str = "tcp://*:5960"):
    """ZMQ Publisher
        Args:
            zmq_address:str ["tcp://*:5960"]

        Returns:
            pub: ZMQ Publisher
            ctx: ZMQ Context
    """
    ctx = zmq.Context()

    # Publisher
    pub = ctx.socket(zmq.PUB)
    pub.setsockopt(zmq.CONFLATE, 1)
    pub.bind(zmq_address)

    log.info("Server is starting up at {}...".format(zmq_address))

    return pub, ctx


def sub(zmq_address: str = "tcp://localhost:5960"):
    """ZMQ Subscriber
        Args:
            zmq_address:str ["tcp://localhost:5960"]

        Returns:
            sub: ZMQ Subscriber
            ctx: ZMQ Context
    """

    ctx = zmq.Context()

    log.info("Connecting to server {}...".format(zmq_address))

    sub = ctx.socket(zmq.SUB)
    sub.setsockopt(zmq.CONFLATE, 1)
    sub.setsockopt_string(zmq.SUBSCRIBE, np.unicode(""))
    sub.connect(zmq_address)

    log.info("Connected.")

    return sub, ctx


def req(zmq_address: str = "tcp://localhost:5962"):
    """ZMQ Request
        Args:
            zmq_address:str ["tcp://localhost:5962"]

        Returns:
            req: ZMQ REQ
            ctx: ZMQ Context
    """
    try:
        host = zmq_address.split(":")[0] + ":" + zmq_address.split(":")[1]
        host = host.split("//")[1]
        port = zmq_address.split(":")[2]

        if isOpen(host, port):
            ctx = zmq.Context()

            log.info("Connecting to server {}...".format(zmq_address))

            req = ctx.socket(zmq.REQ)
            req.connect(zmq_address)

            log.info("Connected.")

            return req, ctx
        else:
            return None, None
    except BaseException:
        return None, None


def isOpen(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, int(port)))
        s.shutdown(2)
        log.info("This host {} and port {} is okay".format(host, port))
        return True
    except BaseException:
        log.info("This host {} and port {} is not exist!!!".format(host, port))
        return False

#!/usr/bin/env python3
import zmq
import numpy as np
import logging as log


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


def rep(zmq_address: str = "tcp://localhost:5962"):
    """ZMQ Request
        Args:
            zmq_address:str ["tcp://localhost:5962"]

        Returns:
            req: ZMQ REP
            ctx: ZMQ Context
    """

    ctx = zmq.Context()

    log.info("Connecting to server {}...".format(zmq_address))

    rep = ctx.socket(zmq.REP)
    rep.bind(zmq_address)

    log.info("Connected.")

    return rep, ctx

#!/usr/bin/env python

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
from iothub_client import (
    IoTHubClient,
    IoTHubClientError,
    IoTHubTransportProvider,
    IoTHubClientResult,
)
from iothub_client import (
    IoTHubMessage,
    IoTHubMessageDispositionResult,
    IoTHubError,
    DeviceMethodReturnValue,
)
from iothub_client import IoTHubClientRetryPolicy
from iothub_client_args import get_iothub_opt, OptionError

# HTTP options
# Because it can poll "after 9 seconds" polls will happen effectively
# at ~10 seconds.
# Note that for scalabilty, the default value of minimumPollingTime
# is 25 minutes. For more information, see:
# https://azure.microsoft.com/documentation/articles/iot-hub-devguide/#messaging
TIMEOUT = 241000
MINIMUM_POLLING_TIME = 9

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

RECEIVE_CONTEXT = 0
MESSAGE_COUNT = 5
RECEIVED_COUNT = 0
CONNECTION_STATUS_CONTEXT = 0
TWIN_CONTEXT = 0
SEND_REPORTED_STATE_CONTEXT = 0
METHOD_CONTEXT = 0

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0
BLOB_CALLBACKS = 0
CONNECTION_STATUS_CALLBACKS = 0
TWIN_CALLBACKS = 0
SEND_REPORTED_STATE_CALLBACKS = 0
METHOD_CALLBACKS = 0

# chose HTTP, AMQP, AMQP_WS or MQTT as transport protocol
PROTOCOL = IoTHubTransportProvider.MQTT

# String containing Hostname, Device Id & Device Key in the format:
# "HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>"
CONNECTION_STRING = os.getenv("AZ_CONNECTION_STRING", None)

# some embedded platforms need certificate information


# global CONNECTION_STRING, PROTOCOL
try:
    (CONNECTION_STRING, PROTOCOL) = get_iothub_opt(
        sys.argv[1:], CONNECTION_STRING, PROTOCOL
    )
except OptionError as option_error:
    print(option_error)
    sys.exit(1)


def set_certificates(client):
    from iothub_client_cert import CERTIFICATES

    try:
        client.set_option("TrustedCerts", CERTIFICATES)
        print("set_option TrustedCerts successful")
    except IoTHubClientError as iothub_client_error:
        print("set_option TrustedCerts failed (%s)" % iothub_client_error)


def receive_message_callback(message, counter):
    global RECEIVE_CALLBACKS
    # message_buffer = message.get_bytearray()
    # size = len(message_buffer)
    # print ("Received Message [%d]:" % counter )
    # map_properties = message.properties()
    # key_value_pair = map_properties.get_internals()
    # print ("    Properties: %s" % key_value_pair )
    counter += 1
    RECEIVE_CALLBACKS += 1
    print("    Total calls received: %d" % RECEIVE_CALLBACKS)
    return IoTHubMessageDispositionResult.ACCEPTED


def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    # map_properties = message.properties()
    # print ("    message_id: %s" % message.message_id )
    # print ("    correlation_id: %s" % message.correlation_id )
    # key_value_pair = map_properties.get_internals()
    # print ("    Properties: %s" % key_value_pair )
    SEND_CALLBACKS += 1
    print("    Total calls confirmed: %d" % SEND_CALLBACKS)


def connection_status_callback(result, reason, user_context):
    global CONNECTION_STATUS_CALLBACKS
    print("Connection status changed[%d] with:" % (user_context))
    print("    reason: %d" % reason)
    print("    result: %s" % result)
    CONNECTION_STATUS_CALLBACKS += 1
    print("    Total calls confirmed: %d" % CONNECTION_STATUS_CALLBACKS)


def device_twin_callback(update_state, payload, user_context):
    global TWIN_CALLBACKS
    print("")
    print("Twin callback called with:")
    print("updateStatus: %s" % update_state)
    print("context: %s" % user_context)
    print("payload: %s" % payload)
    TWIN_CALLBACKS += 1
    print("Total calls confirmed: %d\n" % TWIN_CALLBACKS)


def send_reported_state_callback(status_code, user_context):
    global SEND_REPORTED_STATE_CALLBACKS
    SEND_REPORTED_STATE_CALLBACKS += 1
    print("    Total calls confirmed: %d" % SEND_REPORTED_STATE_CALLBACKS)


def device_method_callback(method_name, payload, user_context):
    global METHOD_CALLBACKS
    METHOD_CALLBACKS += 1
    device_method_return_value = DeviceMethodReturnValue()
    device_method_return_value.response = (
        '{ "Response": "This is the response from the device" }'
    )
    device_method_return_value.status = 200
    return device_method_return_value


def iothub_client_init():
    # prepare iothub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    if client.protocol == IoTHubTransportProvider.HTTP:
        client.set_option("timeout", TIMEOUT)
        client.set_option("MinimumPollingTime", MINIMUM_POLLING_TIME)
    # set the time until a message times out
    client.set_option("messageTimeout", MESSAGE_TIMEOUT)
    # some embedded platforms need certificate information
    set_certificates(client)
    # to enable MQTT logging set to 1
    if client.protocol == IoTHubTransportProvider.MQTT:
        client.set_option("logtrace", 0)
    client.set_message_callback(receive_message_callback, RECEIVE_CONTEXT)
    if (
        client.protocol == IoTHubTransportProvider.MQTT
        or client.protocol == IoTHubTransportProvider.MQTT_WS
    ):
        client.set_device_twin_callback(device_twin_callback, TWIN_CONTEXT)
        client.set_device_method_callback(
            device_method_callback, METHOD_CONTEXT
        )
    if (
        client.protocol == IoTHubTransportProvider.AMQP
        or client.protocol == IoTHubTransportProvider.AMQP_WS
    ):
        client.set_connection_status_callback(
            connection_status_callback, CONNECTION_STATUS_CONTEXT
        )

    retryPolicy = IoTHubClientRetryPolicy.RETRY_INTERVAL
    retryInterval = 100
    client.set_retry_policy(retryPolicy, retryInterval)
    print("SetRetryPolicy to: retryPolicy = %d" % retryPolicy)
    print("SetRetryPolicy to: retryTimeoutLimitInSeconds = %d" % retryInterval)
    retryPolicyReturn = client.get_retry_policy()
    print(
        "GetRetryPolicy returned: retryPolicy = %d"
        % retryPolicyReturn.retryPolicy
    )
    print(
        "GetRetryPolicy returned: retryTimeoutLimitInSeconds \
        = %d"
        % retryPolicyReturn.retryTimeoutLimitInSeconds
    )

    return client


def print_last_message_time(client):
    try:
        last_message = client.get_last_message_receive_time()
        print("Last Message: %s" % time.asctime(time.localtime(last_message)))
        print("Actual time : %s" % time.asctime())
    except IoTHubClientError as iothub_client_error:
        if (
            iothub_client_error.args[0].result
            == IoTHubClientResult.INDEFINITE_TIME
        ):
            print("No message received")
        else:
            print(iothub_client_error)


def iothub_client_detection_run(json_object):

    try:

        client = iothub_client_init()

        if client.protocol == IoTHubTransportProvider.MQTT:
            print("IoTHubClient is reporting state")
            reported_state = '{"newState":"standBy"}'
            client.send_reported_state(
                reported_state,
                len(reported_state),
                send_reported_state_callback,
                SEND_REPORTED_STATE_CONTEXT,
            )

        message = IoTHubMessage(json_object)
        # optional: assign ids
        message.message_id = "message_%d" % 1
        message.correlation_id = "correlation_%d" % 1

        client.send_event_async(message, send_confirmation_callback, 1)
        print(
            "IoTHubClient.send_event_async accepted message [%d] \
            for transmission to IoT Hub."
            % 1
        )

        # Wait for Commands or exit
        # print ("IoTHubClient waiting for commands, press Ctrl-C to exit")

    except IoTHubError as iothub_error:
        print("Unexpected error %s from IoTHub" % iothub_error)
        return
    except KeyboardInterrupt:
        print("IoTHubClient sample stopped")

    print_last_message_time(client)

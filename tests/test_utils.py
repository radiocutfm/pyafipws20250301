#!/usr/bin/python
# -*- coding: utf8 -*-

import pytest

from pyafipws.utils import inicializar_y_capturar_excepciones


pytestmark = [pytest.mark.dontusefix]


class DummyClient(object):
    def __init__(self, xml_request, xml_response):
        self.xml_request = xml_request
        self.xml_response = xml_response


class DummyWS(object):
    def __init__(self, xml_response, error_message="simulated parse error"):
        self.client = DummyClient("<request/>", xml_response)
        self.error_message = error_message
        self.params_in = {}
        self.params_out = {}
        self.reintentos = 0
        self.LanzarExcepciones = False
        self.XmlRequest = ""
        self.XmlResponse = ""
        self.ErrMsg = ""
        self.Traceback = ""
        self.Excepcion = ""

    def inicializar(self):
        pass

    @inicializar_y_capturar_excepciones
    def fail(self):
        raise RuntimeError(self.error_message)


def test_wrapper_normalizes_blank_xml_response():
    ws = DummyWS("\n")
    ws.fail()
    assert ws.XmlResponse == ""
    assert ws.XmlRequest == "<request/>"


def test_wrapper_keeps_non_blank_xml_response():
    ws = DummyWS("<xml>ok</xml>".encode("utf-8"))
    ws.fail()
    assert ws.XmlResponse == "<xml>ok</xml>"


def test_wrapper_adds_http_detail_for_empty_parse_error():
    ws = DummyWS("\n", "ExpatError: no element found: line 2, column 0")
    ws.client.response = {"status": "200"}
    ws.client.content = "\n"
    ws.fail()
    assert "response_len=1" in ws.Excepcion
    assert "HTTP status=200" in ws.Excepcion

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
    def __init__(self, xml_response):
        self.client = DummyClient("<request/>", xml_response)
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
        raise RuntimeError("simulated parse error")


def test_wrapper_normalizes_blank_xml_response():
    ws = DummyWS("\n")
    ws.fail()
    assert ws.XmlResponse == ""
    assert ws.XmlRequest == "<request/>"


def test_wrapper_keeps_non_blank_xml_response():
    ws = DummyWS("<xml>ok</xml>".encode("utf-8"))
    ws.fail()
    assert ws.XmlResponse == "<xml>ok</xml>"

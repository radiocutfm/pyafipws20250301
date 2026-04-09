#!/usr/bin/python
# -*- coding: utf8 -*-

import pytest

from pyafipws.wsfexv1 import WSFEXv1


pytestmark = [pytest.mark.dontusefix]


class DummyClient(object):
    def __init__(self, cae="123"):
        self.cae = cae
        self.getcmp_calls = 0
        self.xml_request = "<request/>"
        self.xml_response = "\n"
        self.response = {"status": "200"}
        self.content = "\n"

    def FEXAuthorize(self, **kwargs):
        self.xml_response = "\n"
        self.content = "\n"
        raise Exception("ExpatError: no element found: line 2, column 0")

    def FEXGetCMP(self, **kwargs):
        self.getcmp_calls += 1
        self.xml_response = "<soap/>"
        self.content = "<soap/>"
        if self.cae:
            return {
                "FEXGetCMPResult": {
                    "FEXResultGet": {
                        "Obs": "",
                        "Cae": self.cae,
                        "Fch_venc_Cae": "20260430",
                        "Fecha_cbte": "20260409",
                        "Punto_vta": 7,
                        "Resultado": "A",
                        "Cbte_nro": 123,
                        "Imp_total": "10.0",
                    }
                }
            }
        return {
            "FEXGetCMPResult": {
                "FEXResultGet": {
                    "Obs": "",
                    "Cae": "",
                    "Fch_venc_Cae": "",
                    "Fecha_cbte": "20260409",
                    "Punto_vta": 7,
                    "Resultado": "",
                    "Cbte_nro": 123,
                    "Imp_total": "10.0",
                }
            }
        }


def make_ws(client):
    ws = WSFEXv1()
    ws.client = client
    ws.Token = "token"
    ws.Sign = "sign"
    ws.Cuit = 20314624301
    ws.CrearFactura(
        tipo_cbte=19,
        punto_vta=7,
        cbte_nro=123,
        fecha_cbte="20260409",
        imp_total=10.0,
        tipo_expo=1,
        pais_dst_cmp=203,
        nombre_cliente="Cliente",
        cuit_pais_cliente="50000000016",
        domicilio_cliente="Rua 123",
        id_impositivo="PJ",
        moneda_id="DOL",
        moneda_ctz=1.0,
        idioma_cbte=1,
    )
    return ws


def test_authorize_recovers_cae_from_getcmp_after_empty_response(monkeypatch):
    monkeypatch.setattr("pyafipws.wsfexv1.time.sleep", lambda _: None)
    client = DummyClient(cae="123")
    ws = make_ws(client)

    cae = ws.Authorize(1)

    assert cae == "123"
    assert ws.Reproceso == "S"
    assert ws.Resultado == "A"
    assert client.getcmp_calls == 1


def test_authorize_raises_after_getcmp_retries_without_cae(monkeypatch):
    monkeypatch.setattr("pyafipws.wsfexv1.time.sleep", lambda _: None)
    client = DummyClient(cae="")
    ws = make_ws(client)

    with pytest.raises(Exception) as exc_info:
        ws.Authorize(1)

    assert "no element found" in str(exc_info.value).lower()
    assert client.getcmp_calls == 3

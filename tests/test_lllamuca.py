"""Prueba Top-Down del rechazo de pedidos por inventario insuficiente.

Se ejecuta el OrderService real desde la capa de negocio. FakeDb sustituye la
persistencia real con almacenamiento en memoria, y un Mock sustituye al
PaymentGateway; ambos son dependencias simuladas.
"""

import pytest

from app.order_service import OrderService, OutOfStockError
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_inventario_insuficiente_no_cobra_ni_registra_pedido(mocker):
    db = FakeDb(stock={"CUADERNO": 1}, prices={"CUADERNO": 10.0})
    payment_gateway = mocker.Mock(spec=PaymentGateway)
    service = OrderService(db, payment_gateway)

    with pytest.raises(OutOfStockError):
        service.place_order("CUADERNO", 2, "tok_prueba")

    payment_gateway.charge.assert_not_called()
    assert db.orders == {}
    assert db.get_stock("CUADERNO") == 1

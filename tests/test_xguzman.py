import pytest
from app.order_service import OrderService, PaymentRejectedError
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_pago_rechazado_no_registra_pedido_ni_descuenta_inventario(requests_mock):
    db = FakeDb(stock={"CUADERNO": 10}, prices={"CUADERNO": 5.0})

    gateway = PaymentGateway()
    requests_mock.post(
        f"{gateway.BASE_URL}/charges",
        json={"approved": False, "reason": "insufficient_funds"},
        status_code=402,
    )

    service = OrderService(db, gateway)

    with pytest.raises(PaymentRejectedError):
        service.place_order(
            product_id="CUADERNO",
            quantity=2,
            card_token="tok_sin_fondos",
        )

    assert len(db.orders) == 0
    assert db.get_stock("CUADERNO") == 10

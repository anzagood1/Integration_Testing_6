from app.order_service import OrderService
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_pedido_aprobado_calcula_iva_cobra_y_registra_pedido(requests_mock):
    db = FakeDb(stock={"CUADERNO": 5}, prices={"CUADERNO": 10.00})
    gateway = PaymentGateway()
    pago_url = f"{gateway.BASE_URL}/charges"
    requests_mock.post(
        pago_url,
        status_code=200,
        json={"transaction_id": "tx_123"},
    )
    service = OrderService(db, gateway)

    result = service.place_order("CUADERNO", 2, "tok_prueba")

    assert result == {"order_id": "ORD-1", "total": 23.2, "status": "CONFIRMED"}
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json() == {
        "card_token": "tok_prueba",
        "amount": 23.2,
    }
    assert db.orders == {
        "ORD-1": {
            "product_id": "CUADERNO",
            "quantity": 2,
            "total": 23.2,
            "transaction_id": "tx_123",
        }
    }

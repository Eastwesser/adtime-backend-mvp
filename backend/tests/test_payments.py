from uuid import uuid4
from app.schemas.payment import PaymentResponse
from app.core.errors import NotFoundError

async def test_payment_creation(mock_db_session, mock_payment_gateway):
    from app.services.payment import PaymentService
    from app.repositories.payment import PaymentRepository
    
    # Setup
    repo = PaymentRepository(mock_db_session)
    service = PaymentService(repo)
    service.yookassa = mock_payment_gateway
    
    # Test
    order_id = uuid4()
    result = await service.create_payment(mock_db_session, order_id, 1000)
    
    # Assert
    assert isinstance(result, PaymentResponse)
    mock_payment_gateway.create_payment.assert_called_once()
    mock_db_session.commit.assert_called_once()

async def test_payment_not_found(mock_db_session):
    from app.services.payment import PaymentService
    from app.repositories.payment import PaymentRepository
    
    repo = PaymentRepository(mock_db_session)
    service = PaymentService(repo)
    
    mock_db_session.execute.return_value = MagicMock(scalar_one_or_none=lambda: None)
    
    with pytest.raises(NotFoundError):
        await service.get_payment_status(mock_db_session, uuid4())
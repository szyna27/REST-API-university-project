class CompleteOrderCommand:
    command_name = "CompleteOrderCommand"

    def __init__(
        self, 
        operator_id: int,
        order_id: int,
        idempotency_key: str,
        ordered_by: str,
        source: str = "API",
        notify_email: bool = True,
        notify_push: bool = False,
        note: str | None = None,
    ) -> None:
        self.operator_id = operator_id
        self.order_id = order_id
        self.idempotency_key = idempotency_key
        self.ordered_by = ordered_by
        self.source = source
        self.notify_email = notify_email
        self.notify_push = notify_push
        self.note = note
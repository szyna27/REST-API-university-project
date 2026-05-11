from dataclasses import dataclass

@dataclass(frozen=True)
class ConfirmOrderCommand:
    operator_id: int

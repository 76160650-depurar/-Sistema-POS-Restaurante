
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List
from .exceptions import ValidationError, InvalidStateError


@dataclass
class Dish:
    name: str
    price: float
    available: bool = True

    def __post_init__(self):
        self.name = self.name.strip()
        if not self.name:
            raise ValidationError("El nombre del plato es obligatorio.")
        if self.price <= 0:
            raise ValidationError("El precio debe ser mayor que cero.")


class TableStatus(str, Enum):
    FREE = "libre"
    OCCUPIED = "ocupada"


class OrderStatus(str, Enum):
    PENDING = "pendiente"
    PREPARING = "en preparación"
    READY = "listo"
    DELIVERED = "entregado"
    CANCELLED = "cancelado"


@dataclass
class OrderLine:
    dish_name: str
    unit_price: float
    quantity: int

    def __post_init__(self):
        if self.quantity < 1:
            raise ValidationError("La cantidad debe ser al menos 1.")
        if self.unit_price <= 0:
            raise ValidationError("El precio unitario debe ser mayor que cero.")

    @property
    def subtotal(self) -> float:
        return round(self.unit_price * self.quantity, 2)


@dataclass
class Order:
    order_id: int
    table_number: int
    lines: List[OrderLine] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING

    @property
    def total(self) -> float:
        return round(sum(line.subtotal for line in self.lines), 2)

    def add_line(self, dish: Dish, quantity: int) -> None:
        if self.status in (OrderStatus.CANCELLED, OrderStatus.DELIVERED):
            raise InvalidStateError("No se puede modificar un pedido cerrado.")
        if not dish.available:
            raise ValidationError(f"El plato '{dish.name}' no está disponible.")
        self.lines.append(OrderLine(dish.name, dish.price, quantity))

    def change_status(self, new_status: OrderStatus) -> None:
        allowed = {
            OrderStatus.PENDING: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
            OrderStatus.PREPARING: {OrderStatus.READY, OrderStatus.CANCELLED},
            OrderStatus.READY: {OrderStatus.DELIVERED},
            OrderStatus.DELIVERED: set(),
            OrderStatus.CANCELLED: set(),
        }
        if new_status not in allowed[self.status]:
            raise InvalidStateError(
                f"No se permite cambiar de '{self.status.value}' a '{new_status.value}'."
            )
        self.status = new_status


@dataclass
class RestaurantTable:
    number: int
    status: TableStatus = TableStatus.FREE

    def occupy(self) -> None:
        if self.status == TableStatus.OCCUPIED:
            raise InvalidStateError(f"La mesa {self.number} ya está ocupada.")
        self.status = TableStatus.OCCUPIED

    def release(self) -> None:
        self.status = TableStatus.FREE

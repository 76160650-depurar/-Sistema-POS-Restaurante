"""Casos de uso y reglas de negocio del restaurante."""
from dataclasses import asdict
from typing import Dict
from src.domain.models import Dish, Order, OrderStatus, RestaurantTable
from src.domain.exceptions import NotFoundError, ValidationError
from src.services.data_manager import DataManager


class RestaurantService:
    def __init__(self, data_manager: DataManager | None = None):
        self.menu: Dict[str, Dish] = {}
        self.tables: Dict[int, RestaurantTable] = {}
        self.orders: Dict[int, Order] = {}
        self._next_order_id = 1
        self.data_manager = data_manager or DataManager()

    def add_dish(self, name: str, price: float) -> Dish:
        dish = Dish(name, price)
        key = dish.name.casefold()
        if key in self.menu:
            raise ValidationError("Ya existe un plato con ese nombre.")
        self.menu[key] = dish
        return dish

    def list_menu(self):
        return list(self.menu.values())

    def add_table(self, number: int) -> RestaurantTable:
        if number < 1:
            raise ValidationError("El número de mesa debe ser positivo.")
        if number in self.tables:
            raise ValidationError("La mesa ya está registrada.")
        table = RestaurantTable(number)
        self.tables[number] = table
        return table

    def create_order(self, table_number: int) -> Order:
        table = self.tables.get(table_number)
        if table is None:
            raise NotFoundError("La mesa no existe.")
        table.occupy()
        order = Order(self._next_order_id, table_number)
        self.orders[order.order_id] = order
        self._next_order_id += 1
        return order

    def add_item(self, order_id: int, dish_name: str, quantity: int) -> Order:
        order = self.orders.get(order_id)
        if order is None:
            raise NotFoundError("El pedido no existe.")
        dish = self.menu.get(dish_name.casefold())
        if dish is None:
            raise NotFoundError("El plato no existe en el menú.")
        order.add_line(dish, quantity)
        return order

    def change_order_status(self, order_id: int, status: OrderStatus) -> Order:
        order = self.orders.get(order_id)
        if order is None:
            raise NotFoundError("El pedido no existe.")
        order.change_status(status)
        if status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
            self.tables[order.table_number].release()
        return order

    def get_order(self, order_id: int) -> Order:
        try:
            return self.orders[order_id]
        except KeyError as exc:
            raise NotFoundError("El pedido no existe.") from exc

    def save_snapshot(self) -> None:
        payload = {
            "menu": [
                {"name": d.name, "price": d.price, "available": d.available}
                for d in self.menu.values()
            ],
            "tables": [
                {"number": t.number, "status": t.status.value}
                for t in self.tables.values()
            ],
            "orders": [
                {
                    "order_id": o.order_id,
                    "table_number": o.table_number,
                    "status": o.status.value,
                    "lines": [
                        {"dish_name": l.dish_name, "unit_price": l.unit_price,
                         "quantity": l.quantity, "subtotal": l.subtotal}
                        for l in o.lines
                    ],
                    "total": o.total,
                }
                for o in self.orders.values()
            ],
            "next_order_id": self._next_order_id,
        }
        self.data_manager.save(payload)

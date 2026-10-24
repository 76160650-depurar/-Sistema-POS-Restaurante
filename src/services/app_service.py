from typing import Dict

from src.domain.models import (
    Dish,
    Order,
    OrderLine,
    OrderStatus,
    RestaurantTable,
    TableStatus,
)
from src.domain.exceptions import NotFoundError, ValidationError
from src.services.data_manager import DataManager


class RestaurantService:
    def __init__(self, data_manager: DataManager | None = None):
        self.menu: Dict[str, Dish] = {}
        self.tables: Dict[int, RestaurantTable] = {}
        self.orders: Dict[int, Order] = {}
        self._next_order_id = 1
        self.data_manager = data_manager or DataManager()

        # Recuperar los datos guardados al iniciar el servicio.
        self.load_snapshot()

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

    def change_order_status(
        self, order_id: int, status: OrderStatus
    ) -> Order:
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
                {
                    "name": dish.name,
                    "price": dish.price,
                    "available": dish.available,
                }
                for dish in self.menu.values()
            ],
            "tables": [
                {
                    "number": table.number,
                    "status": table.status.value,
                }
                for table in self.tables.values()
            ],
            "orders": [
                {
                    "order_id": order.order_id,
                    "table_number": order.table_number,
                    "status": order.status.value,
                    "lines": [
                        {
                            "dish_name": line.dish_name,
                            "unit_price": line.unit_price,
                            "quantity": line.quantity,
                            "subtotal": line.subtotal,
                        }
                        for line in order.lines
                    ],
                    "total": order.total,
                }
                for order in self.orders.values()
            ],
            "next_order_id": self._next_order_id,
        }

        self.data_manager.save(payload)

    def load_snapshot(self) -> None:
        """Recupera el menú, las mesas y los pedidos desde el archivo JSON."""
        payload = self.data_manager.load()

        if not payload:
            return

        for item in payload.get("menu", []):
            dish = Dish(item["name"], item["price"])
            dish.available = item.get("available", True)
            self.menu[dish.name.casefold()] = dish

        for item in payload.get("tables", []):
            table = RestaurantTable(item["number"])
            table.status = TableStatus(item["status"])
            self.tables[table.number] = table

        for item in payload.get("orders", []):
            order = Order(
                item["order_id"],
                item["table_number"],
            )
            order.status = OrderStatus(item["status"])

            for line_data in item.get("lines", []):
                line = OrderLine(
                    dish_name=line_data["dish_name"],
                    unit_price=line_data["unit_price"],
                    quantity=line_data["quantity"],
                )
                order.lines.append(line)

            self.orders[order.order_id] = order

        stored_next_id = payload.get("next_order_id", 1)
        highest_order_id = max(self.orders.keys(), default=0) + 1

        # Evitar reutilizar números de pedidos existentes.
        self._next_order_id = max(stored_next_id, highest_order_id)
"""Pruebas unitarias del dominio y los casos de uso."""

import tempfile
import unittest
from pathlib import Path

from src.domain.exceptions import InvalidStateError, ValidationError
from src.domain.models import (
    Dish,
    Order,
    OrderStatus,
    RestaurantTable,
)
from src.services.app_service import RestaurantService
from src.services.data_manager import DataManager


class DomainTests(unittest.TestCase):

    def test_dish_rejects_non_positive_price(self):
        with self.assertRaises(ValidationError):
            Dish("Sopa", 0)

    def test_order_total(self):
        order = Order(1, 1)
        order.add_line(Dish("Arroz con pollo", 18), 2)

        self.assertEqual(order.total, 36.00)

    def test_invalid_order_transition_is_rejected(self):
        order = Order(1, 1)

        with self.assertRaises(InvalidStateError):
            order.change_status(OrderStatus.DELIVERED)

    def test_table_cannot_be_occupied_twice(self):
        table = RestaurantTable(1)
        table.occupy()

        with self.assertRaises(InvalidStateError):
            table.occupy()

    def test_service_creates_and_totals_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            manager = DataManager(str(Path(tmp) / "test.json"))
            service = RestaurantService(manager)

            service.add_dish("Ceviche", 28)
            service.add_table(1)

            order = service.create_order(1)
            service.add_item(order.order_id, "Ceviche", 2)

            self.assertEqual(order.total, 56.00)

    def test_data_manager_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            manager = DataManager(str(Path(tmp) / "state.json"))
            manager.save({"ok": True, "count": 3})

            self.assertEqual(
                manager.load(),
                {"ok": True, "count": 3},
            )

    def test_delivered_order_cannot_receive_more_items(self):
        order = Order(1, 1)
        dish = Dish("Ceviche", 28)

        order.add_line(dish, 1)
        order.change_status(OrderStatus.PREPARING)
        order.change_status(OrderStatus.READY)
        order.change_status(OrderStatus.DELIVERED)

        with self.assertRaises(InvalidStateError):
            order.add_line(dish, 1)

    def test_cancelled_order_cannot_receive_more_items(self):
        order = Order(1, 1)
        dish = Dish("Ceviche", 28)

        order.change_status(OrderStatus.CANCELLED)

        with self.assertRaises(InvalidStateError):
            order.add_line(dish, 1)


if __name__ == "__main__":
    unittest.main()
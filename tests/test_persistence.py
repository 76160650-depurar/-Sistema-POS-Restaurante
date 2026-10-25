import tempfile
import unittest
from pathlib import Path

from src.domain.models import OrderStatus
from src.services.app_service import RestaurantService
from src.services.data_manager import DataManager


class PersistenceTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        json_path = Path(self.temp_dir.name) / "restaurant.json"
        self.data_manager = DataManager(str(json_path))

    def test_menu_and_tables_are_restored(self):
        service = RestaurantService(self.data_manager)
        service.add_dish("Lomo saltado", 25.50)
        service.add_dish("Chicha morada", 6.00)
        service.add_table(1)
        service.add_table(2)

        service.save_snapshot()
        restored = RestaurantService(self.data_manager)

        self.assertEqual(len(restored.menu), 2)
        self.assertEqual(restored.menu["lomo saltado"].price, 25.50)
        self.assertEqual(len(restored.tables), 2)

    def test_orders_and_next_id_are_restored(self):
        service = RestaurantService(self.data_manager)
        service.add_dish("Ceviche", 30.00)
        service.add_table(1)

        order = service.create_order(1)
        service.add_item(order.order_id, "Ceviche", 2)
        service.change_order_status(
            order.order_id,
            OrderStatus.PREPARING,
        )
        service.save_snapshot()

        restored = RestaurantService(self.data_manager)
        recovered_order = restored.get_order(order.order_id)

        self.assertEqual(recovered_order.status, OrderStatus.PREPARING)
        self.assertEqual(len(recovered_order.lines), 1)
        self.assertEqual(recovered_order.lines[0].quantity, 2)
        self.assertEqual(recovered_order.total, 60.00)
        self.assertEqual(
            restored._next_order_id,
            order.order_id + 1,
        )

    def test_empty_file_does_not_prevent_initialization(self):
        service = RestaurantService(self.data_manager)

        self.assertEqual(service.menu, {})
        self.assertEqual(service.tables, {})
        self.assertEqual(service.orders, {})
        self.assertEqual(service._next_order_id, 1)

    def test_active_order_restores_table_as_occupied(self):
        service = RestaurantService(self.data_manager)
        service.add_dish("Lomo saltado", 25.00)
        service.add_table(1)

        order = service.create_order(1)
        service.add_item(order.order_id, "Lomo saltado", 1)
        service.save_snapshot()

        restored = RestaurantService(self.data_manager)

        self.assertEqual(
            restored.tables[1].status.value,
            "ocupada",
        )

    def test_delivered_order_restores_table_as_free(self):
        service = RestaurantService(self.data_manager)
        service.add_dish("Lomo saltado", 25.00)
        service.add_table(1)

        order = service.create_order(1)
        service.add_item(order.order_id, "Lomo saltado", 1)

        service.change_order_status(
            order.order_id,
            OrderStatus.PREPARING,
        )
        service.change_order_status(
            order.order_id,
            OrderStatus.READY,
        )
        service.change_order_status(
            order.order_id,
            OrderStatus.DELIVERED,
        )
        service.save_snapshot()

        restored = RestaurantService(self.data_manager)

        self.assertEqual(
            restored.tables[1].status.value,
            "libre",
        )

    def test_complete_order_lifecycle_releases_table_and_persists_state(self):
        # Preparar el servicio, el menú y la mesa.
        service = RestaurantService(self.data_manager)
        service.add_dish("Lomo saltado", 25.00)
        service.add_table(1)

        # Crear el pedido y comprobar que la mesa quede ocupada.
        order = service.create_order(1)

        self.assertEqual(
            service.tables[1].status.value,
            "ocupada",
        )

        # Agregar productos y comprobar el total.
        service.add_item(order.order_id, "Lomo saltado", 2)

        self.assertEqual(order.total, 50.00)

        # Pasar el pedido a preparación.
        service.change_order_status(
            order.order_id,
            OrderStatus.PREPARING,
        )
        self.assertEqual(order.status, OrderStatus.PREPARING)

        # Marcar el pedido como listo.
        service.change_order_status(
            order.order_id,
            OrderStatus.READY,
        )
        self.assertEqual(order.status, OrderStatus.READY)

        # Entregar el pedido y comprobar que la mesa quede libre.
        service.change_order_status(
            order.order_id,
            OrderStatus.DELIVERED,
        )

        self.assertEqual(order.status, OrderStatus.DELIVERED)
        self.assertEqual(
            service.tables[1].status.value,
            "libre",
        )

        # Guardar y reconstruir el servicio para simular un reinicio.
        service.save_snapshot()
        restored = RestaurantService(self.data_manager)

        recovered_order = restored.get_order(order.order_id)

        self.assertEqual(
            recovered_order.status,
            OrderStatus.DELIVERED,
        )
        self.assertEqual(recovered_order.total, 50.00)
        self.assertEqual(
            restored.tables[1].status.value,
            "libre",
        )


if __name__ == "__main__":
    unittest.main()
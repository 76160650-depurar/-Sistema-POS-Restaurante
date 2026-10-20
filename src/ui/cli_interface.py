"""Interfaz de línea de comandos (CLI)."""
from src.domain.models import OrderStatus
from src.domain.exceptions import RestaurantError


class RestaurantCLI:
    def __init__(self, service):
        self.service = service

    def run(self):
        self._seed_demo_data()
        actions = {
            "1": self.show_menu,
            "2": self.create_order,
            "3": self.add_item,
            "4": self.show_order,
            "5": self.update_status,
            "6": self.save,
        }
        while True:
            print("\n=== SISTEMA POS - RESTAURANTE ===")
            print("1. Ver menú | 2. Crear pedido | 3. Agregar plato")
            print("4. Consultar pedido | 5. Cambiar estado | 6. Guardar")
            print("0. Salir")
            choice = input("Seleccione una opción: ").strip()
            if choice == "0":
                self.save()
                print("Hasta luego.")
                break
            action = actions.get(choice)
            if action is None:
                print("Opción no válida.")
                continue
            try:
                action()
            except (RestaurantError, ValueError) as exc:
                print(f"Error: {exc}")

    def _seed_demo_data(self):
        if not self.service.menu:
            for name, price in [
                ("Lomo saltado", 25.00), ("Ají de gallina", 20.00),
                ("Chicha morada", 6.00), ("Ceviche", 28.00),
            ]:
                self.service.add_dish(name, price)
        if not self.service.tables:
            for number in range(1, 6):
                self.service.add_table(number)

    def show_menu(self):
        print("\n--- MENÚ ---")
        for dish in self.service.list_menu():
            status = "Disponible" if dish.available else "No disponible"
            print(f"{dish.name}: S/ {dish.price:.2f} ({status})")

    def create_order(self):
        table_number = int(input("Número de mesa (1-5): "))
        order = self.service.create_order(table_number)
        print(f"Pedido #{order.order_id} creado para mesa {table_number}.")
        print("Use la opción 3 para agregar platos.")

    def add_item(self):
        order_id = int(input("Número de pedido: "))
        dish_name = input("Nombre del plato: ").strip()
        quantity = int(input("Cantidad: "))
        order = self.service.add_item(order_id, dish_name, quantity)
        print(f"Pedido #{order.order_id}; total actual: S/ {order.total:.2f}")

    def show_order(self):
        order = self.service.get_order(int(input("Número de pedido: ")))
        print(f"Pedido #{order.order_id} | Mesa {order.table_number}")
        print(f"Estado: {order.status.value}")
        for line in order.lines:
            print(f"- {line.dish_name} x{line.quantity}: S/ {line.subtotal:.2f}")
        print(f"TOTAL: S/ {order.total:.2f}")

    def update_status(self):
        order_id = int(input("Número de pedido: "))
        print("Estados: preparing, ready, delivered, cancelled")
        value = input("Nuevo estado: ").strip().lower()
        mapping = {
            "preparing": OrderStatus.PREPARING,
            "ready": OrderStatus.READY,
            "delivered": OrderStatus.DELIVERED,
            "cancelled": OrderStatus.CANCELLED,
        }
        if value not in mapping:
            raise ValueError("Estado no reconocido.")
        order = self.service.change_order_status(order_id, mapping[value])
        print(f"Pedido actualizado: {order.status.value}")

    def save(self):
        self.service.save_snapshot()
        print("Datos guardados en data/restaurant.json.")

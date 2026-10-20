# Sistema POS y Gestión de Pedidos para Restaurante

Aplicación académica en Python 3 con programación orientada a objetos y arquitectura por capas.

## Funcionalidades
- Menú de platos con validación de precios.
- Registro de mesas y control de ocupación.
- Creación de pedidos y cálculo automático de subtotales y total.
- Estados del pedido: pendiente, en preparación, listo, entregado y cancelado.
- Persistencia de una copia de datos en JSON.
- Pruebas unitarias con `unittest`.

## Requisitos
- Python 3.10 o superior.
- Visual Studio Code (recomendado).
- Git para el flujo colaborativo.

## Ejecución
Desde la carpeta raíz del proyecto:

```bash
python --version
python -m src.main
```

En Windows, si `python` no funciona, prueba `py -m src.main`.

## Pruebas
```bash
python -m unittest discover -s tests -v
```

## Arquitectura
- `src/domain/`: entidades, reglas del dominio y excepciones.
- `src/services/`: casos de uso y persistencia.
- `src/ui/`: interfaz de usuario por terminal.
- `src/main.py`: punto de entrada.
- `tests/`: pruebas automatizadas.

Consulta `architecture.md` para el diagrama Mermaid y las decisiones de diseño.

## Flujo colaborativo
Crear una rama por tarea, realizar commits pequeños, abrir un Pull Request hacia `main`, completar la plantilla, revisar el diff y ejecutar las pruebas antes de fusionar. No se deben inventar commits o evidencias: cada integrante debe trabajar con su propia cuenta y dejar constancia real de su contribución.

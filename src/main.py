
from src.services.app_service import RestaurantService
from src.ui.cli_interface import RestaurantCLI


def main():
    RestaurantCLI(RestaurantService()).run()


if __name__ == "__main__":
    main()

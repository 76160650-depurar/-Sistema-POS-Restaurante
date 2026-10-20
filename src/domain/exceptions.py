"""Excepciones del dominio."""


class RestaurantError(Exception):
    """Error base para operaciones del restaurante."""


class ValidationError(RestaurantError):
    """Se produce cuando los datos no son válidos."""


class NotFoundError(RestaurantError):
    """Se produce cuando no existe el elemento solicitado."""


class InvalidStateError(RestaurantError):
    """Se produce cuando una transición de estado no está permitida."""

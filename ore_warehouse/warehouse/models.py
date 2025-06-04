from django.db import models


class TruckModel(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Название модели",
        help_text="Название модели самосвала (например, БЕЛАЗ, Komatsu)",
    )
    max_capacity = models.PositiveIntegerField(
        verbose_name="Макс. грузоподъемность (т)",
        help_text="Максимальная грузоподъемность самосвала в тоннах",
    )

    class Meta:
        verbose_name = "Модель самосвала"
        verbose_name_plural = "Модели самосвалов"

    def __str__(self):
        return self.name


class DumpTruck(models.Model):
    board_number = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Бортовой номер",
        help_text="Уникальный бортовой номер самосвала",
    )
    model = models.ForeignKey(
        TruckModel,
        on_delete=models.CASCADE,
        verbose_name="Модель самосвала",
    )
    current_weight = models.FloatField(
        verbose_name="Текущий вес (т)",
        help_text="Вес груза, который перевозит самосвал (в тоннах)",
    )
    si_percent = models.FloatField(
        verbose_name="% SiO₂",
        help_text="Процентное содержание диоксида кремния в руде",
    )
    fe_percent = models.FloatField(
        verbose_name="% Fe",
        help_text="Процентное содержание железа в руде",
    )

    unload_x = models.FloatField(
        null=True,
        blank=True,
        verbose_name="X разгрузки",
        help_text="Координата X точки разгрузки",
    )
    unload_y = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Y разгрузки",
        help_text="Координата Y точки разгрузки",
    )

    class Meta:
        verbose_name = "Самосвал"
        verbose_name_plural = "Самосвалы"

    def overload_percent(self):
        delta = self.current_weight - self.model.max_capacity
        return round(max(delta / self.model.max_capacity * 100, 0), 2)

    def __str__(self):
        return self.board_number


class Warehouse(models.Model):
    name = models.CharField(
        max_length=100,
        default="Склад",
        verbose_name="Название склада",
        help_text="Название или идентификатор склада",
    )
    initial_weight = models.FloatField(
        verbose_name="Начальный вес (т)",
        help_text="Объем руды на складе до разгрузки (в тоннах)",
    )
    initial_si = models.FloatField(
        verbose_name="% SiO₂ (нач.)",
        help_text="Начальное содержание диоксида кремния на складе (в долях, например 0.34)",
    )
    initial_fe = models.FloatField(
        verbose_name="% Fe (нач.)",
        help_text="Начальное содержание железа на складе (в долях, например 0.65)",
    )
    area_wkt = models.TextField(
        verbose_name="WKT-полигон склада",
        help_text="WKT-представление полигона, определяющего границу склада",
    )

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    def __str__(self):
        return self.name


__all__ = ()

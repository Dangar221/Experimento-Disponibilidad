from django.db import models

class Proyecto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    class Meta:
        db_table = 'proyectos'

class Recurso(models.Model):
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=100)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='recursos')
    class Meta:
        db_table = 'recursos'

class Consumo(models.Model):
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, related_name='consumos')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='consumos')
    cantidad = models.FloatField()
    costo = models.FloatField()
    fecha = models.DateField()
    class Meta:
        db_table = 'consumos'

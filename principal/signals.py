from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Matriculas , Calificaciones

# @receiver(post_save, sender= Matriculas)
# def create_marks(sender, instance, created, **kwargs):
#     if created:
#         Calificaciones.objects.create(
#             course=instance.course,
#             student=instance.student,
#             nota_1=0,
#             nota_2=0,
#             nota_3=0,
#             nota_4=0,
#             nota_5=0,
#             nota_6=0,
#             average=0
#         )



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

from django.db.models.signals import pre_save
from django.utils import timezone
from .models import Curso

@receiver(pre_save, sender=Curso)
def update_course_status(sender, instance, **kwargs):
    if instance.enrollment_deadline:
        if instance.enrollment_deadline < timezone.now().date() and instance.status == 'I':
            instance.status = 'IT'


@receiver(pre_save, sender=Curso)
def update_course_status(sender, instance, **kwargs):
    if instance.start_date:
        if instance.start_date <= timezone.now().date() and instance.status == 'IT':
            instance.status = 'P'



from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import FeedbackIA
from .ia.auto_treinamento import treinar_ia_automaticamente


@receiver(post_save, sender=FeedbackIA)
def retreinar_ia_apos_feedback(sender, instance, created, **kwargs):

    print("SIGNAL FEEDBACKIA DISPARADO")

    if created:
        print("NOVO FEEDBACK DETECTADO")
        treinar_ia_automaticamente()
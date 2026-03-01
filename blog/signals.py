from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from django.conf import settings
from blog.models import News, Post

User = get_user_model()


@receiver(post_save, sender=Post)
def email_important_news_notifications(sender, instance, **kwargs):
  """Отправка на email уведомлений при публикации важной новости"""
  if (
    hasattr(instance, 'news_item') and 
    instance.news_item.is_important and 
    instance.status == 'published' and
    not instance.news_item.email_notifications_sent
  ):
    subscribers = User.objects.filter(subscribed_to_important_news=True)
    
    if subscribers.exists():
      subject = f"🔔 Важная новость: {instance.title}"

      html_message = render_to_string('blog/emails/important_news_notification.html', {
        'news': instance.news_item,
        'site_url': settings.SITE_URL
      })

      # Можно так (1):
      # for user in subscribers:
      #   # Отправляем email каждому подписчику
      #   send_mail(
      #     subject=subject,
      #     message="",
      #     html_message=html_message,
      #     from_email=settings.DEFAULT_FROM_EMAIL,
      #     recipient_list=[user.email]
      #   )

      # Можно ещё так (2):
      # send_mail(
      #   subject=subject,
      #   message="",
      #   html_message=html_message,
      #   from_email=settings.DEFAULT_FROM_EMAIL,
      #   recipient_list=[user.email for user in subscribers]
      # )

      # И ещё один вариант (3):
      recipient_emails = list(
        subscribers.values_list('email', flat=True) # Получаем только список email-адресов
      )
      # Если писать без flat=True, Django вернет список кортежей: [('admin@mail.ru',), ('user@mail.ru',)]
      # flat=True как раз «вынимает» значение из кортежа и делает список плоским: ['admin@mail.ru', 'user@mail.ru']

      send_mail(
        subject=subject,
        message="",
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_emails
      )
    
    # Помечаем, что уведомления отправлены
    instance.news_item.email_notifications_sent = True
    instance.news_item.save(update_fields=['email_notifications_sent'])


@receiver(post_delete, sender=News)
def delete_related_post(sender, instance, **kwargs):
  Post.objects.filter(id=instance.post_item_id).delete()

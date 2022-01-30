from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    image = models.ImageField(default="/static/media/images/default/default.png")
    status = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class SingleChat(models.Model):
    participant1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='participant1')
    participant2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='participant2')

    def __str__(self):
        return "Chat by {} and {}.".format(self.participant1.name, self.participant2.name)


class Messages(models.Model):
    chat = models.ForeignKey(SingleChat, on_delete=models.CASCADE)
    by = models.ForeignKey(Profile, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)




from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, help="Email пользователя")

    def handle(self, *args, **kwargs):
        email = kwargs["email"]

        user = CustomUser.objects.get(email=email)
        moderator_group = Group.objects.get(name="Moderator")

        user.groups.clear()

        if not user.groups.filter(name="Moderator").exists():
            user.groups.set([moderator_group])

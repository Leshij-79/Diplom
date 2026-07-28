from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        group_name_moderator = "Moderator"
        group_moderator, created_moderator = Group.objects.get_or_create(name=group_name_moderator)

        permissions = Permission.objects.filter(
            codename__in=[
                "can_block_user",
                "can_view_user",
                "can_view_message",
                "can_moderated_mailing",
                "can_view_mailing",
                "can_view_recipient",
            ],
        )

        group_moderator.permissions.set(permissions)

        if created_moderator:
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name_moderator}" создана'))

        group_name_user = "Users"
        group_user, created_user = Group.objects.get_or_create(name=group_name_user)

        if created_user:
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name_user}" создана'))

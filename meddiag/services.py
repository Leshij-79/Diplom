from meddiag.models import Direction


class ServicesServices:
    @staticmethod
    def services_direction(direction_id):
        direction_services = Direction.objects.filter(direction=direction_id)

        if not direction_services.exsits():
            return None

        return direction_services
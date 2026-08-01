from meddiag.models import Direction, Services


class ServicesServices:
    @staticmethod
    def services_direction(service_id):
        direction_services = Services.objects.filter(pk=service_id)

        if not direction_services.exists():
            return None

        return direction_services
from django.db import migrations

CELESTIAL_BODIES = [
    ("sun", "Солнце", "luminar"),
    ("moon", "Луна", "luminar"),
    ("mercury", "Меркурий", "planet"),
    ("venus", "Венера", "planet"),
    ("mars", "Марс", "planet"),
    ("jupiter", "Юпитер", "planet"),
    ("saturn", "Сатурн", "planet"),
    ("uranus", "Уран", "planet"),
    ("neptune", "Нептун", "planet"),
    ("pluto", "Плутон", "dwarf"),
    ("north_node", "Северный узел", "node"),
    ("south_node", "Южный узел", "node"),
    ("lilith", "Лилит", "point"),
]


def seed_celestial_bodies(apps, schema_editor):
    CelestialBody = apps.get_model("charts", "CelestialBody")
    for slug, name, body_type in CELESTIAL_BODIES:
        CelestialBody.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "body_type": body_type,
                "symbol": "",
            },
        )


def unseed_celestial_bodies(apps, schema_editor):
    CelestialBody = apps.get_model("charts", "CelestialBody")
    CelestialBody.objects.filter(slug__in=[slug for slug, _, _ in CELESTIAL_BODIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("charts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_celestial_bodies, unseed_celestial_bodies),
    ]

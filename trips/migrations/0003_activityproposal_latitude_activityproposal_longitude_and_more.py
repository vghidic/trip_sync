import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
from django.utils.text import slugify


def populate_trip_slugs(apps, schema_editor):
    Trip = apps.get_model('trips', 'Trip')
    used_slugs = set(
        Trip.objects.exclude(slug__isnull=True)
        .exclude(slug='')
        .values_list('slug', flat=True)
    )

    for trip in Trip.objects.filter(
        models.Q(slug__isnull=True) | models.Q(slug='')
    ).order_by('pk'):
        base_slug = slugify(trip.name) or 'trip'
        slug = base_slug
        suffix = 2
        while slug in used_slugs:
            slug = f'{base_slug}-{suffix}'
            suffix += 1
        Trip.objects.filter(pk=trip.pk).update(slug=slug)
        used_slugs.add(slug)


class Migration(migrations.Migration):

    dependencies = [
        ("trips", "0002_readonlysharelink"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="activityproposal",
            name="latitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("-90")),
                    django.core.validators.MaxValueValidator(Decimal("90")),
                ],
            ),
        ),
        migrations.AddField(
            model_name="activityproposal",
            name="longitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("-180")),
                    django.core.validators.MaxValueValidator(Decimal("180")),
                ],
            ),
        ),
        migrations.AddField(
            model_name="activityproposal",
            name="status",
            field=models.CharField(
                choices=[
                    ("proposed", "Proposed"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("removed", "Removed"),
                ],
                default="proposed",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="destination",
            name="status",
            field=models.CharField(
                choices=[
                    ("proposed", "Proposed"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("removed", "Removed"),
                ],
                default="proposed",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="trip",
            name="slug",
            field=models.SlugField(
                blank=True,
                db_index=False,
                max_length=100,
                null=True,
            ),
        ),
        migrations.RunPython(
            populate_trip_slugs,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="trip",
            name="slug",
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
        migrations.CreateModel(
            name="AccommodationProposal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("address", models.CharField(blank=True, max_length=255)),
                (
                    "estimated_cost",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.00"))
                        ],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("proposed", "Proposed"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("removed", "Removed"),
                        ],
                        default="proposed",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "proposed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="accommodation_proposals",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accommodation_proposals",
                        to="trips.trip",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="trip",
            name="final_accommodation",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="final_for_trips",
                to="trips.accommodationproposal",
            ),
        ),
        migrations.CreateModel(
            name="TransferProposal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("route", models.CharField(blank=True, max_length=255)),
                (
                    "estimated_cost",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.00"))
                        ],
                    ),
                ),
                (
                    "duration_minutes",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("proposed", "Proposed"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("removed", "Removed"),
                        ],
                        default="proposed",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "proposed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transfer_proposals",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transfer_proposals",
                        to="trips.trip",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="trip",
            name="final_transfer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="final_for_trips",
                to="trips.transferproposal",
            ),
        ),
        migrations.CreateModel(
            name="TripInvitation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("token_hash", models.CharField(max_length=128, unique=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "accepted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="accepted_trip_invitations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_trip_invitations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invitations",
                        to="trips.trip",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AccommodationVote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "accommodation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="votes",
                        to="trips.accommodationproposal",
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accommodation_votes",
                        to="trips.trip",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="accommodation_votes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("trip", "user"),
                        name="unique_accommodation_vote_per_trip_user",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="TransferVote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "transfer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="votes",
                        to="trips.transferproposal",
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transfer_votes",
                        to="trips.trip",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transfer_votes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("trip", "user"),
                        name="unique_transfer_vote_per_trip_user",
                    )
                ],
            },
        ),
    ]

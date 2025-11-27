from django.db import models


# Create your models here.

class IPLists(models.Model):
    LIST_TYPE_CHOICES = [
        ('WHITELIST', 'Whitelist'),
        ('BLACKLIST', 'Blacklist'),
    ]
    network = models.CharField(max_length=43, unique=True)
    list_type = models.CharField(max_length=10, choices=LIST_TYPE_CHOICES, default='Blacklist')
    comment = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.network} ({self.list_type})"

class ThreatLog(models.Model):
    """
    Model reprezentujący pojedynczy wpis logu THREAT z Palo Alto (PAN-OS).
    Zapisane są tylko dane w polach numer:
        6 	- Generated Time
        7 	- Source Address
        11 	- Rule Name
        14 	- Application
        23 	- Repeat Count
        8 	- Destination Address
        25 	- Destination Port
        28 	- Flags
        32 	- Threat ID
        38 	- Source Location
        69 	- Threat Category
        73 	- Payload Protocol ID
    """

    generated_time = models.DateTimeField(
        db_index=True,
        help_text="Czas wygenerowania logu przez firewall (Generated Time)"
    )

    source_address = models.GenericIPAddressField(
        db_index=True,
        help_text="Adres IP źródła (Source Address)"
    )

    rule_name = models.CharField(
        max_length=128,
        db_index=True,
        help_text="Nazwa reguły, która dopasowała ruch (Rule Name)"
    )

    application = models.CharField(
        max_length=128,
        help_text="Zidentyfikowana aplikacja (Application)"
    )

    repeat_count = models.PositiveIntegerField(
        default=1,
        help_text="Liczba powtórzeń zdarzenia w krótkim czasie (Repeat Count)"
    )

    destination_address = models.GenericIPAddressField(
        db_index=True,
        help_text="Adres IP źródła (Destination Address)"
    )

    destination_port = models.PositiveIntegerField(
        db_index=True,
        help_text="Port docelowy (Destination Port)"
    )

    flags = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Flagi sesji TCP (Flags)"
    )

    threat_id = models.CharField(
        max_length=512,
        db_index=True,
        help_text="Identyfikator zagrożenia lub sygnatury, opis (Threat ID)"
    )

    source_location = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Lokalizacja geograficzna źródła (Source Location)"
    )

    threat_category = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        db_index=True,
        help_text="Kategoria zagrożenia (Threat Category)"
    )

    payload_protocol_id = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="Identyfikator protokołu w ładunku (Payload Protocol ID)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Czas dodania logu do bazy danych"
    )

    processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Czy ten log został już przetworzony przez background worker"
    )

    class Meta:
        indexes = [
            models.Index(fields=["source_address", "generated_time"]),
            models.Index(fields=["application", "destination_port"]),
            models.Index(fields=["threat_category"]),
            models.Index(fields=["processed"]),
        ]
        verbose_name = "Threat Log"
        verbose_name_plural = "Threat Logs"
        ordering = ["-generated_time"]

    def __str__(self):
        return f"{self.generated_time} | {self.source_address} → {self.destination_port} | {self.threat_id}"

class FailedLoginSummary(models.Model):
    source_address = models.GenericIPAddressField(db_index=True)
    last_attempt = models.DateTimeField()
    attempts_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Czy ten log został już przetworzony przez background worker"
    )


    class Meta:
        indexes = [
            models.Index(fields=["source_address", "last_attempt"]),
            models.Index(fields=["processed"]),
        ]

    def __str__(self):
        return f"{self.source_address} | {self.attempts_count} attempts"

class BlockedAddress(models.Model):
    """
    Model przechowujący informacje o blokadach nakładanych na adresy IP.
    """

    address = models.GenericIPAddressField(
        db_index=True,
        help_text="Adres IP, na który została nałożona blokada"
    )

    start_time = models.DateTimeField(
        help_text="Data i czas rozpoczęcia blokady"
    )

    block_number = models.PositiveSmallIntegerField(
        choices=[(1, "Blokada 1"), (2, "Blokada 2"), (3, "Blokada 3"), (4, "Blokada 4")],
        help_text="Numer blokady (od 1 do 4)"
    )

    end_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Data zdjęcia blokady"
    )

    is_blocked = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Czy blokada jest obecnie aktywna"
    )

    requires_unblock: bool = models.BooleanField(
        default=False,
        help_text="Czy adres czeka na odblokowanie (np. przez automat lub admina)"
    )

    was_unblocked = models.BooleanField(
        default=False,
        help_text="Czy blokada została już zdjęta"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Czas dodania wpisu do bazy"
    )

    processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Czy wpis blokady został już przetworzony przez background worker"
    )

    class Meta:
        indexes = [
            models.Index(fields=["address", "is_blocked"]),
            models.Index(fields=["block_number"]),
            models.Index(fields=["processed"]),
        ]
        verbose_name = "Blocked Address"
        verbose_name_plural = "Blocked Addresses"
        ordering = ["-start_time"]

    def __str__(self):
        if self.block_number == 4:
            block = "permanentna"
        else:
            block = self.block_number
        return f"{self.address} | blokada {block} | aktywna={self.is_blocked} | do={self.end_time}"
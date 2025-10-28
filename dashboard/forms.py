from django import forms

class SettingsForm(forms.Form):
    bot_frequency = forms.DurationField(
        label="Częstotliwość działania bota",
        help_text="Jak często bot ma się uruchamiać (np. co 5 minut: 0:05:00).",
        initial="0:03:00",
    )

    failed_attempts_limit = forms.IntegerField(
        label="Ilość nieudanych prób logowania przed zablokowaniem",
        min_value=1,
        max_value=100,
        initial=5,
        help_text="Po tylu błędnych próbach adres IP zostanie zablokowany."
    )

    reset_attempts_time = forms.DurationField(
        label="Czas po którym resetuje się liczba nieudanych prób",
        help_text="Po tym czasie bez prób, liczba błędnych logowań zostanie wyzerowana.",
        initial="1:00:00",  # 1 h
    )

    block_duration_1 = forms.DurationField(
        label="Czas trwania 1. blokady",
        initial="0:10:00",  # 10 min
        help_text="Czas trwania pierwszej blokady IP."
    )
    block_duration_2 = forms.DurationField(
        label="Czas trwania 2. blokady",
        initial="1:00:00",
        help_text="Czas trwania drugiej blokady IP."
    )
    block_duration_3 = forms.DurationField(
        label="Czas trwania 3. blokady",
        initial="24:00:00",  # 1 dzień
        help_text="Czas trwania trzeciej blokady IP."
    )

    permanent_block = forms.BooleanField(
        label="Czy stosować permanentną blokadę po 4. naruszeniu?",
        required=False,
        initial=True,
    )

    whitelist_enabled = forms.BooleanField(
        label="Czy włączyć listę dozwolonych adresów (whitelist)?",
        required=False,
        initial=True,
        help_text="Adresy z whitelist nie będą blokowane."
    )

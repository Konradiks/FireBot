import json

from django.http import HttpResponse
from django.shortcuts import redirect

from FireBot.functions import get_firewall_address
from FireBot.models import IPLists, BlockedAddress
from django.contrib.auth.decorators import login_required
from . import forms
from .models import Settings
from django.contrib import messages
from django.apps import apps
from django.db.models import Sum
from FireBot.models import ThreatLog
from django.utils import timezone
import datetime as _dt
from datetime import timedelta
from django.shortcuts import render

from .functions import (gen_panos_securityrules_block, get_command_html, db_mark_block_ip_addresses,
                        db_mark_unblock_ip_addresses, gen_panos_securityrules_unblock, get_commit_command)

debug = False

@login_required
def dashboard_Main(request):
    return redirect('/dashboard/statistics/')

@login_required
def blacklist_page(request):
    blacklist = IPLists.objects.filter(list_type="BLACKLIST")
    block_list = BlockedAddress.objects.filter(
        is_blocked=True
    ).order_by('block_number')

    return render(request, 'dashboard/blacklist.html', {'blacklist': blacklist, 'block_list': block_list})


@login_required
def blocked_view(request):
    block_list = BlockedAddress.objects.filter(
        is_blocked=True
    ).order_by('block_number')
    return render(request, 'dashboard/blocked.html', {'block_list': block_list})
@login_required


@login_required
def whitelist_page(request):
    whitelist = IPLists.objects.filter(list_type="WHITELIST")
    return render(request, 'dashboard/whitelist.html', {'whitelist': whitelist})

@login_required
def mode_page(request):
    if request.method == "POST":
        selected_addresses = request.POST.getlist('addresses')
        # selected_addresses to lista adresów wybranych przez użytkownika
        print(selected_addresses)
        # dalej możesz je np. zablokować w bazie

    settings = Settings.objects.first()
    automated = settings.executor_automated
    if automated is False:
        to_block_list = BlockedAddress.objects.filter(
            was_unblocked=False,
            end_time__gte=timezone.localtime(),
            is_blocked=False
        )
        to_unblock_list = BlockedAddress.objects.filter(
            is_blocked=True,
            end_time__lte=timezone.localtime(),
            was_unblocked=False,
            requires_unblock=True
        )

    else:
        to_block_list = None
        to_unblock_list = None
    return render(request, 'dashboard/mode.html', {
        'automated': automated,
        "to_block_list": to_block_list,
        "to_unblock_list": to_unblock_list,
        })

@login_required
def gen_block_command(request):
    if request.method == "POST":
        # Pobieramy wszystkie adresy z formularza
        selected_addresses = request.POST.getlist('addresses')

        if selected_addresses:
            if debug:
                print("Blokuję wszystkie:", selected_addresses)
            db_mark_block_ip_addresses(selected_addresses)
            command = gen_panos_securityrules_block(host=get_firewall_address(), ip_list=selected_addresses)
            command += get_commit_command(host=get_firewall_address())
            command += "\n" # auto wysłanie

            return HttpResponse(get_command_html(command))

    return redirect('/dashboard/mode/')

@login_required
def gen_unblock_command(request):
    if request.method == "POST":
        # Pobieramy wszystkie adresy z formularza
        selected_addresses = request.POST.getlist('addresses')

        if selected_addresses:
            if debug:
                print("Odblokuję wszystkie:", selected_addresses)

            db_mark_unblock_ip_addresses(selected_addresses)
            command = gen_panos_securityrules_unblock(host=get_firewall_address(), ip_list=selected_addresses)
            command += get_commit_command(host=get_firewall_address())
            command += "\n" # auto wysłanie

            return HttpResponse(get_command_html(command))

        return redirect('/dashboard/mode/')

    return redirect('/dashboard/mode/')

@login_required
def settings_page(request):
    # Pobierz pierwszy rekord lub utwórz domyślny
    settings = Settings.objects.first()
    if not settings:
        settings = Settings.objects.create()

    # Usuń wszystkie inne rekordy
    Settings.objects.exclude(pk=settings.pk).delete()

    if request.method == "POST":
        form = forms.SettingsForm2(request.POST)
        if form.is_valid():
            log_ip = form.cleaned_data.get("log_server_ip")
            log_port = form.cleaned_data.get("log_server_port")
            reset_attempts_time = form.cleaned_data.get("reset_attempts_time")
            sleep_time = form.cleaned_data.get("bot_frequency")
            Settings.objects.all().delete()
            try:

                form.save()
                if form.cleaned_data.get("executor_automated") == True:
                    messages.info(request, "Brak implementacji połączenia z API")
                    s = Settings.objects.first()
                    print(s)
                    s.executor_automated = False
                    s.save(update_fields=['executor_automated'])
                    print(s.executor_automated)
                messages.success(request, 'Settings saved.')
            except Exception as e:
                messages.error(request, e)
                return redirect('/dashboard/settings/')
            # WORKERS RESTART
            worker_config = apps.get_app_config('worker')
            worker_config.log_fetcher_restart(ip=log_ip, port=log_port)
            worker_config.log_analyzer_restart(sleep_time=sleep_time,reset_attempts_time=reset_attempts_time)
            worker_config.action_executor_restart()

            return redirect('/dashboard/settings/')

    if request.method == "GET":
        form = forms.SettingsForm2(instance=settings)
        return render(request, 'dashboard/settings.html', {'form': form})

@login_required
def statistics_page(request):
    # GET params: start_date, end_date (ISO: YYYY-MM-DD), granularity: hour|day
    from django.http import HttpResponse
    import json
    from django.db.models.functions import TruncHour, TruncDay

    # Defaults: last 24 hours
    try:
        end_date = request.GET.get('end_date')
        start_date = request.GET.get('start_date')
        granularity = request.GET.get('granularity', 'hour')

        if end_date:
            # jeśli przekazano tylko datę (YYYY-MM-DD), traktujemy ją jako koniec dnia
            try:
                d = _dt.date.fromisoformat(end_date)
                end_dt = timezone.make_aware(_dt.datetime.combine(d, _dt.time.max))
            except Exception:
                # fallback: spróbuj sparsować jako pełne datetime
                end_dt = timezone.make_aware(timezone.datetime.fromisoformat(end_date))
        else:
            end_dt = timezone.localtime()

        if start_date:
            # jeśli przekazano tylko datę (YYYY-MM-DD), traktujemy ją jako początek dnia
            try:
                d = _dt.date.fromisoformat(start_date)
                start_dt = timezone.make_aware(_dt.datetime.combine(d, _dt.time.min))
            except Exception:
                # fallback: spróbuj sparsować jako pełne datetime
                start_dt = timezone.make_aware(timezone.datetime.fromisoformat(start_date))
        else:
            # default to 24 hours before end_dt
            start_dt = end_dt - timedelta(hours=24)
    except Exception:
        # fallback to last 24 hours
        end_dt = timezone.localtime()
        start_dt = end_dt - timedelta(hours=24)
        granularity = 'hour'

    qs = ThreatLog.objects.filter(generated_time__gte=start_dt, generated_time__lte=end_dt)

    # Time series aggregation
    # We aggregate in Python to allow custom bucket sizes:
    # - when granularity == 'hour'  -> bucket size = 10 minutes
    # - when granularity == 'day'   -> bucket size = 1 hour
    logs = qs.values('generated_time', 'repeat_count').order_by('generated_time')

    buckets = {}
    tz = timezone.get_current_timezone()

    if granularity == 'day':
        # bucket to hours
        def make_bucket(dt):
            dt = dt.astimezone(tz)
            return dt.replace(minute=0, second=0, microsecond=0)
        step = timedelta(hours=1)
    else:
        # default: 'hour' -> bucket to 10-minute intervals
        def make_bucket(dt):
            dt = dt.astimezone(tz)
            minute = (dt.minute // 10) * 10
            return dt.replace(minute=minute, second=0, microsecond=0)
        step = timedelta(minutes=10)

    for row in logs:
        gen = row['generated_time']
        cnt = row.get('repeat_count') or 0
        if gen is None:
            continue
        bucket = make_bucket(gen)
        buckets[bucket] = buckets.get(bucket, 0) + cnt

    # Build ordered time series covering full range (including empty buckets)
    # Align start_dt to bucket boundary
    if granularity == 'day':
        start_aligned = start_dt.astimezone(tz).replace(minute=0, second=0, microsecond=0)
    else:
        sd = start_dt.astimezone(tz)
        start_aligned = sd.replace(minute=(sd.minute // 10) * 10, second=0, microsecond=0)

    end_aligned = end_dt.astimezone(tz)
    # ensure inclusive end: step to cover the last bucket
    # generate periods from start_aligned to end_aligned inclusive
    periods = []
    cur = start_aligned
    while cur <= end_aligned:
        periods.append(cur)
        cur = cur + step

    x_time = [p.isoformat() for p in periods]
    y_counts = [buckets.get(p, 0) for p in periods]

    # Additional metrics
    total_attempts = int(sum(y_counts)) if y_counts else 0
    unique_sources = qs.values('source_address').distinct().count()
    if y_counts:
        peak_count = int(max(y_counts))
        peak_time = x_time[y_counts.index(max(y_counts))]
    else:
        peak_count = 0
        peak_time = None

    # Pie: threat category distribution
    categories = qs.values('threat_category').annotate(count=Sum('repeat_count')).order_by('-count')
    pie = {c['threat_category'] or 'unknown': c['count'] for c in categories}

    # Top sources, destination ports, rules, countries
    top_sources = list(qs.values('source_address').annotate(count=Sum('repeat_count')).order_by('-count')[:10])
    top_ports = list(qs.values('destination_port').annotate(count=Sum('repeat_count')).order_by('-count')[:10])
    top_rules = list(qs.values('rule_name').annotate(count=Sum('repeat_count')).order_by('-count')[:10])
    top_countries = list(qs.values('source_location').annotate(count=Sum('repeat_count')).order_by('-count')[:10])
    top_dest = list(qs.values('destination_address').annotate(count=Sum('repeat_count')).order_by('-count')[:10])

    context = {
        'x_time_json': json.dumps(x_time),
        'y_time_json': json.dumps(y_counts),
        'pie_json': json.dumps(pie),
        'top_sources_json': json.dumps([{ 'source': s['source_address'], 'count': s['count']} for s in top_sources]),
        'top_ports_json': json.dumps([{ 'port': p['destination_port'], 'count': p['count']} for p in top_ports]),
        'top_rules_json': json.dumps([{ 'rule': r['rule_name'], 'count': r['count']} for r in top_rules]),
    'top_countries_json': json.dumps([{ 'country': c['source_location'] or 'unknown', 'count': c['count']} for c in top_countries]),
    'top_dest_json': json.dumps([{ 'destination': d['destination_address'], 'count': d['count']} for d in top_dest]),
        'start_date': start_dt.date().isoformat(),
        'end_date': end_dt.date().isoformat(),
        'granularity': granularity,
        'total_attempts': total_attempts,
        'unique_sources': unique_sources,
        'peak_count': peak_count,
        'peak_time': peak_time,
    }

    return render(request, "dashboard/statistics.html", context)


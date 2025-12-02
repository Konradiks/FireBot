# worker/apps.py
from sqlite3 import OperationalError

from django.apps import AppConfig
import os

from django.utils import timezone


class WorkerConfig(AppConfig):
    name = 'worker'

    log_fetcher = None
    log_analyzer = None

    def ready(self):
        """
        Uruchamiane automatycznie przy starcie Django
        (runserver, celery, testy, migrate itp.)
        """
        if os.environ.get('RUN_MAIN') != 'true':
            return  # nie startujemy w autoreload watcher

        from .classes import LogFetcher, LogAnalyzer, ActionExecutor
        from dashboard.models import Settings
        from django.db.utils import OperationalError
        from django.core.exceptions import ObjectDoesNotExist

        if hasattr(self, 'workers_started'):
            return  # zapobiega ponownemu startowi przy autoreload

        self.workers_started = True

        # Bezpieczne pobranie ustawień
        try:
            self.settings = Settings.objects.first()
            if not self.settings:
                # Jeśli nie ma rekordu, stworzymy domyślny
                self.settings = Settings.objects.create()
        except (OperationalError, ObjectDoesNotExist):
            # Tabela jeszcze nie istnieje (np. migrate nie było wykonane)
            self.settings = None
            return

        # if getattr(self, 'workers_started', False):
        #     return
        # self.workers_started = True

        # Teraz możesz korzystać z 'settings', jeśli nie jest None

        self.log_analyzer = LogAnalyzer(sleep_time=self.settings.bot_frequency, reset_attempts_time=self.settings.reset_attempts_time)
        self.log_fetcher = LogFetcher(ip=self.settings.log_server_ip, port=self.settings.log_server_port, allowed_ips=self.settings.get_allowed_log_sources())
        self.action_executor = ActionExecutor(
            unblock_ip_interval=self.settings.unblock_frequency,
            failed_attempts_limit=self.settings.failed_attempts_limit,
            block_duration_1=self.settings.block_duration_1,
            block_duration_2=self.settings.block_duration_2,
            block_duration_3=self.settings.block_duration_3,
            block_4_permanently=self.settings.permanent_block,
            block_period_reset_time=self.settings.block_period_reset_time,
            automated=self.settings.executor_automated,
            whitelist=self.settings.whitelist_enabled,
            sleep_time=self.settings.executor_frequency,
        )

        self.log_fetcher.open_udp_server()

        self.log_analyzer.daemon = True
        self.log_fetcher.daemon = True
        self.action_executor.daemon = True

        self.log_analyzer.start()
        self.log_fetcher.start()
        self.action_executor.start()


    def action_executor_restart(self):
        if self.action_executor:
            self.action_executor.stop()
            print(f"{self.name} restarting...")
        from worker.classes import ActionExecutor
        self.update_settings()
        self.action_executor = ActionExecutor(
            unblock_ip_interval=self.settings.unblock_frequency,
            failed_attempts_limit=self.settings.failed_attempts_limit,
            block_duration_1=self.settings.block_duration_1,
            block_duration_2=self.settings.block_duration_2,
            block_duration_3=self.settings.block_duration_3,
            block_4_permanently=self.settings.permanent_block,
            block_period_reset_time=self.settings.block_period_reset_time,
            automated=self.settings.executor_automated,
            whitelist=self.settings.whitelist_enabled,
            sleep_time=self.settings.executor_frequency,
        )
        self.action_executor.daemon = True
        self.action_executor.start()

    def log_fetcher_restart(self, ip=None, port=None, allowed_ips=None):
        if self.log_fetcher:
            self.log_fetcher.UDPServer.close()
            self.log_fetcher.stop()

        from worker.classes import LogFetcher
        if not ip:
            self.update_settings()
            ip = self.settings.log_server_ip

        if not port:
            self.update_settings()
            port = self.settings.log_server_port

        if not allowed_ips:
            self.update_settings()
            allowed_ips = self.settings.get_allowed_log_sources()


        self.log_fetcher = LogFetcher(ip=ip, port=port, allowed_ips=allowed_ips)
        self.log_fetcher.daemon = True
        self.log_fetcher.open_udp_server()
        self.log_fetcher.start()

    def log_analyzer_restart(self, sleep_time=None, reset_attempts_time=None):
        try:
            self.log_analyzer.stop()
        except OperationalError:
            pass

        from worker.classes import LogAnalyzer
        if not sleep_time:
            self.update_settings()
            sleep_time = self.settings.bot_frequency

        if not reset_attempts_time:
            self.update_settings()
            reset_attempts_time = self.settings.reset_attempts_time

        self.log_analyzer = LogAnalyzer(sleep_time=sleep_time, reset_attempts_time=reset_attempts_time)
        self.log_analyzer.daemon = True
        self.log_analyzer.start()

    def update_settings(self):
        try:
            from dashboard.models import Settings
            self.settings = Settings.objects.first()
            if not self.settings:
                # Jeśli nie ma rekordu, stworzymy domyślny
                self.settings = Settings.objects.create()
        except (OperationalError):
            # Tabela jeszcze nie istnieje (np. migrate nie było wykonane)
            self.settings = None
        return self.settings
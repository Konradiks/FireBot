# from django.apps import AppConfig
# import atexit
# from worker.manager import manager
#
# class FireBotConfig(AppConfig):
#     name = "FireBot"
#
#     def ready(self):
#         # start workerów
#         manager.start()
#
#         # zatrzymaj workerów na exit
#         atexit.register(manager.stop)

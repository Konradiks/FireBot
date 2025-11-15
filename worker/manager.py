# from worker.classes import LogFetcher, LogAnalyzer
#
# class WorkerManager:
#     def __init__(self):
#         self.workers = [
#             LogFetcher(),
#             LogAnalyzer(),
#         ]
#
#     def start(self):
#         for w in self.workers:
#             w.start()
#
#     def stop(self):
#         for w in self.workers:
#             w.stop()
#         for w in self.workers:
#             w.join()
#
# manager = WorkerManager()
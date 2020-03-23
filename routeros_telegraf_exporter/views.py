""" Cornice services.
"""
import os
from queue import Queue
from threading import Thread

from cornice import Service

from .routeros_exporter import worker
from .models import Args

output_type = os.environ.get("ROUTEROS_EXPORTER_OUTPUT", "influx")
q = Queue()
metrics = Service(name='metrics', path='/metrics', description="RouterOS metrics output", content_type="text/html",
                  renderer="string" if output_type == "influx" else "json")

worker_args = Args(daemon=True, output=output_type)
qworker = Thread(target=worker, args=(worker_args, q,))
qworker.setDaemon(True)
qworker.start()


@metrics.get()
def get_metrics(request):
    """Returns JSON or string"""
    global output_type
    values = []
    params = request.params
    if params.get("output_type"):
        output_type = params.get("output_type")

    if q.empty():
        worker(worker_args, q, False)
    while not q.empty():
        values.append(q.get())
    if output_type == "influx":
        if values:
            v = []
            for x in values:
                for x2 in x:
                    v.append(x2)
            return "\n".join(v)
        else:
            return ""
    return values

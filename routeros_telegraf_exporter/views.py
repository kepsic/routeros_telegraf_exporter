""" Cornice services.
"""
import os
from queue import Queue
from threading import Thread

from cornice import Service

from .utils import format_values_to_str
from .routeros_exporter import worker
from .models import Args

output_type = os.environ.get("ROUTEROS_EXPORTER_OUTPUT", "influx")
q = Queue()
metrics = Service(name='metrics', path='/metrics', description="RouterOS metrics output", content_type="text/html",
                  renderer="string" if output_type == "influx" else "json")

worker_args = Args(daemon=True, output_type=output_type)
qworker = Thread(target=worker, args=(worker_args, q,))
qworker.setDaemon(True)
qworker.start()


@metrics.get()
def get_metrics(request):
    """Returns JSON or influx formatted string
    Args:
    request: Pylon requests object
    """
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
            return format_values_to_str(values)
        else:
            return ""
    return values

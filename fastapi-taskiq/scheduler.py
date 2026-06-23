from broker import broker
from taskiq.schedule_sources import LabelScheduleSource
from taskiq import TaskiqScheduler

scheduler = TaskiqScheduler(
    broker,
    sources=[LabelScheduleSource()],
)

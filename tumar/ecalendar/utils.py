from dateutil.relativedelta import relativedelta

from .models import HANDLING, FEEDING


def create_mother_cow_events_next_year(obj):
    last_sluchka_date = (
        obj.events.filter(title__icontains="Случка")
        .latest("scheduled_date")
        .scheduled_date
    )
    for i in range(11, 13):
        obj.events.create(
            title="Случка коровы",
            scheduled_date=last_sluchka_date + relativedelta(months=i),
            type=HANDLING,
        )

    for i in range(7, 9):
        obj.events.create(
            title="Подготовка коровы к отелу",
            scheduled_date=last_sluchka_date + relativedelta(months=i),
            type=HANDLING,
        )

    obj.events.create(
        title="Отел коровы",
        scheduled_date=last_sluchka_date + relativedelta(months=9),
        type=HANDLING,
    )

    for i in range(9, 16):
        obj.events.create(
            title="Пастбищное содержание коров",
            scheduled_date=last_sluchka_date + relativedelta(months=i),
            type=HANDLING,
        )

    obj.events.create(
        title="Отъем телят",
        scheduled_date=last_sluchka_date + relativedelta(months=16),
        type=HANDLING,
    )

    for i in range(16, 21):
        obj.events.create(
            title="Стойловое содержание коровы",
            scheduled_date=last_sluchka_date + relativedelta(months=i),
            type=HANDLING,
        )

    for i in range(16, 18):
        obj.events.create(
            title="Выбраковка коровы (определение яловости)",
            scheduled_date=last_sluchka_date + relativedelta(months=i),
            type=HANDLING,
        )

    obj.events.create(
        title="Измерение СКТ коровы (визуальное + отправка эксперту)",
        scheduled_date=last_sluchka_date + relativedelta(months=8),
        type=FEEDING,
    )

    obj.events.create(
        title="Измерение СКТ коровы (визуальное + отправка эксперту)",
        scheduled_date=last_sluchka_date + relativedelta(months=10),
        type=FEEDING,
    )

    obj.events.create(
        title="Измерение СКТ коровы (визуальное + отправка эксперту)",
        scheduled_date=last_sluchka_date + relativedelta(months=13),
        type=FEEDING,
    )

    obj.events.create(
        title="Измерение СКТ коровы (визуальное + отправка эксперту)",
        scheduled_date=last_sluchka_date + relativedelta(months=16),
        type=FEEDING,
    )

    obj.events.create(
        title="Анализ нагрузки на пастбище",
        scheduled_date=last_sluchka_date + relativedelta(months=11),
        type=FEEDING,
    )

    for i in range(11, 14):
        obj.events.create(
            title="Определение состояния пастбищ (автоматически)",
            scheduled_date=last_sluchka_date + relativedelta(months=i),
            type=FEEDING,
        )

    print("created mother cow events for the next year")

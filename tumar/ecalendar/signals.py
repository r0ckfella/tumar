from dateutil.relativedelta import relativedelta

from django.db.models.signals import pre_save, post_save

from tumar.animals.models import BreedingStock, Calf, MALE, FEMALE
from .models import HANDLING, FEEDING


def create_male_calf_events(obj):
    if obj.birth_date:
        birth_date = obj.birth_date
        obj.mother.events.create(
            title="Отел коровы",
            scheduled_date=birth_date,
            completion_date=birth_date,
            type=HANDLING,
            completed=True,
        )
    else:
        birth_date = (
            obj.mother.events.filter(title__icontains="Отел")
            .latest("scheduled_date")
            .scheduled_date
        )
    obj.events.create(title="Рождение", scheduled_date=birth_date, type=HANDLING)

    obj.events.create(title="Биркование", scheduled_date=birth_date, type=HANDLING)

    obj.events.create(
        title="Взвешивание теленка", scheduled_date=birth_date, type=FEEDING
    )

    obj.events.create(
        title="Взвешивание теленка",
        scheduled_date=birth_date + relativedelta(months=7),
        type=FEEDING,
    )

    for i in range(7):
        obj.events.create(
            title="Выращивание на подсосе (пастбищное содержание)",
            scheduled_date=birth_date + relativedelta(months=i),
            type=HANDLING,
        )

    obj.events.create(
        title="Отъем от коровы",
        scheduled_date=birth_date + relativedelta(months=7),
        type=HANDLING,
    )

    obj.events.create(
        title="Реализация на откормплощадку",
        scheduled_date=birth_date + relativedelta(months=7),
        type=HANDLING,
    )

    obj.events.create(
        title="Сравнить прогноз и факт. эффективность теленка",
        scheduled_date=birth_date + relativedelta(months=7),
        type=HANDLING,
    )
    print("created male calf events")


def create_female_calf_events(obj):
    if obj.birth_date:
        birth_date = obj.birth_date
        obj.mother.events.create(
            title="Отел коровы",
            scheduled_date=birth_date,
            completion_date=birth_date,
            type=HANDLING,
            completed=True,
        )
    else:
        birth_date = (
            obj.mother.events.filter(title__icontains="Отел")
            .latest("scheduled_date")
            .scheduled_date
        )
    obj.events.create(title="Рождение", scheduled_date=birth_date, type=HANDLING)

    obj.events.create(title="Биркование", scheduled_date=birth_date, type=HANDLING)

    obj.events.create(
        title="Взвешивание теленка", scheduled_date=birth_date, type=FEEDING
    )

    obj.events.create(
        title="Взвешивание теленка",
        scheduled_date=birth_date + relativedelta(months=7),
        type=FEEDING,
    )

    for i in range(7):
        obj.events.create(
            title="Выращивание на подсосе (пастбищное содержание)",
            scheduled_date=birth_date + relativedelta(months=i),
            type=HANDLING,
        )

    obj.events.create(
        title="Отъем от коровы",
        scheduled_date=birth_date + relativedelta(months=7),
        type=HANDLING,
    )

    for i in range(7, 12):
        obj.events.create(
            title="Доращивание (стойловое содержание)",
            scheduled_date=birth_date + relativedelta(months=i),
            type=HANDLING,
        )

    obj.events.create(
        title="Реализация или Перевод в Маточное",
        scheduled_date=birth_date + relativedelta(months=12),
        type=HANDLING,
    )
    print("created female calf events")


def create_mother_cow_events(obj):
    for i in range(5, 7):
        obj.events.create(
            title="Случка коровы",
            scheduled_date=obj.birth_date + relativedelta(months=i),
            type=HANDLING,
        )

    for i in range(3, 10):
        obj.events.create(
            title="Пастбищное содержание коров",
            scheduled_date=obj.birth_date + relativedelta(months=i),
            type=HANDLING,
        )

    for i in range(10, 15):
        obj.events.create(
            title="Стойловое содержание коров",
            scheduled_date=obj.birth_date + relativedelta(months=i),
            type=HANDLING,
        )

    for i in range(4, 8, 3):
        obj.events.create(
            title="Измерение СКТ коровы (визуальное + отправка эксперту)",
            scheduled_date=obj.birth_date + relativedelta(months=i),
            type=FEEDING,
        )

    obj.events.create(
        title="Анализ нагрузки на пастбище",
        scheduled_date=obj.birth_date + relativedelta(months=5),
        type=FEEDING,
    )

    for i in range(5, 8):
        obj.events.create(
            title="Определение состояния пастбищ (автоматически)",
            scheduled_date=obj.birth_date + relativedelta(months=i),
            type=FEEDING,
        )
    print("created mother cow events")


def on_change_breedingstock(sender, instance: BreedingStock, **kwargs):
    if instance._state.adding is False:
        previous = BreedingStock.objects.get(id=instance.id)
        if (
            previous.birth_date is None and instance.birth_date is not None
        ):  # field will be updated
            # create_mother_cow_events(instance)
            pass


def post_save_breedingstock(sender, instance: BreedingStock, created, **kwargs):
    if created:
        if instance.birth_date is not None:  # new object will be created
            # create_mother_cow_events(instance)
            pass


def on_change_calf(sender, instance: Calf, **kwargs):
    if instance._state.adding is False:
        previous = Calf.objects.get(id=instance.id)
        if (
            previous.birth_date is None and instance.birth_date is not None
        ):  # field will be updated
            if instance.gender == MALE:
                # create_male_calf_events(instance)
                pass
            elif instance.gender == FEMALE:
                # create_female_calf_events(instance)
                pass


def post_save_calf(sender, instance: Calf, created, **kwargs):
    if created:
        if instance.birth_date is not None:  # new object will be created
            if instance.gender == MALE:
                # create_male_calf_events(instance)
                pass
            elif instance.gender == FEMALE:
                # create_female_calf_events(instance)
                pass


pre_save.connect(receiver=on_change_breedingstock, sender=BreedingStock)
post_save.connect(receiver=post_save_breedingstock, sender=BreedingStock)
pre_save.connect(receiver=on_change_calf, sender=Calf)
post_save.connect(receiver=post_save_calf, sender=Calf)

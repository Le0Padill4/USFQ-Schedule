"""Humo: el paquete se importa. No prueba comportamiento del motor."""


def test_package_imports():
    import usfq_schedule
    import usfq_schedule.domain
    import usfq_schedule.domain.scheduling

    assert usfq_schedule.__doc__

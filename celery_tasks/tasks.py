from typing import List

from celery import shared_task

from api import universities


@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='universities:get_all_universities_task')
def get_all_universities_task(self, countries: List[str]):
    data: dict = {}
    for cnt in countries:
        data.update(universities.get_all_universities_for_country(cnt))
    return data


@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='university:get_university_task')
def get_university_task(self, country: str):
    university = universities.get_all_universities_for_country(country)
    return university

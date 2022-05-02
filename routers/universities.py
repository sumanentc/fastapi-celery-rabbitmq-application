from celery import group
from fastapi import APIRouter
from starlette.responses import JSONResponse

from api import universities
from celery_tasks.tasks import get_all_universities_task, get_university_task
from config.celery_utils import get_task_info
from schemas.schemas import Country

router = APIRouter(prefix='/universities', tags=['University'], responses={404: {"description": "Not found"}})


@router.post("/")
def get_universities(country: Country) -> dict:
    """
    Return the List of universities for the countries for e.g ["turkey","india","australia"] provided
    in input in a sync way
    """
    data: dict = {}
    for cnt in country.countries:
        data.update(universities.get_all_universities_for_country(cnt))
    return data


@router.post("/async")
async def get_universities_async(country: Country):
    """
    Return the List of universities for the countries for e.g ["turkey","india","australia"] provided
    in input in a async way. It just returns the task id, which can later be used to get the result.
    """
    task = get_all_universities_task.apply_async(args=[country.countries])
    return JSONResponse({"task_id": task.id})


@router.get("/task/{task_id}")
async def get_task_status(task_id: str) -> dict:
    """
    Return the status of the submitted Task
    """
    return get_task_info(task_id)


@router.post("/parallel")
async def get_universities_parallel(country: Country) -> dict:
    """
    Return the List of universities for the countries for e.g ["turkey","india","australia"] provided
    in input in a sync way. This will use Celery to perform the subtasks in a parallel manner
    """

    data: dict = {}
    tasks = []
    for cnt in country.countries:
        tasks.append(get_university_task.s(cnt))
    # create a group with all the tasks
    job = group(tasks)
    result = job.apply_async()
    ret_values = result.get(disable_sync_subtasks=False)
    for result in ret_values:
        data.update(result)
    return data

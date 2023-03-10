from datetime import datetime, timedelta
from typing import Dict

from airflow.decorators import dag, task
from airflow.models.baseoperator import chain
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.email import EmailOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.weekday import BranchDayOfWeekOperator
from airflow.utils.edgemodifier import Label
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.weekday import WeekDay

DAY_ACTIVITY_MAPPING = {
    "monday": {"is_weekday": True, "activity": "guitar lessons"},
    "tuesday": {"is_weekday": True, "activity": "studying"},
    "wednesday": {"is_weekday": True, "activity": "soccer practice"},
    "thursday": {"is_weekday": True, "activity": "contributing to Airflow"},
    "friday": {"is_weekday": True, "activity": "family dinner"},
    "saturday": {"is_weekday": False, "activity": "going to the beach"},
    "sunday": {"is_weekday": False, "activity": "sleeping in"},
}


@task(multiple_outputs=True)
def _going_to_the_beach() -> Dict:
    return {
        "subject": "Beach day!",
        "body": "It's Saturday and I'm heading to the beach.<br><br>Come join me!<br>",
    }


def _get_activity(day_name) -> str:
    activity_id = DAY_ACTIVITY_MAPPING[day_name]["activity"].replace(" ", "_")

    if DAY_ACTIVITY_MAPPING[day_name]["is_weekday"]:
        return f"weekday_activities.{activity_id}"

    return f"weekend_activities.{activity_id}"


@dag(
    start_date=datetime(2021, 6, 11),
    max_active_runs=1,
    schedule_interval="@daily",
    default_args={
        "owner": "community",
        "retries": 2,
        "retry_delay": timedelta(minutes=3),
    },
    default_view="graph",
    catchup=False,
    tags=["example"],
)
def example_dag_advanced():
    begin = DummyOperator(task_id="begin")
    end = DummyOperator(task_id="end", trigger_rule=TriggerRule.NONE_FAILED)

    check_day_of_week = BranchDayOfWeekOperator(
        task_id="check_day_of_week",
        week_day={WeekDay.SATURDAY, WeekDay.SUNDAY},
        follow_task_ids_if_true="weekend",
        follow_task_ids_if_false="weekday",
        use_task_execution_day=True,
    )

    weekend = DummyOperator(task_id="weekend")
    weekday = DummyOperator(task_id="weekday")

    day_name = "{{ dag_run.start_date.strftime('%A').lower() }}"

    with TaskGroup("weekday_activities") as weekday_activities:
        which_weekday_activity_day = BranchPythonOperator(
            task_id="which_weekday_activity_day",
            python_callable=_get_activity,
            op_args=[day_name],
        )

        for day, day_info in DAY_ACTIVITY_MAPPING.items():
            if day_info["is_weekday"]:
                day_of_week = Label(label=day)
                activity = day_info["activity"]

                do_activity = BashOperator(
                    task_id=activity.replace(" ", "_"),
                    bash_command=f"echo It's {day.capitalize()} and I'm busy with {activity}.",
                )

                which_weekday_activity_day >> day_of_week >> do_activity

    with TaskGroup("weekend_activities") as weekend_activities:
        which_weekend_activity_day = BranchPythonOperator(
            task_id="which_weekend_activity_day",
            python_callable=_get_activity,
            op_args=[day_name],
        )

        saturday = Label(label="saturday")
        sunday = Label(label="sunday")

        sleeping_in = BashOperator(task_id="sleeping_in", bash_command="sleep $[ ( $RANDOM % 30 )  + 1 ]s")

        going_to_the_beach = _going_to_the_beach()

        inviting_friends = EmailOperator(
            task_id="inviting_friends",
            to="friends@community.com",
            subject=going_to_the_beach["subject"],
            html_content=going_to_the_beach["body"],
        )

        chain(which_weekend_activity_day, [saturday, sunday], [going_to_the_beach, sleeping_in])

    chain(begin, check_day_of_week, [weekday, weekend], [weekday_activities, weekend_activities], end)


dag = example_dag_advanced()

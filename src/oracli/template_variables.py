import logging
from datetime import datetime, time, timedelta

log = logging.getLogger(__name__)


def get_filename_ctx(step_name: str, dt: datetime) -> dict:
    """ファイル名テンプレートのバインド変数を返す"""
    return {
        "step_name": step_name,
        "datetime": dt.strftime("%Y%m%d_%H%M%S"),
        "date": dt.strftime("%Y%m%d"),
        "yyyy": dt.strftime("%Y"),
        "mm": dt.strftime("%m"),
        "dd": dt.strftime("%d"),
    }


def get_sql_ctx(dt: datetime, business_day_start: time) -> dict:
    """sqlテンプレートのバインド変数を返す"""
    boundary = timedelta(
        hours=business_day_start.hour, minutes=business_day_start.minute
    )

    work_day = (dt - boundary).date()
    work_day_from = datetime.combine(work_day, business_day_start)
    work_day_to = work_day_from + timedelta(days=1)

    month_begin = work_day.replace(day=1)

    if month_begin.month == 12:
        next_month_begin = month_begin.replace(year=month_begin.year + 1, month=1)
    else:
        next_month_begin = month_begin.replace(month=month_begin.month + 1)

    month_end = next_month_begin - timedelta(days=1)

    month_from = datetime.combine(month_begin, business_day_start)
    month_to = datetime.combine(next_month_begin, business_day_start)

    return {
        "work_day": work_day,
        "work_day_from": work_day_from,
        "work_day_to": work_day_to,
        "month_begin": month_begin,
        "month_end": month_end,
        "next_month_begin": next_month_begin,
        "month_from": month_from,
        "month_to": month_to,
    }

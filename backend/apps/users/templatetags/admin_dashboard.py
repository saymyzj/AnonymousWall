from django import template

from common.admin_panel import (
    get_admin_metrics,
    get_admin_trends,
    get_report_queue,
    get_review_queue,
    get_workbench_navigation,
    get_workbench_page_pills,
)

register = template.Library()


@register.simple_tag
def admin_dashboard_metrics():
    return get_admin_metrics()


@register.simple_tag
def admin_dashboard_trends(days=7):
    return get_admin_trends(days)


@register.simple_tag
def admin_review_queue(limit=8):
    return get_review_queue(limit)


@register.simple_tag
def admin_report_queue(limit=8):
    return get_report_queue(limit)


@register.simple_tag
def admin_workbench_navigation(active_key='dashboard'):
    metrics = get_admin_metrics()
    return get_workbench_navigation(active_key, metrics)


@register.simple_tag
def admin_workbench_page_pills():
    metrics = get_admin_metrics()
    return get_workbench_page_pills(metrics)

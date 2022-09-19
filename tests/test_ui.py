import time

from seleniumbase import BaseCase

from app import app


def test_index_page(sb):
    sb.open("http://localhost:8501")
    sb.assert_exact_text("Sandmark info", "#sandmark-info")
    sb.assert_exact_text("Latest commit", "#latest-commit")
    for each in app.apps:
        sb.assert_element(f'label:contains("{each["title"]}")')
    sb.assert_text_not_visible("Traceback:", timeout=1)


def test_sequential_benchmarks_page(sb):
    sb.open("http://localhost:8501")
    sb.click('label:contains("Sequential Benchmarks")')
    sb.click(".stSelectbox div")
    sb.click("li[role=option]:nth-child(2)")
    time.sleep(2)
    sb.wait_for_text_not_visible("Running...")
    time.sleep(2)
    sb.assert_text_not_visible("Traceback:", timeout=1)

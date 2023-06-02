import os
import shutil
import time

import pytest
from app import app
from apps.utils import ARTIFACTS_DIR, ROOT


@pytest.fixture
def create_test_data():
    if ROOT != ARTIFACTS_DIR:
        paths = [
            "sequential/turing/20220322_001002/7130374bc80ac322e8f5158255b0d1bcd20190a4/5.0.0+trunk+sequential_1.orun.summary.bench",
            "sequential/navajo/20220822_001002/c716850acaa4859048e8c041e5c7342dc675ec13/5.1.0+trunk+sequential_1.orun.summary.bench",
            "parallel/turing/20220322_015642/7130374bc80ac322e8f5158255b0d1bcd20190a4/5.0.0+trunk+parallel_1.orunchrt.summary.bench",
            "parallel/navajo/20220822_004325/c716850acaa4859048e8c041e5c7342dc675ec13/5.1.0+trunk+parallel_1.orunchrt.summary.bench",
            "perfstat/turing/20220912_015102/5cce2cc6d14cee01b0c43c9090a14d29e26bf5a7/5.1.0+trunk+perfstat_1.perfstat.summary.bench",
            "perfstat/turing/20220912_041325/head/5.1.0+trunk+gadmm+pr11307+perfstat_1.perfstat.summary.bench",
        ]
        for path in paths:
            src = os.path.join(ROOT, path)
            dst = os.path.join(ARTIFACTS_DIR, path)
            if os.path.exists(dst):
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            os.link(src, dst)

    yield

    if ROOT != ARTIFACTS_DIR:
        shutil.rmtree(ARTIFACTS_DIR)


def test_index_page(sb, create_test_data):
    url = "http://localhost:8501" if sb.data is None else sb.data
    sb.open(url)
    sb.assert_exact_text("Sandmark info", "#sandmark-info")
    sb.assert_exact_text("Latest commit", "#latest-commit")
    for each in app.apps:
        sb.assert_element(f'label:contains("{each["title"]}")')
    sb.assert_text_not_visible("Traceback:", timeout=1)


def test_sequential_benchmarks_page(sb, create_test_data):
    url = "http://localhost:8501" if sb.data is None else sb.data
    sb.open(url)
    sb.click('label:contains("Sequential - throughput")')
    sb.wait_for_text_not_visible("Running...")
    time.sleep(2)
    sb.assert_text_not_visible("Traceback:", timeout=1)


def test_parallel_benchmarks_page(sb, create_test_data):
    url = "http://localhost:8501" if sb.data is None else sb.data
    sb.open(url)
    sb.click('label:contains("Parallel - throughput")')
    sb.wait_for_text_not_visible("Running...")
    time.sleep(2)
    sb.assert_text_not_visible("Traceback:", timeout=1)


def test_perfstat_benchmarks_page(sb, create_test_data):
    url = "http://localhost:8501" if sb.data is None else sb.data
    sb.open(url)
    sb.click('label:contains("Perfstat Output")')
    sb.wait_for_text_not_visible("Running...")
    time.sleep(2)
    sb.assert_text_not_visible("Traceback:", timeout=1)


def test_status_page(sb, create_test_data):
    url = "http://localhost:8501" if sb.data is None else sb.data
    sb.open(f"{url}/status")
    sb.wait_for_text_not_visible("Running...")
    time.sleep(2)
    sb.assert_text_not_visible("Traceback:", timeout=1)

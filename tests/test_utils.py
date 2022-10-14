from pathlib import Path

from apps.utils import format_variant, fmt_baseline, ARTIFACTS_DIR
from apps.benchstruct import BenchRun

RUN = BenchRun(
    type="sequential",
    host="turing",
    timestamp="20210608_141854",
    commit="06d5aa0bf63778de509a7eee129bb5f31508466f",
    variant="4.12.0+domains+effects_1.orun.summary.bench",
)

FORMATTED_RUN = "turing_4.12.0+domains+effects_20210608_06d5aa0"


def test_format_variant():
    path = Path(ARTIFACTS_DIR).joinpath(
        "sequential/turing/20210608_141854/06d5aa0bf63778de509a7eee129bb5f31508466f"
    )
    bench_file = path.joinpath("4.12.0+domains+effects_1.orun.summary.bench")
    assert str(bench_file) == RUN.filepath(ARTIFACTS_DIR)
    assert format_variant(RUN.filepath(ARTIFACTS_DIR)) == FORMATTED_RUN


def test_format_baseline():
    assert fmt_baseline(RUN) == FORMATTED_RUN


def test_format_baseline_variant_match():
    assert fmt_baseline(RUN) == format_variant(RUN.filepath(ARTIFACTS_DIR))

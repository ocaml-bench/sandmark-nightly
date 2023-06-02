# Tests

We have a bunch of browser-based UI tests written using [Selenium
Base](https://seleniumbase.io/), apart from a few simple Python utility
function tests.

The tests are written using Pytest and can be run using the pytest command
line.

## Test setup

To install the test requirements, use the `tests/requirements.txt` file.

```sh
pip install -r tests/requirements.txt
```

## Running the tests

To keep the tests simple, we assume that there is a running instance of the
Nightly UI against which the UI tests are run.

Assuming you have the requirements for the app installed, you can start up the
server using:

```sh
streamlit run app/app.py --server.runOnSave true
```

The tests can be run by simply invoking `pytest` at the terminal. See the
`pytest` CLI [usage documentation](https://docs.pytest.org/en/6.2.x/usage.html)
for more options.

## Testing on CI

The nightly UI, by default, uses the latest benchmark files committed to the
repo in the visualizations.  When the "latest" benchmark files committed to the
repo are somehow broken, this would break the tests.  But, we would like to
separate the concerns and make it easy to identify failures due to broken
nightly UI (Python) code, and failures due to broken benchmark runs. In order
to do this, we use a frozen set of benchmark files for the test UI.

To run tests using this frozen set of benchmark files, we need to run the
server by setting the `USE_TEST_ARTIFACTS` environment variable.

```sh
USE_TEST_ARTIFACTS=1 streamlit run app/app.py --server.runOnSave true
```

We also run the tests by setting this environment variable:

```sh
USE_TEST_ARTIFACTS=1 pytest
```

### Catching broken benchmark files

As mentioned above, we want to separate the concerns of catching broken
benchmark files due to broken benchmark runs from the concern of broken UI
code. We use a scheduled [GitHub
Action](../.github/workflows/production-user-tests.yml) that runs the same UI
tests every day against the production deployment of the nightly UI to catch
any broken benchmark files that are committed to the repo from Sandmark runs.

## Adding new tests

UI tests can be added to the `test_ui.py`.

If new pages/apps are added, and the apps use benchmark files different from
those used by the existing apps, ensure that there are benchmark files copied
to the sanitized test artifacts directory too, when `USE_TEST_ARTIFACTS` is
set. See `tests.test_ui.maybe_copy_test_artifacts`.

import os
from pathlib import Path
from random import uniform, seed
from typing import Dict

import matplotlib
matplotlib.use('agg')
import pytest  # noqa: E402
from allensdk.test_utilities.temp_dir import temp_dir  # noqa: E402


@pytest.fixture(scope="function")
def fn_temp_dir(request):
    return temp_dir(request)


@pytest.fixture(scope="module")
def md_temp_dir(request):
    return temp_dir(request)


def pytest_collection_modifyitems(config, items):
    ''' A pytest magic function. This function is called post-collection and gives us a hook for modifying the 
    collected items.
    '''

    skip_api_endpoint_test = pytest.mark.skipif(
        'TEST_API_ENDPOINT' not in os.environ,
        reason='this test requires that an API endpoint be specified (set the TEST_API_ENDPOINT environment variable).'
    )

    skip_nightly_test = pytest.mark.skipif(
        os.getenv('TEST_COMPLETE') != 'true',
        reason='this test is either time/memory/compute expensive or it depends on resources internal to the Allen Institute. '\
            'Either way, it does\'nt run by default and must be opted into (it does run in our nightly builds).'
    )

    skip_flaky_test = pytest.mark.skipif(
        (os.getenv('TEST_COMPLETE') != 'true') and (os.getenv('TEST_FLAKY') != 'true'),
        reason='this test does not consistently pass (for instance, because it makes requests that sometimes time out).'\
            'All such tests should be fixed, but in the mean time we\'ve restricted it to run in our nightly build only '\
            'in order to reduce the prevalence of bogus test results.'
    )

    skip_prerelease_test = pytest.mark.skipif(
        os.environ.get('TEST_PRERELEASE') != 'true',
        reason='prerelease tests are only valid if external and internal data expected to align'
    )

    skip_neuron_test = pytest.mark.skipif(
        os.getenv('TEST_NEURON') != 'true',
        reason='this test depends on the NEURON simulation library. This dependency is not straghtforward to build '\
            'and install, so you must opt in to running this test'
    )

    skip_outside_bamboo_test = pytest.mark.skipif(
        os.environ.get('TEST_BAMBOO') != 'true',
        reason='this test depends on the resources only available to Bamboo agents, but are still fast.  If they are slow, mark with nightly'
    )

    for item in items:
        if 'requires_api_endpoint' in item.keywords:
            item.add_marker(skip_api_endpoint_test)

        if 'nightly' in item.keywords:
            item.add_marker(skip_nightly_test)

        if 'todo_flaky' in item.keywords:
            item.add_marker(skip_flaky_test)

        if 'prerelease' in item.keywords:
            item.add_marker(skip_prerelease_test)

        if 'requires_neuron' in item.keywords:
            item.add_marker(skip_neuron_test)

        if 'requires_bamboo' in item.keywords:
            item.add_marker(skip_outside_bamboo_test)


@pytest.fixture()
def behavior_stimuli_time_fixture(request):
    """
    Fixture that allows for parameterization of behavior_stimuli stimuli
    time data.
    """
    data_points = request.param.get("data_points", 10)
    max_time_stamp = request.param.get("max_time_stamp", 1000)
    min_time_stamp = request.param.get("min_time_stamp", 0)
    max_stimuli_duration = request.param.get("max_stimuli_duration", 100)
    min_stimuli_duration = request.param.get("min_stimuli_duration", 10)
    random_seed = request.param.get("random_seed", 0)

    fixture_params = {
        'data_points': data_points,
        'max_time_stamp': max_time_stamp,
        'min_time_stamp': min_time_stamp,
        'max_stimuli_duration': max_stimuli_duration,
        'min_stimuli_duration': min_stimuli_duration,
        'random_seed': random_seed
    }

    seed(random_seed)
    time_stamp_zero = uniform((min_time_stamp+min_stimuli_duration),
                              (min_time_stamp+max_stimuli_duration))
    time_stamps = [time_stamp_zero]
    for i in range(1, data_points):
        next_stim_min = time_stamps[i-1] + min_stimuli_duration
        next_stim_max = min((time_stamps[i-1] + max_stimuli_duration),
                            max_time_stamp)
        time_stamp = uniform(next_stim_min, next_stim_max)
        time_stamps.append(time_stamp)

    return time_stamps, fixture_params


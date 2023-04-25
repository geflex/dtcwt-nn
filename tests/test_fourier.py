import dataclasses

import pytest

from widgets.fourier import *


@pytest.fixture
def model():
    return FourierModel()


@pytest.fixture
def storage():
    return Fourier()


@pytest.mark.parametrize('any_storage', [pytest.lazy_fixture(s) for s in ('model', 'storage')])
class TestFourierModel:
    def test_feature_size(self, any_storage):
        assert any_storage.feature_size

    def test_args(self, any_storage):
        assert any_storage.fs
        assert any_storage.fragment_len

    def test_as_dict(self, any_storage, model, storage):
        assert dataclasses.asdict(storage) == model.as_dict()

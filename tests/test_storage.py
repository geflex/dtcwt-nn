import pytest
from PyQt6.QtWidgets import QBoxLayout

from pyqt_framework.model import Model, Field
from pyqt_framework.widgets.simple import FloatSpinFactory, IntSpinFactory, ComboFactory, \
    CheckBoxFactory
from pyqt_framework.widgets.model_editor import ModelEditorFactory, create_form_layout, \
    create_layout


class ModelAllTypes(Model):
    # TODO: type auto inferrence
    int_field: int = Field(IntSpinFactory(val_range=(0, 300), step=1))
    float_field: float = Field(FloatSpinFactory(val_range=(0, 1), step=0.1), default=0.3)
    bool_field: bool = Field(default=False)
    combo_field: bool = Field(ComboFactory(['a', 'b']), default='a')


class ModelSuper(Model):
    model_field: ModelAllTypes = Field()


@pytest.fixture
def config():
    obj = ModelAllTypes(int_field=20)
    return obj


@pytest.fixture
def model_super(config):
    return ModelSuper(model_field=config)


class TestModel:
    def test_as_dict(self, config):
        data = config.as_dict()
        assert len(data) == len(config.__data__) == len(config.__fields__)

    def test_generate_model_widget(self, model_super, qtbot):
        layout = create_layout(model_super)
        assert isinstance(layout, QBoxLayout)

    def test_notify(self, config):
        new_values = []
        config.changed_connect('int_field', new_values.append)
        config.int_field = 50
        assert len(new_values) == 1


def test_generate_form_layout(config, qtbot):
    layout = create_form_layout(config)
    assert layout.count() == 8  # with labels


def test_generate_widget(config, qtbot):
    pass

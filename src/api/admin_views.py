from flask_admin.contrib.sqla import ModelView
from wtforms import validators
from flask_admin.form import ImageUploadField
import os
from flask_admin import Admin
from .models2 import db, User, VehicleBrand, VehicleCategory, VehicleColor, VehicleModel
from wtforms.fields import SelectField


class VehicleBrandAdmin(ModelView):
    column_list = ['id', 'name']
    form_columns = ['name']
    can_view_details = True
    can_create = True
    can_edit = True
    can_delete = True

    def on_model_change(self, form, model, is_created):
        if not model.name or model.name.strip() == "":
            raise ValueError("El nombre no puede estar vacío")


class VehicleCategoryAdmin(ModelView):
    column_list = ['id', 'img', 'name', 'rate', 'min_rate', 'airport_min_rate']
    form_columns = ['img', 'name', 'rate', 'min_rate', 'airport_min_rate']
    column_labels = {
        'name': 'Nombre',
        'rate': 'Tasa/Km',
        'min_rate': 'Tasa mínima',
        'airport_min_rate': 'Tasa mínima (aeropuerto)',
    }
    can_view_details = True

    # Validar campos con WTForms validators
    form_args = {
        'name': {
            'validators': [validators.DataRequired(), validators.Length(max=255)]
        },
        'rate': {
            'validators': [validators.DataRequired()]
        }
    }

    # Para manejar subida de imagen (opcional)
    form_overrides = {
        'img': ImageUploadField
    }

    form_extra_fields = {
        'img': ImageUploadField(
            'Image',
            base_path=os.path.join(
                os.path.dirname(__file__), 'static/uploads'),
            relative_path='uploads/',
            thumbnail_size=(100, 100, True)
        )
    }

    def on_model_change(self, form, model, is_created):
        if not model.name or model.name.strip() == "":
            raise ValueError("El nombre no puede estar vacío")


class VehicleColorAdmin(ModelView):
    column_list = ['id', 'name', 'hex']
    form_columns = ['name', 'hex']
    column_labels = {
        'name': 'Nombre',
        'hex': 'Código Hex',
    }

    column_formatters = {
        'hex': lambda v, c, m, p: Markup(
            f"<div style='width:30px; height:20px; background-color:{m.hex}; border:1px solid #ccc'></div> {m.hex}"
        )
    }

    form_args = {
        'hex': {
            'label': 'Código Hex',
            'validators': [],
            'default': '#000000'
        }
    }

    def on_model_change(self, form, model, is_created):
        if not model.name.strip():
            raise ValueError("El nombre no puede estar vacío")
        if not model.hex.startswith("#") or len(model.hex) != 7:
            raise ValueError(
                "El código hex debe comenzar con # y tener 6 caracteres hexadecimales")


class VehicleModelAdmin(ModelView):
    column_list = ['id', 'name', 'brand']
    form_columns = ['name', 'brand']

    column_labels = {
        'name': 'Nombre',
        'brand': 'Marca',
    }

    form_args = {
        'name': {'label': 'Nombre'},
        'brand': {'label': 'Marca'},
    }

    column_searchable_list = ['name']
    column_filters = ['brand.name']


class VehicleAdmin(ModelView):
    column_list = ['model', 'model.brand', 'color', 'category', 'plate']
    column_labels = {
        'model': 'Modelo',
        'model.brand': 'Marca',
        'color': 'Color',
        'category': 'Categoría',
        'plate': 'Matrícula',
    }

    form_columns = ['model', 'color', 'category', 'plate']

    form_args = {
        'model': {'label': 'Modelo'},
        'color': {'label': 'Color'},
        'category': {'label': 'Categoría'},
        'plate': {'label': 'Matrícula'},
    }

    column_filters = ['model.brand.name', 'color.name', 'category.name']
    column_searchable_list = ['plate']

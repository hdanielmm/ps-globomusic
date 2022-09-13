from flask import Blueprint, flash, render_template, redirect, url_for, current_app
from flask.views import View, MethodView
from app.models import Album, Tour, User
from app.album.forms import UpdateAlbumForm
from app.tour.forms import UpdateTourForm
from app import db
from flask_login import login_required, current_user
from functools import wraps
from flask_babel import _


def admin_required(f):
    @wraps(f)
    def _admin_required(*args, **kwargs):
        if not current_user.is_admin:
            flash(_("You need to be an administrator to access this page"), "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return _admin_required


admin = Blueprint("admin", __name__, template_folder="templates")


class TableView(View):
    decorators = [login_required, admin_required]

    def __init__(self, model, edit_allowed=False):
        self.model = model
        self.edit_allowed = edit_allowed
        self.columns = self.model.__mapper__.columns.keys()
        super(TableView, self).__init__()

    def dispatch_request(self):
        return render_template(
            "resource_table.html",
            instances=self.model.query.all(),
            columns=self.columns,
            resource_name=self.model.__name__.lower(),
            edit_allowed=self.edit_allowed,
        )


class ModifyResourceView(MethodView):
    decorators = [login_required, admin_required]

    def __init__(self, model, edit_form):
        self.model = model
        self.edit_form = edit_form
        self.columns = self.model.__mapper__.columns.keys()
        self.resource_name = self.model.__name__.lower()
        super(ModifyResourceView, self).__init__()

    def get(self, resource_id):
        form = self.edit_form()
        parameters = self.get_update_parameters(form)
        model_instance = self.get_model_instance(resource_id)
        for parameter in parameters:
            form_attr = getattr(form, parameter)
            form_attr.data = getattr(model_instance, parameter)
        return render_template(
            "resource_edit.html",
            parameters=parameters,
            resource_name=self.resource_name,
            model_instance=model_instance,
            form=form,
        )

    def post(self, resource_id):
        form = self.edit_form()
        parameters = self.get_update_parameters(form)
        model_instance = self.get_model_instance(resource_id)
        if form.validate_on_submit():
            for parameter in parameters:
                form_attr = getattr(form, parameter).data
                setattr(model_instance, parameter, form_attr)
            db.session.add(model_instance)
            db.session.commit()
            return redirect(url_for(f"admin.{self.resource_name}_table"))
        return redirect(
            url_for(f"admin.{self.resource_name}", resource_id=model_instance.id)
        )

    def delete(self, resource_id):
        model_instance = self.get_model_instance(resource_id)
        db.session.delete(model_instance)
        db.session.commit()
        return ""

    def get_model_instance(self, resource_id):
        return self.model.query.filter_by(id=resource_id).first()

    def get_update_parameters(self, form_instance):
        parameter_list = list(form_instance.__dict__.keys())
        parameter_list = [
            parameter
            for parameter in parameter_list
            if parameter[0] != "_" and parameter not in ["submit", "csrf_token", "meta"]
        ]
        return parameter_list


def register_admin_resource(model, edit_form=None):
    resource_name = model.__name__.lower()
    view_func = ModifyResourceView.as_view(
        f"{resource_name}", model=model, edit_form=edit_form
    )
    edit_allowed = True
    view_methods = ["GET", "POST", "DELETE"]
    if edit_form is None:
        edit_allowed = False
        view_methods = ["DELETE"]

    admin.add_url_rule(
        f"/{resource_name}/",
        view_func=TableView.as_view(
            f"{resource_name}_table", model=model, edit_allowed=edit_allowed
        ),
    )
    admin.add_url_rule(
        f"/{resource_name}/<int:resource_id>", view_func=view_func, methods=view_methods
    )


register_admin_resource(model=Album, edit_form=UpdateAlbumForm)
register_admin_resource(model=Tour, edit_form=UpdateTourForm)
register_admin_resource(model=User)

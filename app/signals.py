from flask.signals import Namespace
from flask import template_rendered

custom_namespace = Namespace()
admin_deleted = custom_namespace.signal("admin_deleted")

def log_template_renders(sender, template, context, **extra):
    print("Rendering template {}".format(
        template.name or "template string"
    ))
    print("with context: {}".format(str(context)))

def log_admin_deletion(senderm, a_name, r_name, r_id, **kw):
    print("{} with id {} was deleted by {}". format(
        r_name.capitalize(),
        str(r_id),
        a_name
    ))

def register_signals(app):
    admin_deleted.connect(log_admin_deletion, app)
    template_rendered.connect(log_template_renders, app)
from flask import render_template

# 404 error handler
def page_not_found(e):
    return render_template("errors/404.html")

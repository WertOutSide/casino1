from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.flask_helper import render_template
from models import db, User, Item, Inventory

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/")
@login_required
def profile():
    user_inventory = Inventory.query.filter_by(user_id=current_user.id).all()
    return render_template("profile.html", user_inventory=user_inventory, username=current_user.name)

@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.name = request.form.get("name", current_user.name)

        db.session.commit()
        flash("Профиль успешно обновлен!", "success")
        return redirect(url_for("profile.profile"))
    return render_template("edit_profile.html")

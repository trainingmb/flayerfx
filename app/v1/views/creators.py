#!/usr/bin/python3
"""
API Base for Creator based actions
"""
from app.v1.views import app_views, jsonify, abort, redirect,request, render_template, url_for
from app.v1.views import BaseCreatorForm
from models import storage
from models.creator import Creator
from models.creation import Creation


@app_views.route('/creators', methods=['GET'], strict_slashes=False)
def all_creators():
    """
    Returns a list of all creators
    """
    creators = [i.to_dict() for i in storage.all(Creator).values()]
    return render_template('user/list_creators.html', creators = creators)

@app_views.route('/newcreator', methods=['POST', 'GET'], strict_slashes=False)
def create_creator():
    """
    Create a New Creator
    """
    form = BaseCreatorForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            newcreator_obj = Creator(name=form.creator_name.data, reference=form.creator_reference.data, \
                                     link=form.creator_link.data)
            newcreator_obj.save()
            return redirect(url_for('app_views.rud_creator', creator_id=newcreator_obj.id))
    return render_template('user/create_creator.html', form=form)

@app_views.route('/creators/<creator_id>', methods=['POST', 'GET', 'DELETE'])
def rud_creator(creator_id):
    """
    Get/Modify/Delete creator with id <creator_id>
    if present else returns raises error 404
    """
    creator_obj = storage.get(Creator, creator_id)
    form = BaseCreatorForm()
    if creator_obj is None:
        abort(404, "Creator not Found")
    if '_method' in request.form.keys() and request.form['_method'] == 'DELETE':
        creator_obj.delete()
        storage.save()
        return redirect(url_for('app_views.all_creators'))
    if request.method == 'POST':
        if form.validate_on_submit():
            creator_obj.name = form.creator_name.data
            creator_obj.reference = form.creator_reference.data
            creator_obj.link = form.creator_link.data
            creator_obj.save()
    form.creator_name.data = creator_obj.name
    form.creator_reference.data = creator_obj.reference
    form.creator_link.data = creator_obj.link
    form.submit.label.text = "Save Changes"
    return render_template('user/creator_view.html', creator=creator_obj, creations=creator_obj.creations, form=form)

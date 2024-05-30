#!/usr/bin/python3
"""
API Base for Creations based actions
"""
from app.v1.views import app_views, jsonify, abort, redirect,request, render_template, url_for
from app.v1.views import BaseCreationForm
from models import storage
from models.creator import Creator
from models.creation import Creation
from models.post import Post

@app_views.route('/creations', methods=['GET'], strict_slashes=False)
def all_creations():
    """
    Returns a list of all creations
    """
    creations = [i.to_dict() for i in storage.all(Creation).values()]
    return render_template('user/list_creations.html', creations = creations)

@app_views.route('/creators/<creator_id>/newcreation', methods=['POST', 'GET'], strict_slashes=False)
def create_creation(creator_id):
    """
    Create a New Creation
    """
    creator_obj = storage.get(Creator, creator_id)
    if creator_obj is None:
        abort(404, "Creator not Found")
    form = BaseCreationForm()
    form.creation_creators.choices = [(creator_obj.id,creator_obj.name)]
    form.creation_creators.data = creator_obj.id
    if request.method == 'POST':
        if form.validate_on_submit():
            newcreation_obj = Creation(creator_id=creator_id, name=form.creation_name.data, \
                                       regexfilter=form.creation_regexfilter.data)
            newcreation_obj.save()
            return redirect(url_for('app_views.rud_creation', creator_id=creator_id, creation_id=newcreation_obj.id))
    return render_template('user/create_creation.html', creator=creator_obj, form=form)

@app_views.route('/creators/<creator_id>/creations/<creation_id>', methods=['POST', 'GET', 'DELETE'])
def rud_creation(creator_id, creation_id):
    """
    Get/Modify/Delete creation with id <creation_id>
    if present else returns raises error 404
    """
    creator_obj = storage.get(Creator, creator_id)
    if creator_obj is None:
        abort(404, "Creator not Found")
    creation_obj = storage.get(Creation, creation_id)
    form = BaseCreationForm()
    choices = [(cr.id, cr.name) for cr in storage.all(Creator).values()]
    form.creation_creators.choices = choices
    if creation_obj is None or creation_obj.creator_id != creator_obj.id:
        abort(404, "Creation not Found")
    if '_method' in request.form.keys() and request.form['_method'] == 'DELETE':
        creation_obj.delete()
        storage.save()
        return redirect(url_for('app_views.all_creations'))
    if '_method' in request.form.keys() and request.form['_method'] == 'CLEAN':
        posts=[{'id':i.id, 'title':i.title, 'reference': i.reference} for i in sorted(creation_obj.posts_no_content, key=lambda i:(i.reference, i.fetched_at), reverse=True)]
        for c in range(1,len(posts)):
            print(c)
            if posts[c]['reference'] == posts[c-1]['reference']:
                print(posts[c]['reference'], posts[c]['title'])
                storage.get(Post, posts[c]['id']).delete()
        storage.save()
        return redirect(url_for('app_views.all_creations'))
    if request.method == 'POST':
        if form.validate_on_submit():
            creation_obj.name = form.creation_name.data
            creation_obj.regexfilter = form.creation_regexfilter.data
            if form.creation_creators.data != creator_obj.id and form.creation_creators.data in \
                [i[0] for i in choices]:
                    creation_obj.creator_id = form.creation_creators.data
            creation_obj.save()
    form.creation_name.data = creation_obj.name
    form.creation_regexfilter.data = creation_obj.regexfilter
    form.creation_creators.data = creation_obj.creator_id
    form.submit.label.text = "Save Changes"
    posts=[{'id':i.id, 'title':i.title, 'reference': i.reference} for i in sorted(creation_obj.posts_no_content, key=lambda i:i.reference)]
    return render_template('user/creation_view.html', creation=creation_obj, posts=posts, form=form)

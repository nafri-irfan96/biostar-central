from django.shortcuts import render
from biostar4.forum.models import Post, PostUpload
from biostar4.forum import forms, auth
from biostar4.forum.decorators import *
from biostar4.forum import search
from django.core.urlresolvers import reverse


@fill_user
def search_view(request, user):
    query = request.GET.get('q')
    if not query:
        utils.error(request, "please enter a search query")
        redirect("home")

    result, hits = search.do_search(query)
    context = dict(
        user=user,
        result=result,
        hits=hits,
    )
    return render(request, "search.html", context=context)


@fill_post
def post_details(request, user, post):
    answers = Post.objects.filter(parent=post, type=Post.ANSWER).order_by('-vote_count',
                                                                          '-creation_date')

    print(answers)

    context = dict(
        user=user,
        post=post,
        answers=answers,
    )
    return render(request, "post_details.html", context=context)

@login_required
@fill_user
def post_new(request, user, type=Post.QUESTION):
    "New post"

    if type in Post.TOP_LEVEL:
        FormClass = forms.TopLevel
        create_method = auth.new_toplevel_post
    else:
        FormClass = forms.Content
        create_method = auth.new_toplevel_post
        1/0

    # Instantiate the form class
    form = FormClass(user=user, post=None)

    if request.method == 'POST':
        form = FormClass(user, None, request.POST, request.FILES)
        if form.is_valid():
            post = create_method(user=user, data=form.cleaned_data)
            auth.set_post_files(request, user=user, post=post)
            return redirect("post_details", pid=post.id)

    context = dict(
        user=user,
        form=form,
        form_title='Create a new post',
        action=reverse("post_new")
    )

    return render(request, "post_edit.html", context=context)


@login_required
@edit_post
def post_edit(request, user, post):
    "Edit toplevel post"

    initial = dict(
        title=post.title, tag_val=post.tag_val,
        type=post.type, status=post.status,
        text=post.text,
    )

    if post.is_toplevel():
        FormClass = forms.TopLevel
        edit_method = auth.edit_toplevel_post
        form_title = "Edit post"
    else:
        FormClass = forms.Content
        edit_method = auth.edit_toplevel_post
        form_title = "Edit content"

    # Initialize form class.
    form = FormClass(user=user, post=post, initial=initial)

    if request.method == 'POST':
        form = FormClass(user, post, request.POST, request.FILES)
        if form.is_valid():

            # Update the post data.
            post = edit_method(user=user, post=post, data=form.cleaned_data)

            # Manage uploaded files.
            auth.set_post_files(request, user=user, post=post)

            return redirect("post_details", pid=post.id)

    context = dict(
        user=user,
        form=form,
        form_title=form_title,
        action=reverse("post_edit", kwargs=dict(pid=post.id))
    )

    return render(request, "post_edit.html", context=context)


@fill_user
def planet_list(request, user):
    context = dict(
        user=user,
    )
    return render(request, "planet_list.html", context=context)

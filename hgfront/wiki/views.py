from hgfront.wiki.models import Page, PageChange
from hgfront.project.models import Project
from hgfront.project.decorators import check_project_permissions
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext

import hgfront.markdown as markdown

@check_project_permissions('view_wiki')
def view_page(request, slug, page_name):
    try:
        page = Page.objects.get(pk=page_name)
    except Page.DoesNotExist:
        return render_to_response("wiki/create.html", {"project":slug, "page_name": page_name}, context_instance=RequestContext(request))
    page = Page.objects.get(name=page_name)
    project = get_object_or_404(Project, name_short=slug)
    return render_to_response("wiki/page.html", {"project":project, "page": page, "content":markdown.markdown(page.content)}, context_instance=RequestContext(request))
    
@check_project_permissions('edit_wiki')
def edit_page(request, slug, page_name):
    try:
        page = Page.objects.get(pk=page_name)
        content = page.content
    except Page.DoesNotExist:
        content = ""
    return render_to_response("wiki/edit.html", {"project":get_object_or_404(Project, name_short=slug), "page_name": page_name, "content":content}, context_instance=RequestContext(request))
    
@check_project_permissions('edit_wiki')
def save_page(request, slug, page_name):

    content = request.POST['content']

    try:
        page = Page.objects.get(pk=page_name)
        page.content = content
    except Page.DoesNotExist:
        page = Page(name=page_name, content=content)
    page.save()
    if request.POST['change']:
        changeset = PageChange(page_id=page, change_message = request.POST['change'])
        changeset.save()
    
    return HttpResponseRedirect("/hgfront/projects/" + slug + "/wiki/" + page_name + "/")
    
@check_project_permissions('view_wiki')
def view_changes(request, slug, page_name):
    project = get_object_or_404(Project, name_short=slug)
    page = Page.objects.get(name=page_name)
    return render_to_response("wiki/changes.html", {"project":project, "page":page, "changesets": page.changesets()}, context_instance=RequestContext(request))

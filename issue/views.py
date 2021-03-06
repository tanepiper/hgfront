# General Libraries
import datetime
# Django Libraries
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.core.paginator import Paginator as ObjectPaginator, InvalidPage
from django.core.urlresolvers import reverse
from django.template import RequestContext
# Project Libraries
from issue.models import *
from issue.forms import IssueCreateForm, IssueEditForm
from project.models import Project
from project.decorators import check_project_permissions

@check_project_permissions('view_issues')
def issue_list(request, slug):
    """Returns a list of isses that belong to the project identified by `slug`
    Also, this accepts querystring variables:

    `page` - which page we want to view
    
    `completed` - do we want to see completed or uncompleted issues. A value
    of `yes` means we want it to show the completed ones, anything else matches
    uncompleted issues

    Apart from these two querystring variables, it also accepts filter variables
    that act just as if you gave them as keyword arguments for the filter function.
    So an example querystring for this view might look like

    ?page=1&issue_sev__slug=minor&issue_type__slug=bug&completed=no
    """
    
    #read the page variable in the querystring to determine which page we are at
    page = request.GET['page'] if request.GET.has_key('page') else 1
    try:
        page = int(page)-1
    except ValueError:
        page = 0

    project = get_object_or_404(Project.projects.select_related(), project_id__exact = slug)
    issues = project.issue_set.select_related()

    #check if we're filtering the issues by completed and if we are, filter the selection
    if request.GET.has_key('completed'):
        issues = issues.filter(finished_date__isnull = False if request.GET['completed']=='yes' else True)

    #modify the querydict so it doesn't have completed and page in it
    GET_copy = request.GET.copy()
    if GET_copy.has_key('completed'):
        del GET_copy['completed']
    if GET_copy.has_key('page'):
        del GET_copy['page']

    #filter the issues by what's left
    issues = issues.filter(**dict([(str(key),str(value)) for key,value in GET_copy.items()]))

    #initialize the pagination
    paginator = ObjectPaginator(issues, Issue.issue_options.issues_per_page)
    try:
        issues = paginator.get_page(page)
    except InvalidPage:
        issues = []

    #generate the list of pages for the template
    pages = []
    if len(paginator.page_range) > 1:
        for page_number in paginator.page_range:
            new_query_dict = request.GET.copy()
            new_query_dict['page'] = page_number
            pages.append((page_number, new_query_dict.urlencode()))
    
    if request.is_ajax():
        template = 'issue/issue_list_ajax.html'
    else:
        template = 'issue/issue_list.html'
    
    return render_to_response(template,
        {
            'project':project,
            'issue_list':issues,
            'permissions':project.get_permissions(request.user),
            'pages':pages,
            'current_page':page+1
        }, context_instance=RequestContext(request)
    )
    #TODO: Implement advanced filtering in the sidebar (kind of like the filtering the django admin has)

@check_project_permissions('view_issues')
def issue_detail(request, slug, issue_id):
    """Returns the details of the issue identified by `issue_id`"""
    project = get_object_or_404(Project.projects.select_related(), project_id__exact = slug)
    issue = get_object_or_404(Issue.objects.select_related(), id = issue_id)
    
    if request.is_ajax():
        template = 'issue/issue_detail_ajax.html'
    else:
        template = 'issue/issue_detail.html'
    
    return render_to_response(template,
        {
            'project':project,
            'issue':issue,
            'permissions':project.get_permissions(request.user),
        }, context_instance=RequestContext(request)
    )

@check_project_permissions('add_issues')
def issue_create(request, slug):
    """
    This view displays a form based on a new issue
    """
    project = get_object_or_404(Project.projects.select_related(), project_id__exact=slug)
    if request.method == "POST":
        form = IssueCreateForm(request.POST)
        if form.is_valid():
            default_status = IssueStatus.objects.order_by('id')[0]
            issue = form.save(commit=False)
            # Let's set the values that we don't get explicitly from the form
            issue.project = project
            issue.pub_date = datetime.datetime.now()
            issue.user_posted = request.user
            issue.issue_status = default_status
            issue.save()
            # Let's send a message of success to the user if the user isn't anonymous
            if request.user.is_authenticated():
                request.user.message_set.create(message="The issue has been added. Let's hope someone solves it soon!")
            return HttpResponseRedirect(issue.get_absolute_url())
    else:
        form = IssueCreateForm()
        
    if request.is_ajax():
        template = 'issue/issue_create_ajax.html'
    else:
        template = 'issue/issue_create.html'
    
    return render_to_response(template, 
        {
            'form':form, 
            'project':project, 
            'permissions':project.get_permissions(request.user)
        }, context_instance=RequestContext(request)
    )

@check_project_permissions('edit_issues')
def issue_edit(request, slug, issue_id):
    project = get_object_or_404(Project.projects.select_related(), project_id__exact=slug)
    issue = get_object_or_404(project.issue_set.select_related(), id=issue_id)
    if request.method == "POST":
        #this view is called by post either when editing an issue or when toggling its completed state
        #so here we check what we're doing
        if request.POST.has_key('toggling_completed'):
            if issue.finished_date is None:
                issue.finished_date = datetime.datetime.now()
                issue.save()
                request.user.message_set.create(message='The issue has been marked as completed!')
            else:
                issue.finished_date = None
                issue.save()
                request.user.message_set.create(message='The issue has been reopened!')
            return HttpResponseRedirect(issue.get_absolute_url())
        else:
            form = IssueEditForm(request.POST)
            if form.is_valid():
                new_issue = form.save(commit=False)
                new_issue.project = project
                new_issue.user_posted = issue.user_posted
                new_issue.pub_date = issue.pub_date
                new_issue.id = issue.id
                new_issue.save()
                form.save_m2m()
                request.user.message_set.create(message='The issue has been edited!')
                return HttpResponseRedirect(new_issue.get_absolute_url())
    else:
        form = IssueEditForm(instance=issue)
        
    if request.is_ajax():
        template = 'issue/issue_edit_ajax.html'
    else:
        template = 'issue/issue_edit.html'
    return render_to_response(template,
        {
            'form':form,
            'issue':issue,
            'project':project,
            'permissions':project.get_permissions(request.user)
        }, context_instance=RequestContext(request)
    )

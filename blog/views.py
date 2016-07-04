from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from django.contrib import messages

from allauth.account.decorators import login_required

from .models import Post, Comment
from .forms import PostForm, CommentForm

import logging

logger = logging.getLogger(__name__)


# Create your views here.
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    context = {
        'posts': posts,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    context = {
        'post': post,
    }
    return render(request, 'blog/post_detail.html', context)


@login_required
def post_new(request):
    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        # post.published_date = timezone.now()
        post.save()
        messages.success(request, "Successfully Created")
        return redirect('post_detail', pk=post.pk)
    else:
        messages.error(request, "Not Successfully Created")

    context = {
        'form': form,
    }

    return render(request, 'blog/post_form.html', context)


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        # post.published_date = timezone.now()
        post.save()
        messages.success(request, "Post Saved")
        return redirect('post_detail', pk=post.pk)

    context = {
        'title': post.title,
        'instance': post,
        'form': form,
    }

    return render(request, 'blog/post_form.html', context)


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    context = {
        'posts': posts,
    }
    return render(request, 'blog/post_draft_list.html', context)


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user.is_superuser and post.published_date is None:
        post.publish()
        messages.success(request, "Post published")
    return redirect(post_list)


@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user or request.user.is_superuser:
        post.delete()
        messages.success(request, "Post removed.")
    return redirect(post_list)


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        messages.success(request, "Comment is added")
        messages.success(request, "Thank you for the comment")
        return redirect(post_detail, pk=post.pk)

    context = {
        'form': form,
    }

    return render(request, 'blog/add_comment_to_post.html', context)


def post_comment_draft_list(request):
    posts = Post.objects.order_by('-created_date')
    # comments = Comment.objects.filter(published_date__isnull=True).order_by('created_date')
    context = {
        'posts': posts,
    }
    return render(request, 'blog/post_comment_draft_list.html', context)


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user.is_superuser or comment.post.author == request.user:
        comment.approve()
        messages.success(request, "Comment approved")
    return redirect(post_detail, pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    if comment.author == request.user or request.user.is_superuser or comment.post.author == request.user:
        comment.delete()
        messages.success(request, "Comment removed")
    return redirect(post_detail(), pk=post_pk)

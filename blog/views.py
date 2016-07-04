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
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES or None)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.published_date = timezone.now()
            post.save()
            messages.success(request, "Successfully Created")
            return redirect('post_detail', pk=post.pk)
        else:
            messages.error(request, "Not Successfully Created")
    else:
        form = PostForm()

    return render(request, 'blog/post_form.html', {'form': form})


@login_required
def post_edit(request, pk):
    instance = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES or None, instance=instance)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            # post.published_date = timezone.now()
            instance.save()
            messages.success(request, "Post Saved")
            return redirect('post_detail', pk=instance.pk)
    else:
        form = PostForm(request.POST, instance=instance)

    return render(request, 'blog/post_form.html', {'form': form})


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user.is_superuser and post.published_date is None:
        post.publish()
        messages.success(request, "Post published")
    return redirect('blog.views.post_list')


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
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.success(request, "Comment is added")
            messages.success(request, "Thank you for the comment")
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})


def post_comment_draft_list(request):
    posts = Post.objects.order_by('-created_date')
    # comments = Comment.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_comment_draft_list.html', {'posts': posts})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user.is_superuser or comment.post.author == request.user:
        comment.approve()
        messages.success(request, "Comment approved")
    return redirect('blog.views.post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    if comment.author == request.user or request.user.is_superuser or comment.post.author == request.user:
        comment.delete()
        messages.success(request, "Comment removed")
    return redirect('blog.views.post_detail', pk=post_pk)

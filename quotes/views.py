from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Q
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from .models import Quote, Vote, Source
from .forms import QuoteForm

@require_http_methods(["GET", "POST"])
@csrf_protect
def add_quote_view(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Цитата успешно добавлена!")
            return redirect("quotes:random")
    else:
        form = QuoteForm()

    return render(request, "quotes/add_quote_html", {"form": form})


def search_view(request):
    query = request.GET.get('q', '')
    quote_list = Quote.objects.active().order_by('-created_at')

    if query:
        quote_list = quote_list.filter(
            Q(text__icontains=query) | Q(source__name__icontains=query)
        ).distinct()

    ctx = {
        'query': query,
        'quotes': quote_list,
    }
    return render(request, "quotes/quote_list.html", ctx)


def ensure_session(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


@require_http_methods(["GET", "POST"])
@csrf_protect
def add_quote_view(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Цитата успешно добавлена!")
            return redirect("quotes:random")
    else:
        form = QuoteForm()

    return render(request, "quotes/add_quote.html", {"form": form})

@require_http_methods(["GET"])
def random_quote_view(request):
    last_quote_pk = request.session.get('last_quote_pk')

    q = Quote.objects.weighted_random(exclude_pk=last_quote_pk)

    if not q:
        q = Quote.objects.weighted_random()
        if not q:
            return render(request, "quotes/random_quote.html", {"quote": None})

    request.session['last_quote_pk'] = q.pk

    Quote.objects.filter(pk=q.pk).update(views=F("views") + 1)
    q.refresh_from_db(fields=["views", "likes", "dislikes"])

    return render(request, "quotes/random_quote.html", {"quote": q})

@require_http_methods(["POST"])
@csrf_protect
def vote_view(request, pk: int):
    action = request.POST.get("action")
    if action not in ("like", "dislike"):
        return HttpResponseBadRequest("invalid action")

    quote = get_object_or_404(Quote, pk=pk)
    session_key = ensure_session(request)

    value = Vote.LIKE if action == "like" else Vote.DISLIKE

    try:
        vote = Vote.objects.get(quote=quote, session_key=session_key)
        if vote.value == value:
            pass
        else:
            if value == Vote.LIKE:
                Quote.objects.filter(pk=quote.pk).update(
                    likes=F("likes") + 1, dislikes=F("dislikes") - 1
                )
            else:
                Quote.objects.filter(pk=quote.pk).update(
                    likes=F("likes") - 1, dislikes=F("dislikes") + 1
                )
            vote.value = value
            vote.save(update_fields=["value"])
    except Vote.DoesNotExist:
        Vote.objects.create(quote=quote, session_key=session_key, value=value)
        if value == Vote.LIKE:
            Quote.objects.filter(pk=quote.pk).update(likes=F("likes") + 1)
        else:
            Quote.objects.filter(pk=quote.pk).update(dislikes=F("dislikes") + 1)

    return redirect("quotes:random")

def top_view(request):

    source_kind = request.GET.get("kind")
    qs = Quote.objects.active()

    if source_kind in {Source.MOVIE, Source.BOOK}:
        qs = qs.filter(source__kind=source_kind)

    top_by_likes = qs.order_by("-likes", "-views")[:10]

    ctx = {
        "top_by_likes": top_by_likes,
        "selected_kind": source_kind or "",
    }
    return render(request, "quotes/top.html", ctx)

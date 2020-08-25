import os
import csv
import markdown

from django.shortcuts import render
from django.utils.html import html_safe


def top_view(request):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    csv_file = os.path.join(BASE_DIR, 'data/faq.csv')
    with open(csv_file, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        faqs = [dict(question=row[0], answer=row[1]) for row in reader]
    context = dict(faqs=faqs)
    return render(request, 'cababa/index.html', context=context)


def markdown_html(filename):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    agreement_text = os.path.join(BASE_DIR, 'data/{}.md'.format(filename))
    with open(agreement_text, 'r', encoding='utf8') as f:
        md_text = f.read()
    md = markdown.Markdown()
    md_text = md.convert(md_text)
    return md_text


def user_agreement_view(request):
    context = dict(md_text=markdown_html('user_agreement'))
    return render(request, 'cababa/agreement.html', context=context)


def cast_agreement_view(request):
    context = dict(md_text=markdown_html('cast_agreement'))
    return render(request, 'cababa/agreement.html', context=context)


def privacy_policy_view(request):
    context = dict(md_text=markdown_html('privacy_policy'))
    return render(request, 'cababa/agreement.html', context=context)


def cancel_policy_view(request):
    context = dict(md_text=markdown_html('cancel_policy'))
    return render(request, 'cababa/agreement.html', context=context)


def specified_commercial_transactions_act_view(request):
    context = dict(md_text=markdown_html('specified_commercial_transactions_act'))
    return render(request, 'cababa/agreement.html', context=context)

def system_view(request):
    return render(request, 'cababa/system.html')
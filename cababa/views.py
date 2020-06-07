import os
import csv

from django.shortcuts import render


def top_view(request):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    csv_file = os.path.join(BASE_DIR, 'faq.csv')
    with open(csv_file, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        faqs = [dict(question=row[0], answer=row[1]) for row in reader]
    context = dict(faqs=faqs)
    return render(request, 'cababa/index.html', context=context)

def system_view(request):
    return render(request, 'cababa/system.html')
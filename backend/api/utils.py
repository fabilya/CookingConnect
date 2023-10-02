import csv

from django.http import HttpResponse


def queryset_to_csv(queryset):

    response = HttpResponse(
        content_type="text/csv",
        headers={'Content-Disposition':
                 'attachment; filename="shopping_list.csv"'},
    )
    writer = csv.DictWriter(response, fieldnames=queryset.first().keys())
    writer.writeheader()
    writer.writerows(queryset)
    return response

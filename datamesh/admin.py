from django.contrib import admin

from .models import LogicModuleModel, Relationship, JoinRecord


for model in [LogicModuleModel, Relationship, JoinRecord]:
    admin.site.register(model)

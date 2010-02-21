from django.contrib import admin

from .models import Barcamp, Talk, TalkIdea, SideEvent, Sponsor, Sponsoring


class SponsoringInline(admin.TabularInline):
    model = Sponsoring
    extra = 1
    
class BarcampAdmin(admin.ModelAdmin):
    model = Barcamp
    inlines = (SponsoringInline,)

admin.site.register(Barcamp, BarcampAdmin)
admin.site.register(Talk)
admin.site.register(TalkIdea)
admin.site.register(SideEvent)
admin.site.register(Sponsor)
admin.site.register(Sponsoring)
from django.contrib import admin

from .models import Barcamp, Talk, TalkIdea, SideEvent, Sponsor


class SponsorInline(admin.TabularInline):
    model = Sponsor
    extra = 1
    
class BarcampAdmin(admin.ModelAdmin):
    model = Barcamp
    inlines = (SponsorInline,)

admin.site.register(Barcamp, BarcampAdmin)
admin.site.register(Talk)
admin.site.register(TalkIdea)
admin.site.register(SideEvent)
admin.site.register(Sponsor)
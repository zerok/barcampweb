from django.contrib import admin

from .models import Barcamp, Talk, TalkIdea, SideEvent, Sponsor


class SponsorInline(admin.TabularInline):
    model = Sponsor
    extra = 1
    
class BarcampAdmin(admin.ModelAdmin):
    model = Barcamp
    inlines = (SponsorInline,)

class TalkIdeaAdmin(admin.ModelAdmin):
    model = TalkIdea
    list_display = ('barcamp', 'name')

admin.site.register(Barcamp, BarcampAdmin)
admin.site.register(Talk)
admin.site.register(TalkIdea, TalkIdeaAdmin)
admin.site.register(SideEvent)
admin.site.register(Sponsor)
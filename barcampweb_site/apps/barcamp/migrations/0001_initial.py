
from south.db import db
from django.db import models
from barcampweb_site.apps.barcamp.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Talk'
        db.create_table('barcamp_talk', (
            ('event_ptr', orm['barcamp.Talk:event_ptr']),
            ('speakers', orm['barcamp.Talk:speakers']),
            ('timeslot', orm['barcamp.Talk:timeslot']),
        ))
        db.send_create_signal('barcamp', ['Talk'])
        
        # Adding model 'ResourceType'
        db.create_table('barcamp_resourcetype', (
            ('id', orm['barcamp.ResourceType:id']),
            ('name', orm['barcamp.ResourceType:name']),
            ('slug', orm['barcamp.ResourceType:slug']),
        ))
        db.send_create_signal('barcamp', ['ResourceType'])
        
        # Adding model 'TalkIdea'
        db.create_table('barcamp_talkidea', (
            ('id', orm['barcamp.TalkIdea:id']),
            ('name', orm['barcamp.TalkIdea:name']),
            ('description', orm['barcamp.TalkIdea:description']),
            ('user', orm['barcamp.TalkIdea:user']),
            ('user_name', orm['barcamp.TalkIdea:user_name']),
            ('user_email', orm['barcamp.TalkIdea:user_email']),
            ('barcamp', orm['barcamp.TalkIdea:barcamp']),
            ('created_at', orm['barcamp.TalkIdea:created_at']),
            ('modified_at', orm['barcamp.TalkIdea:modified_at']),
        ))
        db.send_create_signal('barcamp', ['TalkIdea'])
        
        # Adding model 'Barcamp'
        db.create_table('barcamp_barcamp', (
            ('id', orm['barcamp.Barcamp:id']),
            ('name', orm['barcamp.Barcamp:name']),
            ('slug', orm['barcamp.Barcamp:slug']),
            ('start', orm['barcamp.Barcamp:start']),
            ('end', orm['barcamp.Barcamp:end']),
            ('teaser', orm['barcamp.Barcamp:teaser']),
            ('description', orm['barcamp.Barcamp:description']),
            ('logo', orm['barcamp.Barcamp:logo']),
            ('twitter_tag', orm['barcamp.Barcamp:twitter_tag']),
            ('marked_for_removal_at', orm['barcamp.Barcamp:marked_for_removal_at']),
            ('removal_requested_by', orm['barcamp.Barcamp:removal_requested_by']),
            ('removal_canceled_by', orm['barcamp.Barcamp:removal_canceled_by']),
            ('available', orm['barcamp.Barcamp:available']),
        ))
        db.send_create_signal('barcamp', ['Barcamp'])
        
        # Adding model 'Resource'
        db.create_table('barcamp_resource', (
            ('id', orm['barcamp.Resource:id']),
            ('name', orm['barcamp.Resource:name']),
            ('rtype', orm['barcamp.Resource:rtype']),
            ('description', orm['barcamp.Resource:description']),
            ('url', orm['barcamp.Resource:url']),
        ))
        db.send_create_signal('barcamp', ['Resource'])
        
        # Adding model 'Event'
        db.create_table('barcamp_event', (
            ('id', orm['barcamp.Event:id']),
            ('name', orm['barcamp.Event:name']),
            ('description', orm['barcamp.Event:description']),
            ('place', orm['barcamp.Event:place']),
            ('barcamp', orm['barcamp.Event:barcamp']),
            ('start', orm['barcamp.Event:start']),
            ('end', orm['barcamp.Event:end']),
        ))
        db.send_create_signal('barcamp', ['Event'])
        
        # Adding model 'Place'
        db.create_table('barcamp_place', (
            ('id', orm['barcamp.Place:id']),
            ('name', orm['barcamp.Place:name']),
            ('location', orm['barcamp.Place:location']),
            ('address', orm['barcamp.Place:address']),
            ('barcamp', orm['barcamp.Place:barcamp']),
            ('is_sessionroom', orm['barcamp.Place:is_sessionroom']),
        ))
        db.send_create_signal('barcamp', ['Place'])
        
        # Adding model 'TimeSlot'
        db.create_table('barcamp_timeslot', (
            ('id', orm['barcamp.TimeSlot:id']),
            ('start', orm['barcamp.TimeSlot:start']),
            ('end', orm['barcamp.TimeSlot:end']),
            ('barcamp', orm['barcamp.TimeSlot:barcamp']),
            ('place', orm['barcamp.TimeSlot:place']),
        ))
        db.send_create_signal('barcamp', ['TimeSlot'])
        
        # Adding model 'SideEvent'
        db.create_table('barcamp_sideevent', (
            ('event_ptr', orm['barcamp.SideEvent:event_ptr']),
        ))
        db.send_create_signal('barcamp', ['SideEvent'])
        
        # Adding model 'Sponsor'
        db.create_table('barcamp_sponsor', (
            ('id', orm['barcamp.Sponsor:id']),
            ('name', orm['barcamp.Sponsor:name']),
            ('url', orm['barcamp.Sponsor:url']),
            ('logo', orm['barcamp.Sponsor:logo']),
            ('level', orm['barcamp.Sponsor:level']),
            ('barcamp', orm['barcamp.Sponsor:barcamp']),
        ))
        db.send_create_signal('barcamp', ['Sponsor'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Talk'
        db.delete_table('barcamp_talk')
        
        # Deleting model 'ResourceType'
        db.delete_table('barcamp_resourcetype')
        
        # Deleting model 'TalkIdea'
        db.delete_table('barcamp_talkidea')
        
        # Deleting model 'Barcamp'
        db.delete_table('barcamp_barcamp')
        
        # Deleting model 'Resource'
        db.delete_table('barcamp_resource')
        
        # Deleting model 'Event'
        db.delete_table('barcamp_event')
        
        # Deleting model 'Place'
        db.delete_table('barcamp_place')
        
        # Deleting model 'TimeSlot'
        db.delete_table('barcamp_timeslot')
        
        # Deleting model 'SideEvent'
        db.delete_table('barcamp_sideevent')
        
        # Deleting model 'Sponsor'
        db.delete_table('barcamp_sponsor')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'barcamp.barcamp': {
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'marked_for_removal_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organizers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'removal_canceled_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'canceled_barcamp_removals'", 'null': 'True', 'to': "orm['auth.User']"}),
            'removal_requested_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'requested_barcamp_removals'", 'null': 'True', 'to': "orm['auth.User']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'teaser': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'twitter_tag': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'barcamp.event': {
            'barcamp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': "orm['barcamp.Barcamp']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['barcamp.Place']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'barcamp.place': {
            'address': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'barcamp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'places'", 'to': "orm['barcamp.Barcamp']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sessionroom': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'barcamp.resource': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rtype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['barcamp.ResourceType']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'barcamp.resourcetype': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'barcamp.sideevent': {
            'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['barcamp.Event']", 'unique': 'True', 'primary_key': 'True'})
        },
        'barcamp.sponsor': {
            'barcamp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sponsors'", 'to': "orm['barcamp.Barcamp']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'barcamp.talk': {
            'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['barcamp.Event']", 'unique': 'True', 'primary_key': 'True'}),
            'resources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['barcamp.Resource']", 'null': 'True', 'blank': 'True'}),
            'speakers': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'timeslot': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'talks'", 'null': 'True', 'to': "orm['barcamp.TimeSlot']"})
        },
        'barcamp.talkidea': {
            'barcamp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['barcamp.Barcamp']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'talkideas'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'votes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'barcamp.timeslot': {
            'barcamp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'slots'", 'to': "orm['barcamp.Barcamp']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'roomslots'", 'null': 'True', 'to': "orm['barcamp.Place']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['barcamp']

# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Barcamp'
        db.create_table('barcamp_barcamp', (
            ('available', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('marked_for_removal_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('removal_canceled_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='canceled_barcamp_removals', null=True, to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('teaser', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('twitter_tag', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('removal_requested_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='requested_barcamp_removals', null=True, to=orm['auth.User'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('barcamp', ['Barcamp'])

        # Adding M2M table for field organizers on 'Barcamp'
        db.create_table('barcamp_barcamp_organizers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('barcamp', models.ForeignKey(orm['barcamp.barcamp'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('barcamp_barcamp_organizers', ['barcamp_id', 'user_id'])

        # Adding model 'Sponsor'
        db.create_table('barcamp_sponsor', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('barcamp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sponsors', to=orm['barcamp.Barcamp'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('barcamp', ['Sponsor'])

        # Adding model 'Place'
        db.create_table('barcamp_place', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('barcamp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='places', to=orm['barcamp.Barcamp'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_sessionroom', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('barcamp', ['Place'])

        # Adding model 'Event'
        db.create_table('barcamp_event', (
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['barcamp.Place'])),
            ('barcamp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events', to=orm['barcamp.Barcamp'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('barcamp', ['Event'])

        # Adding model 'Talk'
        db.create_table('barcamp_talk', (
            ('event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['barcamp.Event'], unique=True, primary_key=True)),
            ('speakers', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('timeslot', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='talks', null=True, to=orm['barcamp.TimeSlot'])),
        ))
        db.send_create_signal('barcamp', ['Talk'])

        # Adding M2M table for field resources on 'Talk'
        db.create_table('barcamp_talk_resources', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('talk', models.ForeignKey(orm['barcamp.talk'], null=False)),
            ('resource', models.ForeignKey(orm['barcamp.resource'], null=False))
        ))
        db.create_unique('barcamp_talk_resources', ['talk_id', 'resource_id'])

        # Adding model 'SideEvent'
        db.create_table('barcamp_sideevent', (
            ('event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['barcamp.Event'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('barcamp', ['SideEvent'])

        # Adding model 'TimeSlot'
        db.create_table('barcamp_timeslot', (
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('barcamp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='slots', to=orm['barcamp.Barcamp'])),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='roomslots', null=True, to=orm['barcamp.Place'])),
        ))
        db.send_create_signal('barcamp', ['TimeSlot'])

        # Adding model 'TalkIdea'
        db.create_table('barcamp_talkidea', (
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='talkideas', null=True, to=orm['auth.User'])),
            ('barcamp', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['barcamp.Barcamp'])),
            ('user_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('barcamp', ['TalkIdea'])

        # Adding M2M table for field votes on 'TalkIdea'
        db.create_table('barcamp_talkidea_votes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('talkidea', models.ForeignKey(orm['barcamp.talkidea'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('barcamp_talkidea_votes', ['talkidea_id', 'user_id'])

        # Adding model 'Resource'
        db.create_table('barcamp_resource', (
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('rtype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['barcamp.ResourceType'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('barcamp', ['Resource'])

        # Adding model 'ResourceType'
        db.create_table('barcamp_resourcetype', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('barcamp', ['ResourceType'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Barcamp'
        db.delete_table('barcamp_barcamp')

        # Removing M2M table for field organizers on 'Barcamp'
        db.delete_table('barcamp_barcamp_organizers')

        # Deleting model 'Sponsor'
        db.delete_table('barcamp_sponsor')

        # Deleting model 'Place'
        db.delete_table('barcamp_place')

        # Deleting model 'Event'
        db.delete_table('barcamp_event')

        # Deleting model 'Talk'
        db.delete_table('barcamp_talk')

        # Removing M2M table for field resources on 'Talk'
        db.delete_table('barcamp_talk_resources')

        # Deleting model 'SideEvent'
        db.delete_table('barcamp_sideevent')

        # Deleting model 'TimeSlot'
        db.delete_table('barcamp_timeslot')

        # Deleting model 'TalkIdea'
        db.delete_table('barcamp_talkidea')

        # Removing M2M table for field votes on 'TalkIdea'
        db.delete_table('barcamp_talkidea_votes')

        # Deleting model 'Resource'
        db.delete_table('barcamp_resource')

        # Deleting model 'ResourceType'
        db.delete_table('barcamp_resourcetype')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
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
            'Meta': {'object_name': 'Barcamp'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'marked_for_removal_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organizers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'organized_barcamps'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'removal_canceled_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'canceled_barcamp_removals'", 'null': 'True', 'to': "orm['auth.User']"}),
            'removal_requested_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'requested_barcamp_removals'", 'null': 'True', 'to': "orm['auth.User']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'teaser': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'twitter_tag': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'barcamp.event': {
            'Meta': {'object_name': 'Event'},
            'barcamp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': "orm['barcamp.Barcamp']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['barcamp.Place']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'barcamp.place': {
            'Meta': {'object_name': 'Place'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'barcamp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'places'", 'to': "orm['barcamp.Barcamp']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sessionroom': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'barcamp.resource': {
            'Meta': {'object_name': 'Resource'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rtype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['barcamp.ResourceType']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'barcamp.resourcetype': {
            'Meta': {'object_name': 'ResourceType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'barcamp.sideevent': {
            'Meta': {'object_name': 'SideEvent', '_ormbases': ['barcamp.Event']},
            'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['barcamp.Event']", 'unique': 'True', 'primary_key': 'True'})
        },
        'barcamp.sponsor': {
            'Meta': {'object_name': 'Sponsor'},
            'barcamp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sponsors'", 'to': "orm['barcamp.Barcamp']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'barcamp.talk': {
            'Meta': {'object_name': 'Talk', '_ormbases': ['barcamp.Event']},
            'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['barcamp.Event']", 'unique': 'True', 'primary_key': 'True'}),
            'resources': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'talks'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['barcamp.Resource']"}),
            'speakers': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'timeslot': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'talks'", 'null': 'True', 'to': "orm['barcamp.TimeSlot']"})
        },
        'barcamp.talkidea': {
            'Meta': {'object_name': 'TalkIdea'},
            'barcamp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['barcamp.Barcamp']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'talkideas'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'votes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'voted_ideas'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'barcamp.timeslot': {
            'Meta': {'object_name': 'TimeSlot'},
            'barcamp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'slots'", 'to': "orm['barcamp.Barcamp']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'roomslots'", 'null': 'True', 'to': "orm['barcamp.Place']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['barcamp']

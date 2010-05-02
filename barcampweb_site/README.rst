BarcampWeb
==========

Overview
---------

barcampweb is a project with the goal of helping people organize schedules on
a Barcamp. In its final version it should offer following features:

*   One installation should support multiple barcamps

*   Registered users should be able to create talks and assign them
    to timeslots

*   A timeslot is either associated with a fixed place or it should be generic
    (it should apply to every place marked for sessions)

*   Organizers should be able to annotate barcamps and add sponsors (with
    logos)

Installation
------------

Being a Django application you first of all have to have Python installed on
your system. What route you take from there is up to you but probably the
easiest approach would be to use virtualenv and pip.

Once you have these two installed, following commands should get you up and
running::
    
    cd barcampweb
    virtualenv --no-site-packages barcampweb.env
    source barcampweb.env/bin/activate
    pip install -r requirements.txt

The last command downloads and installs all the requirements into the
barcampweb.env. Once this is complete, just go into the barcampweb_site folder
and run ``python manage.py syncdb`` to create all the necessary tables in your
database and then start the development server using ``python manage.py
runserver``.

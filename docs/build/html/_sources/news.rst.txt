
The News Application
====================

Overview
--------

The news application is the core component of The Weekly Times.
It manages the creation, publication, review, and distribution
of news content.

The application supports three main user roles:

* **Journalists:** Create and manage their own articles and newsletters.
* **Editors:** Review, approve, edit, and manage submitted content.
* **Readers:** Browse news content and subscribe to publishers
  and journalists.

Purpose of the Application
--------------------------

The application provides a platform where journalists can submit
news content for editorial review. Editors are responsible for
reviewing and approving submitted content before publication.

Readers can access approved news content and subscribe to their
preferred publishers and journalists.

The application also provides REST API functionality for accessing
approved news content and managing application resources.

Module Reference
----------------

This section provides technical documentation for the Python modules
that implement the application's functionality.

News Package
------------

The news package contains the main components of The Weekly Times,
including its database models, application views, forms,
administrative functionality, permissions, and API implementation.


Submodules
----------

The following sections describe the individual Python modules
within the news application.

news.admin module
-----------------

This module configures the Django administration interface.
It registers the application's models and provides administrative
controls for managing news content and user-related records.

.. automodule:: news.admin
   :members:
   :show-inheritance:
   

news.api_permissions module
----------------------------

This module defines the permission classes used to control access
to the application's REST API resources.

It helps ensure that users can only perform actions permitted
by their assigned roles and access rights.

.. automodule:: news.api_permissions
   :members:
   :show-inheritance:
   

news.api_urls module
--------------------

This module defines the URL routes for the application's REST API.
It connects incoming API requests to the appropriate API views
and endpoints.

.. automodule:: news.api_urls
   :members:
   :show-inheritance:
   

news.api_views module
---------------------

This module contains the API views responsible for handling
requests involving articles, newsletters, publishers, and other
application resources.

It processes API operations and manages the responses returned
to API clients.

.. automodule:: news.api_views
   :members:
   :show-inheritance:
   

news.apps module
----------------

This module contains the Django application configuration.
It defines the NewsConfig class and handles application
initialisation tasks, including the registration of signals.

.. automodule:: news.apps
   :members:
   :show-inheritance:
   

news.forms module
-----------------

This module contains the forms used to collect and validate
user input within the application.

It supports the processing of information submitted through
the application's forms, including article and user-related
information.

.. automodule:: news.forms
   :members:
   :show-inheritance:
   

news.models module
------------------

This module defines the database models used by The Weekly Times.

These models represent the application's main data structures,
including users, articles, newsletters, publishers, and their
associated relationships.

The models provide the foundation for storing and managing
the application's news content and user information.

.. automodule:: news.models
   :members:
   :show-inheritance:
   

news.roles module
-----------------

This module manages the application's user roles and permissions.

It contains functionality for assigning and managing the
Reader, Editor, and Journalist roles and their associated
Django permissions.

.. automodule:: news.roles
   :members:
   :show-inheritance:
   

news.serializers module
-----------------------

This module contains the serializers used by the Django REST
Framework API.

Serializers convert application model data into formats suitable
for API responses and handle incoming data during API operations.

.. automodule:: news.serializers
   :members:
   :show-inheritance:
   

news.signals module
-------------------

This module contains Django signal handlers that respond to
specific application events.

It supports automated tasks associated with application events,
including the creation and configuration of user role groups.

.. automodule:: news.signals
   :members:
   :show-inheritance:
   

news.tests module
-----------------

This module contains automated tests for the news application.

These tests help verify application behaviour and check that
important functionality operates as expected.

.. automodule:: news.tests
   :members:
   :show-inheritance:
   

news.urls module
----------------

This module defines the URL patterns for the main news application.

It connects browser requests to the appropriate application views,
allowing users to access the different pages and features
of The Weekly Times.

.. automodule:: news.urls
   :members:
   :show-inheritance:
   

news.views module
-----------------

This module contains the main application views.

It handles user requests and manages the functionality associated
with displaying articles, managing journalist content,
and providing access to the application's different pages.

It also supports article creation, editing, deletion,
and other application operations.

.. automodule:: news.views
   :members:
   :show-inheritance:
   

Module Contents
---------------

The following section provides additional documentation
for the news package itself.

.. automodule:: news
   :members:
   :show-inheritance:
   

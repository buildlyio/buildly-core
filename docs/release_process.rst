.. _release_process:

Release Process
===============

Buildly Core release numbering will work following the semantic versioning as defined in the following description that
was extracted from the `Semantic Versioning 2.0.0 web page <https://semver.org/>`_.
Given a version number MAJOR.MINOR.PATCH, increment the:

1. MAJOR version when we make incompatible API changes,
2. MINOR version when we add functionality in a backwards compatible manner, and
3. PATCH version when we make backwards compatible bug fixes.

Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.

.. image:: ./_static/images/release-version.png
    :align: center
    :alt: Release versioning


Extending the description, we’re going to issue releases following this process:

- MAJOR.MINOR is the feature release version number.
- PATCH is the patch release version number, which is incremented for bugfix and security releases
- We make release candidate releases before a final feature release. These are of the form MAJOR.MINOR rc N, which means the Nth release candidate of version MAJOR.MINOR.

On GitHub, each Buildly feature release will have a branch called MAJOR.MINOR.x, so bugfix and security patches will be
created from there. It will also have a signed tag indicating its version number.

Release timeline
----------------

Feature releases (MAJOR.MINOR) will happen following the roadmap, so it will depend on the prioritization and sprints.
These releases will contain enhancements, new features, and so on.

Patch releases (MAJOR.MINOR.PATCH) will happen as needed, to security issues and/or fix bugs.

Some specific feature releases will be assigned as long-term support (LTS) releases, so they will still receive
security and data loss fixes for a granted period of time, two years.

Deprecation policy
------------------

Certain features can be marked as deprecated by a feature release and if this happens in feature release MAJOR.X, the
deprecated features will raise warnings but keep working in all MAJOR.X+n versions. Deprecated features will be removed
in the MAJOR+1.0 release for features deprecated in the last MAJOR.X+n feature releases.

For example:

- MAJOR.0
- MAJOR.1
- MAJOR.2: Mark feature A, added in MAJOR.0, as deprecated
- MAJOR.3: Feature A still available and a warning is raised
- MAJOR+1.0: Remove feature A marked as deprecated in MAJOR.2

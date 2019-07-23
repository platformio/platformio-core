Contributing
------------

To get started, <a href="https://www.clahub.com/agreements/platformio/platformio-core">sign the Contributor License Agreement</a>.

1. Fork the repository on GitHub.
2. Make a branch off of ``develop``
3. Run ``pip install tox``
4. Go to the root of project where is located ``tox.ini`` and run ``tox -e py27``
5. Activate current development environment:

   * Windows: ``.tox\py27\Scripts\activate``
   * Bash/ZSH: ``source .tox/py27/bin/activate``
   * Fish: ``source .tox/py27/bin/activate.fish``

6. Make changes to code, documentation, etc.
7. Lint source code ``tox -e lint``
8. Run the tests ``tox -e py27``
9. Build documentation ``tox -e docs`` (creates a directory _build under docs where you can find the html)
10. Commit changes to your forked repository
11. Submit a Pull Request on GitHub.

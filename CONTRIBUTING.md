Contributing
------------

To get started, <a href="https://cla-assistant.io/platformio/platformio-core">sign the Contributor License Agreement</a>.

1. Fork the repository on GitHub.
2. Clone repository `git clone --recursive https://github.com/YourGithubUsername/platformio-core.git`
3. Run `pip install tox`
4. Go to the root of project where is located `tox.ini` and run `tox -e py37`
5. Activate current development environment:

   * Windows: `.tox\py37\Scripts\activate`
   * Bash/ZSH: `source .tox/py37/bin/activate`
   * Fish: `source .tox/py37/bin/activate.fish`

6. Make changes to code, documentation, etc.
7. Lint source code `make before-commit`
8. Run the tests `make test`
9. Build documentation `tox -e docs` (creates a directory _build under docs where you can find the html)
10. Commit changes to your forked repository
11. Submit a Pull Request on GitHub.

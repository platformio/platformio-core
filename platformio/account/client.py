---
$schema: https://raw.githubusercontent.com/streetsidesoftware/cspell/main/cspell.schema.json
version: '0.2'
# Allows things like stringLength
allowCompoundWords: true

# Read files not to spell check from the git ignore
useGitignore: true

#  Language settings for C
languageSettings:
  - caseSensitive: false
    enabled: true
    languageId: c
    locale: "*"

# Add a dictionary, and the path to the word list
dictionaryDefinitions:
  - name: freertos-words
    path: '.github/.cSpellWords.txt'
    addWords: true

dictionaries:
  - freertos-words

# Paths and files to ignore
ignorePaths:
  - 'dependency'
  - 'docs'
  - 'ThirdParty'
  - 'History.txt'

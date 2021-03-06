import os
import sublime
import sublime_plugin
import sys
import threading
import urllib.request

# Ensure it works for python 2 and 3
try:
  from urllib.parse import urlencode
  from urllib.request import urlopen
except ImportError:
  from urllib import urlencode, urlopen

API_URL = "https://jsonblob.com/api/jsonBlob"

class SendToJsonBlobPromptCommand(sublime_plugin.WindowCommand):
  """Show a window to allow the user to setup the Paste options"""

  def run(self):
    self.window.show_input_panel("Paste Name:", "", self.on_done, None, None)

  def on_done(self, paste_name):
    if self.window.active_view():
      self.window.active_view().run_command("send_to_json_blob", {"paste_name": paste_name} )

class SendToJsonBlobCommand(sublime_plugin.TextCommand):

  def run(self, view, paste_name = None):
    self.settings = sublime.load_settings("SendToJsonBlob.sublime-settings")

    # These are all the syntaxes supported by PasteBin currently (http://pastebin.com/api)
    syntaxes = {
      'ActionScript.tmLanguage': 'actionscript',
      'AppleScript.tmLanguage': 'applescript',
      'ASP.tmLanguage': 'asp',
      'Bibtex.tmLanguage': 'bibtex',
      'C.tmLanguage': 'c',
      'C#.tmLanguage': 'csharp',
      'C++.tmLanguage': 'cpp',
      'Clojure.tmLanguage': 'clojure',
      'CoffeeScript.tmLanguage': 'coffeescript',
      'CSS.tmLanguage': 'css',
      'D.tmLanguage': 'd',
      'Diff.tmLanguage': 'diff',
      'DOT.tmLanguage': 'dot',
      'Erlang.tmLanguage': 'erlang',
      'Go.tmLanguage': 'go',
      'Groovy.tmLanguage': 'groovy',
      'Haskell.tmLanguage': 'haskell',
      'HTML.tmLanguage': 'html5',
      'Java.tmLanguage': 'java',
      'JavaScript.tmLanguage': 'javascript',
      'JSON.tmLanguage': 'javascript',
      'JSON Generic Array Elements.tmLanguage': 'javascript',
      'LaTeX.tmLanguage': 'latex',
      'LaTeX Beamer.tmLanguage': 'latex',
      'LaTeX Memoir.tmLanguage': 'latex',
      'Lisp.tmLanguage': 'lisp',
      'Literate Haskell.tmLanguage': 'haskell',
      'Lua.tmLanguage': 'lua',
      'Makefile.tmLanguage': 'make',
      'Matlab.tmLanguage': 'matlab',
      'Objective-C.tmLanguage': 'objc',
      'Objective-C++.tmLanguage': 'objc',
      'OCaml.tmLanguage': 'ocaml',
      'OCamllex.tmLanguage': 'ocaml',
      'OCamlyacc.tmLanguage': 'ocaml',
      'Perl.tmLanguage': 'perl',
      'PHP.tmLanguage': 'php',
      'Plain text.tmLanguage': 'text',
      'Python.tmLanguage': 'python',
      'R.tmLanguage': 'rsplus',
      'R Console.tmLanguage': 'rsplus',
      'Regular Expressions (Python).tmLanguage': 'python',
      'Ruby.tmLanguage': 'ruby',
      'Ruby Haml.tmLanguage': 'ruby',
      'Ruby on Rails.tmLanguage': 'rails',
      'Scala.tmLanguage': 'scala',
      'SCSS.tmLanguage': 'css',
      'Shell-Unix-Generic.tmLanguage': 'bash',
      'SQL.tmLanguage': 'sql',
      'SQL (Rails).tmLanguage': 'sql',
      'Tcl.tmLanguage': 'tcl',
      'TeX.tmLanguage': 'latex',
      'TeX Math.tmLanguage': 'latex',
      'Textile.tmLanguage': 'latex',
      'XML.tmLanguage': 'xml',
      'YAML.tmLanguage': 'yaml'
    }

    # Use the filename as a default paste name
    if paste_name is None:
      paste_name = self.view.file_name()

      # Check if file exists on disk
      if paste_name is not None:
        # Only use the basename (we don't care about the path)
        paste_name =  os.path.basename(paste_name)
      else:
        paste_name = "Untitled"

    # Manage the user selected text
    for region in self.view.sel():
      syntax = syntaxes.get(self.view.settings().get('syntax').split('/')[-1], 'text')

      text = self.view.substr(region)

      if not text:
        sublime.status_message('Error sending to JsonBlob: Nothing selected')
      else:
        # Use a background thread to avoid freezing the main thread
        thread = PasteBinApiCall(text)
        thread.start()

class PasteBinApiCall(threading.Thread):
  """Manages the call to JsonBlob's API.
  Used to be able to do the call in another thread."""

  def __init__(self, call_args):
    self.call_args = call_args
    threading.Thread.__init__(self)

  def run(self):
    sublime.status_message('Sending to JsonBlob...')
    req = urllib.request.Request(API_URL)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondataasbytes = self.call_args.encode('utf-8')
    response = urllib.request.urlopen(req, jsondataasbytes)
    print(response.status)
    print(response.getheader('X-jsonblob'))
    sublime.set_clipboard('https://jsonblob.com/'+response.getheader('X-jsonblob'))
    sublime.status_message('jsonBlob URL copied to clipboard: ' + response.getheader('X-jsonblob'))
    
    

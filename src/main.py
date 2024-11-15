from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import TextArea, Frame

import requests
import json


def store_url(_):
    """Store the URL """
    global stored
    if url_bar.text == 'local':
        stored = 'http://127.0.0.1:8000/products/'
    else:
        stored = url_bar.text

def post_req(_):
    """
    POST request in JSON format
    """
    try:
        data = json.loads(post_method.text)
        requests.post(stored, json=data)
    except Exception as e:
        post_method.text = str(e)

def get_res(_):
    """
    Get response from store_url and store it (write out) in the get_method section
    in json format
    """
    try:
        r = json.dumps(requests.get(stored).json(), indent=4)
    except Exception as e:
        r = str(e)
    get_method.text = r
    get_head()

def get_head():
    head_method.text = ''
    response = requests.head(stored).headers
    for k in response:
        head_method.text += f'{k}: {response[k]}\n'

# Create text areas to represent different sections
url_bar = TextArea(height=1, wrap_lines=True)
get_method = TextArea(wrap_lines=True, read_only=True, scrollbar=True)
post_method = TextArea(wrap_lines=True)
head_method = TextArea(scrollbar=True)

# Keybind window
keybinds_window = Frame(
        VSplit(
            [
                Window(content=FormattedTextControl("GET(C-g)")),
                Window(content=FormattedTextControl("POST(C-p)")),
                Window(content=FormattedTextControl("PATCH(C-P)")),
                Window(content=FormattedTextControl("PUT(C-u)")),
                Window(content=FormattedTextControl("DELETE(C-r)")),
                ],
            height=1,
            )
        )

# Define the layouts
get_layout = HSplit(
    [
        Frame(url_bar, title="Enter URL"),  # URL input area at the top
        VSplit([
            Frame(get_method, title="GET"),
            Frame(head_method, title="HEAD"),
        ]),
        keybinds_window
    ]
)

post_layout = HSplit(
    [
        Frame(url_bar, title="Enter URL"),  # URL input area at the top
        VSplit([
            Frame(post_method, title="POST"),
            Frame(head_method, title="HEAD"),
        ]),
        keybinds_window
    ]
)

# Save the current layout for easier layout swap
current_layout = get_layout

layout = Layout(container=current_layout)

kb = KeyBindings()

# Exit app on Ctrl-d
@kb.add('c-d')
def exit_(event):
    event.app.exit()

# Store the url and print get response on Enter
@kb.add('enter')
def enter(event):
    if current_layout is get_layout:
        store_url(event)
        get_res(event)
    elif current_layout is post_layout:
        store_url(event)
        post_req(event)

# Change method layout
@kb.add('c-g')
def to_get_method(event):
    global current_layout
    current_layout = get_layout
    layout.container = current_layout
    event.app.invalidate()

@kb.add('c-p')
def to_post_method(event):
    global current_layout
    current_layout = post_layout
    layout.container = current_layout
    event.app.invalidate()

# Change between URL input and method input
# No reason to swap to GET window
@kb.add('c-n')
def tab(event):
    if event.app.layout.has_focus(url_bar) and current_layout is post_layout:
        event.app.layout.focus(post_method)
    elif event.app.layout.has_focus(url_bar) and current_layout is get_layout:
        event.app.layout.focus(get_method)
    else:
        event.app.layout.focus(url_bar)

# Create and run the application
app = Application(layout=layout, key_bindings=kb, full_screen=True)
app.run()
print(post_method.text)

# Note Custom Content

Exercises `NOTE__GET_CUSTOM_CONTENT` on every surface it offers, and keeps itself current without Canvas re-rendering it.

Above the note body, in the combined view: the patient, their date of birth and sex at birth, the provider, the date of service, and how many commands the note holds.

Inside each section: how many of the note's commands belong to that section, and a button that adds one more.

## Served as pages, not inline

Every block is returned as a `url` rather than an inline `content` string, and served by `NoteContentAPI`. A block that keeps a socket open has to be a page of its own: inline content is rendered into a frame whose lifetime Canvas owns, and its socket delivered nothing. Each block carries a dot showing whether its socket is connecting, open or dropped, so a silent feed is visible on the page.

## Staying current

Canvas draws each block once. From then on the plugin keeps it live on its own: `BroadcastCounts` answers with a `Broadcast` carrying the note's section counts, and each block picks its own number out of the message.

There is no single event for a command being added. Each command type fires its own `<COMMAND>_COMMAND__POST_ORIGINATE`, and the same for delete and enter-in-error, so `sections.py` reads the 167 of them off the event enum by suffix rather than listing them. A command type added to Canvas is picked up without touching this plugin.

The channel is one per note, so a block only hears about the note it is rendered in, and `NoteContentSocket` admits signed-in staff alone. A closed socket dims the block rather than leaving a stale number looking live.

The counts travel in the message, so nothing is fetched when one arrives.

## Adding a command

The blocks are pages the plugin serves, so the button `fetch`es the plugin's own route with the staff session already on the request. The route answers with an originate effect, and Canvas inserts the command.

History, Exam and Assessment & Plan each add a command chosen for needing nothing but the note: Medical History, Vitals and Plan. Internal reports its count and offers no button, because the sandbox allows none of the commands that section gathers.

## Which commands a section holds

`sections.py` declares the mapping. Canvas decides which commands a section gathers and does not expose it, so a plugin that wants to reason about section membership has to state its own view of it.

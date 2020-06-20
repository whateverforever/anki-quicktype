from .model_chooser import ModelChooserino
from aqt.addcards import AddCards
from aqt import dialogs
from anki.hooks import addHook, remHook
from anki.lang import _
from anki.notes import Note
from anki.sound import clearAudioQueue
from aqt.deckchooser import DeckChooser
from aqt.utils import tooltip
from aqt import gui_hooks
from aqt.sound import av_player


def init_add_card(addCards):
    gui_hooks.current_note_type_did_change.remove(addCards.onModelChange)

gui_hooks.add_cards_did_init.append(init_add_card)
    
def setupChoosers(self):
    self.modelChooser = ModelChooserino(self, self.mw, self.form.modelArea, self.form.horizontalLayout)
    self.deckChooser = DeckChooser(self.mw, self.form.deckArea)

AddCards.setupChoosers = setupChoosers
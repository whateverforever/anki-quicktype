from aqt import gui_hooks
from aqt.addcards import AddCards
from aqt.deckchooser import DeckChooser

from .model_chooser import ModelChooserino


def init_add_card(addCards):
    gui_hooks.current_note_type_did_change.remove(addCards.onModelChange)


gui_hooks.add_cards_did_init.append(init_add_card)


def setupChoosers(self):
    self.modelChooser = ModelChooserino(
        self, self.mw, self.form.modelArea, self.form.horizontalLayout
    )
    self.deckChooser = DeckChooser(self.mw, self.form.deckArea)


AddCards.setupChoosers = setupChoosers

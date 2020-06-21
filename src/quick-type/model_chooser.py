# -*- coding: utf-8 -*-
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import re
from typing import Union

from anki.lang import _
from aqt import gui_hooks, mw
from aqt.modelchooser import ModelChooser
from aqt.qt import *
from aqt.utils import shortcut, showInfo, showWarning

CONFIG = mw.addonManager.getConfig(__name__)
RE_BTN = re.compile(r"\(\d+\)\s(.+)")


class ModelChooserino(ModelChooser):
    def __init__(
        self, addcards, mw, widget: QWidget, layout: QBoxLayout, label=True
    ) -> None:
        super().__init__(mw, widget, label=label)

        self.parent = addcards
        self.radioButtons = []
        self.radioButtonForName = {}

        layout.setDirection(QBoxLayout.BottomToTop)
        widget.setMinimumHeight(30)

        self.radioLayout = QHBoxLayout()

        self.addLayout(self.radioLayout)
        self.setupRadioBtns()

    def setupRadioBtns(self):
        for imodel, modelName in enumerate(CONFIG["displayedCardTypes"]):
            button = QRadioButton("({}) {}".format(imodel + 1, modelName))

            self.radioLayout.addWidget(button, alignment=Qt.AlignLeft)
            self.radioButtons.append(button)
            self.radioButtonForName[modelName] = button

            qconnect(button.clicked, self.onDeckRadioClicked)

            shortcut_text = "Ctrl+{}".format(imodel + 1)
            button.setShortcut(QKeySequence(shortcut_text))
            button.setToolTip(shortcut("Select Note Type ({})".format(shortcut_text)))

        self.updateSelectedRadioBtn()

    def onDeckRadioClicked(self):
        sender: Union[QRadioButton, QShortcut] = QObject.sender(self)
        button: QRadioButton = sender
        if isinstance(sender, QShortcut):
            key = sender.key().toString()
            radio_btn_idx = int(key.split("+")[1]) - 1
            button = self.radioButtons[radio_btn_idx]

        button.setChecked(True)
        current = self.deck.models.current()["name"]

        buttonLabel = button.text()
        modelName = RE_BTN.match(buttonLabel).group(1)
        model = self.deck.models.byName(modelName)

        if model is None:
            # then we have a note type added in the config that doesn't exist
            showWarning(
                "The note type '{}' has been set in the config, but doesn't actually exist.\n"
                "Please adapt the addon config for existing note types.".format(
                    modelName
                )
            )
            button.setChecked(False)
            self.mw.reset()
            return

        self.deck.conf["curModel"] = model["id"]
        cdeck = self.deck.decks.current()
        cdeck["mid"] = model["id"]
        self.deck.decks.save(cdeck)
        gui_hooks.current_note_type_did_change(current)
        # Let AddCards redraw the fields of this note type
        self.parent.onModelChange()
        # Let the parent refresh text on model selector button
        self.updateModels()

    def updateModels(self):
        super().updateModels()

        # If we're still in the super() constructor, this is not yet available
        if hasattr(self, "radioButtonForName"):
            self.updateSelectedRadioBtn()
            self.parent.onModelChange()
            self.parent.setAndFocusNote(self.parent.editor.note)

    def updateSelectedRadioBtn(self):
        currentModelName = self.deck.models.current()["name"]

        if currentModelName in self.radioButtonForName:
            self.radioButtonForName[currentModelName].setChecked(True)
        else:
            # TODO: No radio button for this choice. What makes sense to do here?
            pass

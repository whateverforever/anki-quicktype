# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import re

from anki.lang import _
from aqt import gui_hooks
from aqt.qt import *
from aqt.utils import shortcut, showInfo, showWarning
from aqt import mw
config = mw.addonManager.getConfig(__name__)

RE_BTN = re.compile(r"\(\d+\)\s(.+)")

class ModelChooserino(QHBoxLayout):
    def __init__(self, addcards, mw, widget: QWidget, layout: QBoxLayout, label=True) -> None:
        self.parent = addcards
        
        QHBoxLayout.__init__(self)
        self.radioButtons = []
        self.radioButtonForName = {}

        layout.setDirection(QBoxLayout.BottomToTop)
        self.widget = widget
        self.mw = mw
        self.deck = mw.col
        self.label = label
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(8)
        self.setupModels()
        gui_hooks.state_did_reset.append(self.onReset)
        self.widget.setLayout(self)  # type: ignore

    def setupModels(self):
        if self.label:
            self.modelLabel = QLabel(_("Type"))
            self.addWidget(self.modelLabel)

        for imodel, modelName in enumerate(config["displayedCardTypes"]):
            button = QRadioButton("({}) {}".format(imodel+1, modelName))
            self.addWidget(button, alignment=Qt.AlignLeft)
            self.radioButtons.append(button)
            self.radioButtonForName[modelName] = button

            qconnect(button.clicked, self.onDeckRadioClicked)

            shortcut_text = "Ctrl+{}".format(imodel + 1)
            button.setShortcut(QKeySequence(shortcut_text))
            button.setToolTip(shortcut("Select Note Type ({})".format(shortcut_text)))

        # models box
        self.models = QPushButton("...")
        self.models.setToolTip(shortcut(_("Change Note Type (Ctrl+N)")))
        s = QShortcut(QKeySequence("Ctrl+N"), self.widget, activated=self.onModelChange)
        self.models.setAutoDefault(False)
        self.addWidget(self.models, alignment=Qt.AlignRight)
        qconnect(self.models.clicked, self.onModelChange)
        a = QPushButton()
        a.setSizePolicy(QSizePolicy.Policy(QSizePolicy.ShrinkFlag), QSizePolicy.Policy(QSizePolicy.ShrinkFlag))
        # layout
        #sizePolicy = QSizePolicy(QSizePolicy.Policy(7), QSizePolicy.Policy(0))
        #self.models.setSizePolicy(sizePolicy)
        self.updateModels()

    def onDeckRadioClicked(self):
        sender: Union[QRadioButton, QShortcut] = QObject.sender(self)
        button: QRadioButton = sender
        if isinstance(sender, QShortcut):
            key = sender.key().toString()
            radio_btn_idx = int(key.split("+")[1]) - 1
            button = self.radioButtons[radio_btn_idx]

        button.setChecked(True)
        buttonLabel = button.text()
        modelName = RE_BTN.match(buttonLabel).group(1)
        current = self.deck.models.current()["name"]

        m = self.deck.models.byName(modelName)

        if m is None:
            # then we have a note type added in the config that doesn't exist
            showWarning("The note type '{}' has been set in the config, but doesn't actually exist.\n"
                        "Please adapt the config for existing note types.".format(modelName))
            button.setChecked(False)
            self.mw.reset()
            return

        self.deck.conf["curModel"] = m["id"]
        cdeck = self.deck.decks.current()
        cdeck["mid"] = m["id"]
        self.deck.decks.save(cdeck)
        gui_hooks.current_note_type_did_change(current)
        self.parent.onModelChange()
        self.parent.setAndFocusNote(self.parent.editor.note)
        self.mw.reset()

    def cleanup(self) -> None:
        gui_hooks.state_did_reset.remove(self.onReset)

    def onReset(self):
        self.updateModels()

    def show(self):
        self.widget.show()

    def hide(self):
        self.widget.hide()

    def onEdit(self):
        import aqt.models

        aqt.models.Models(self.mw, self.widget)

    def onModelChange(self) -> None:
        from aqt.studydeck import StudyDeck

        current = self.deck.models.current()["name"]
        # edit button
        edit = QPushButton(_("Manage"), clicked=self.onEdit)  # type: ignore

        def nameFunc():
            return sorted(self.deck.models.allNames())

        ret = StudyDeck(
            self.mw,
            names=nameFunc,
            accept=_("Choose"),
            title=_("Choose Note Type"),
            help="_notes",
            current=current,
            parent=self.widget,
            buttons=[edit],
            cancel=True,
            geomKey="selectModel",
        )
        if not ret.name:
            return

        m = self.deck.models.byName(ret.name)
        self.deck.conf["curModel"] = m["id"]
        cdeck = self.deck.decks.current()
        cdeck["mid"] = m["id"]
        self.deck.decks.save(cdeck)
        gui_hooks.current_note_type_did_change(current)
        self.mw.reset()

    def updateModels(self):
        currentModelName = self.deck.models.current()["name"]

        #self.models.setText(currentModelName)
        if currentModelName in self.radioButtonForName:
            self.radioButtonForName[currentModelName].setChecked(True)
        else:
            pass
            #TODO current card type not in radiobuttons

/*
 *  Copyright 2018 by Aditya Mehra <aix.m@outlook.com>
 *  Copyright 2018 Marco Martin <mart@kde.org>
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.

 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.

 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft
import QtGraphicalEffects 1.0

Item {
    id: root
    property bool compactMode: height < 600 ? 1 : 0
    property bool configOverlayOpened: false

    Component.onCompleted: {
        txtFld.forceActiveFocus()
    }

    Keys.onEscapePressed: {
        if (root.configOverlayOpened) {
            ocpConfigOverlay.close()
        }
    }

    MouseArea {
        anchors.fill: parent
        enabled: root.configOverlayOpened ? 1 : 0
        z: 3
        onClicked: {
            if (root.configOverlayOpened) {
                ocpConfigOverlay.close()
            }
        }
    }

    ItemDelegate {
        id: ocpConfigOverlay
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: Kirigami.Units.gridUnit * 2
        opacity: root.configOverlayOpened ? 1 : 0
        visible: root.configOverlayOpened ? 1 : 0
        enabled: root.configOverlayOpened ? 1 : 0
        z: 4

        background: Rectangle {
            color: Kirigami.Theme.backgroundColor
            radius: Mycroft.Units.gridUnit * 0.5
            border.width: 1
            border.color: Qt.darker(Kirigami.Theme.textColor, 1.5)
        }

        Keys.onEscapePressed: {
            if (root.configOverlayOpened) {
                ocpConfigOverlay.close()
            }
        }

        function open() {
            root.configOverlayOpened = true
        }

        function close() {
            root.configOverlayOpened = false
        }

        Behavior on opacity {
            OpacityAnimator {
                duration: Kirigami.Units.longDuration
                easing.type: Easing.InOutQuad
            }
        }

        contentItem: ColumnLayout {
            anchors.fill: parent
            anchors.margins: Mycroft.Units.gridUnit
            spacing: Mycroft.Units.gridUnit

            Item {
                id: headsOverlay
                Layout.fillWidth: true
                Layout.preferredHeight: Mycroft.Units.gridUnit * 3
                
                Label {
                    text: "Settings"                    
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: headsOverlayCloseButton.left
                    horizontalAlignment: Text.AlignLeft
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight                   
                    wrapMode: Text.WordWrap
                    color: Kirigami.Theme.textColor
                    font.pixelSize: parent.height * 0.6
                }

                Rectangle {
                    id: headsOverlayCloseButton
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    width: Mycroft.Units.gridUnit * 4
                    color: Kirigami.Theme.highlightColor
                    radius: Mycroft.Units.gridUnit * 0.5

                    Kirigami.Icon {
                        id: closeIcon
                        anchors.centerIn: parent
                        width: Mycroft.Units.gridUnit * 1.8
                        height: Mycroft.Units.gridUnit * 1.8
                        source: "window-close-symbolic"

                        ColorOverlay {
                            anchors.fill: parent
                            source: parent
                            color: Kirigami.Theme.textColor
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            ocpConfigOverlay.close()
                        }
                    }
                }
            }

            Kirigami.Separator {
                id: sepOverlay
                Layout.fillWidth: true
                Layout.preferredHeight: 1
            }

            ConfigDelegateLayoutItem {
                id: enableTimeoutConfigDelegateItem
                label: qsTr("Enable Player Timeout")
                description: qsTr("Player will be automatically hidden after ") + configSliderTimeout.value + qsTr(" seconds")

                ConfigSwitchDelegate {
                    id: timeoutConfigButton
                    checked: sessionData.app_view_timeout_enabled ? sessionData.app_view_timeout_enabled : false
                    text: timeoutConfigButton.checked ? qsTr("Enabled") : qsTr("Disabled")
                    guiEvent: "ovos.common_play.gui.enable_app_timeout"
                    guiEventData: {"enabled": timeoutConfigButton.checked}
                }
            }

            ConfigDelegateLayoutItem {
                id: setTimeoutConfigDelegateItem
                label: qsTr("Set Player Timeout")
                description: qsTr("Timeout for player to be automatically hidden")
                enabled: timeoutConfigButton.checked
                opacity: timeoutConfigButton.checked ? 1 : 0.5

                ConfigSliderDelegate {
                    id: configSliderTimeout
                    value: sessionData.app_view_timeout ? sessionData.app_view_timeout : 30
                    guiEvent: "ovos.common_play.gui.set_app_timeout"
                    guiEventData: {"timeout": configSliderTimeout.value}
                }
            }

            ConfigDelegateLayoutItem {
                id: setTimeoutModeConfigDelegateItem
                label: qsTr("Select Timeout Mode")
                description: qsTr("All: Timeout always | Pause: Timeout on pause")
                enabled: timeoutConfigButton.checked
                opacity: timeoutConfigButton.checked ? 1 : 0.5

                ConfigOptionDelegate {
                    id: configTimeoutMode
                    property string selectedMode: sessionData.app_view_timeout_mode ? sessionData.app_view_timeout_mode : "all"
                    model: ListModel {
                        id: model
                        ListElement { text: "All"; value: "all" }
                        ListElement { text: "Pause"; value: "pause" }
                    }
                    textRole: "text"
                    valueRole: "value"

                    currentIndex: 0
                    guiEvent: "ovos.common_play.gui.timeout.mode"
                    guiEventData: {"mode": model.get(currentIndex).value}

                    onSelectedModeChanged: {
                        if(selectedMode == "all") {
                            currentIndex = 0
                        } else if(selectedMode == "pause") {
                            currentIndex = 1
                        }
                    }

                    onCurrentValueChanged: {
                        Mycroft.MycroftController.sendRequest(guiEvent, guiEventData)
                    }
                }
            }

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Mycroft.Units.gridUnit * 0.5
        enabled: !root.configOverlayOpened
        opacity: !root.configOverlayOpened ? 1 : 0.5

        Item {
            id: topAreaSearchPage
            Layout.fillWidth: true
            Layout.preferredHeight: compactMode ?  Mycroft.Units.gridUnit * 0.5 : Mycroft.Units.gridUnit * 3
        }

        Item {
            id: middleAreaSearchPage
            Layout.fillWidth: true
            Layout.preferredHeight: heads.height + sep.height + txtFld.height + answerButton.height
            Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter

            Rectangle {
                id: heads
                anchors.top: parent.top
                width: Mycroft.Units.gridUnit * 20
                height: compactMode ? Mycroft.Units.gridUnit * 3 :  Mycroft.Units.gridUnit * 4
                color: Kirigami.Theme.backgroundColor
                radius: Mycroft.Units.gridUnit * 0.5
                
                Label {
                    text: "Find Something To Play"                    
                    anchors.fill: parent
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight                   
                    wrapMode: Text.WordWrap
                    color: Kirigami.Theme.textColor
                    font.pixelSize: parent.height * 0.4
                }
            }

            Button {
                id: ocpConfigurationButton
                anchors.verticalCenter: heads.verticalCenter
                anchors.left: heads.right
                anchors.leftMargin: Mycroft.Units.gridUnit * 0.5
                height: compactMode ? Mycroft.Units.gridUnit * 3.5 :  Mycroft.Units.gridUnit * 4
                width: Mycroft.Units.gridUnit * 4

                background: Rectangle {
                    id: ocpConfigurationButtonBackground
                    color: Qt.darker(Kirigami.Theme.highlightColor, 1.25)
                    radius: Mycroft.Units.gridUnit * 0.5
                }

                SequentialAnimation {
                    id: ocpConfigurationButtonAnim

                    PropertyAnimation {
                        target: ocpConfigurationButtonBackground
                        property: "color"
                        to: Qt.lighter(Kirigami.Theme.highlightColor, 1.25)
                        duration: 200
                    }

                    PropertyAnimation {
                        target: ocpConfigurationButtonBackground
                        property: "color"
                        to: Qt.darker(Kirigami.Theme.highlightColor, 1.25)
                        duration: 200
                    }
                }

                contentItem: Item {

                    Kirigami.Icon {
                        source: "configure"
                        width: parent.width * 0.8
                        height: parent.height * 0.8
                        anchors.centerIn: parent
                        color: Kirigami.Theme.textColor
                    }
                }

                onClicked: {
                    ocpConfigurationButtonAnim.restart()
                    ocpConfigOverlay.open()
                }
            }

            Item {
                id: sep
                anchors.top: heads.bottom
                width: parent.width
                height: Kirigami.Units.largeSpacing
            }

            Rectangle {
                id: txtFld
                anchors.top: sep.bottom
                width: parent.width
                height: compactMode ? Kirigami.Units.gridUnit * 3 : Kirigami.Units.gridUnit * 5
                color: "transparent"
                border.width: 2
                radius: Mycroft.Units.gridUnit * 0.5
                border.color: txtFld.activeFocus ? Kirigami.Theme.linkColor : "transparent"
                KeyNavigation.down: answerButton
                focus: true

                Keys.onReturnPressed: {
                    txtFldInternal.forceActiveFocus()
                }

                TextField {
                    id: txtFldInternal
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.gridUnit / 3
                    KeyNavigation.down: answerButton
                    placeholderText: "Search for music, podcasts, movies ..."
                    font.pixelSize: parent.height * 0.3
                    font.bold: true

                    onAccepted: {
                        triggerGuiEvent("search", { "utterance": txtFldInternal.text})
                    }
                    Keys.onReturnPressed: {
                        triggerGuiEvent("search", { "utterance": txtFldInternal.text})
                    }
                }
            }

            Button {
                id: answerButton
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: txtFld.bottom
                anchors.margins: compactMode ? Mycroft.Units.gridUnit / 2 : Mycroft.Units.gridUnit
                height: compactMode ? Mycroft.Units.gridUnit * 3 : Mycroft.Units.gridUnit * 4
                KeyNavigation.up: txtFld

                background: Rectangle {
                    id: answerButtonBackground
                    color: answerButton.activeFocus ? Kirigami.Theme.highlightColor : Qt.darker(Kirigami.Theme.highlightColor, 1.25)
                    radius: Mycroft.Units.gridUnit
                }

                SequentialAnimation {
                    id: answerButtonAnim

                    PropertyAnimation {
                        target: answerButtonBackground
                        property: "color"
                        to: Qt.lighter(Kirigami.Theme.highlightColor, 1.25)
                        duration: 200
                    }

                    PropertyAnimation {
                        target: answerButtonBackground
                        property: "color"
                        to: answerButton.activeFocus ? Kirigami.Theme.highlightColor : Qt.darker(Kirigami.Theme.highlightColor, 1.25)
                        duration: 200
                    }
                }

                contentItem: Item {
                    Kirigami.Heading {
                        anchors.centerIn: parent
                        text: "Play!"
                        level: compactMode ? 3 : 1
                    }
                }

                onClicked: {
                    triggerGuiEvent("search", { "utterance": txtFldInternal.text})
                }

                onPressed: {
                    answerButtonAnim.running = true;
                }

                Keys.onReturnPressed: {
                    clicked()
                }
            }
        }

        Item {
            id: bottomAreaSearchPage
            Layout.fillWidth: true            
            Layout.fillHeight: true
        }
    }
}

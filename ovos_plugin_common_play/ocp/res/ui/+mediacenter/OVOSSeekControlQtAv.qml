/*
 * Copyright 2019 by Aditya Mehra <aix.m@outlook.com>
 * Copyright 2019 by Marco Martin <mart@kde.org>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12 as Controls
import org.kde.kirigami 2.10 as Kirigami
import QtQuick.Templates 2.12 as Templates
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft
import QtAV 1.7

Item {
    id: seekControl
    property bool opened: false
    property int duration: 0
    property int playPosition: 0
    property int seekPosition: 0
    property bool enabled: true
    property bool seeking: false
    property var videoControl
    property string title
    property var currentState: videoService.playbackState

    readonly property var videoService: Mycroft.MediaService

    clip: true
    implicitWidth: parent.width
    implicitHeight: mainLayout.implicitHeight + Kirigami.Units.largeSpacing * 2
    opacity: opened

    function itemKeyFocus() {
        playPauseButton.forceActiveFocus()
    }

    onOpenedChanged: {
        if (opened) {
            playPauseButton.forceActiveFocus()
            hideTimer.restart();
        }
    }

    Timer {
        id: hideTimer
        interval: 5000
        onTriggered: {
            seekControl.opened = false;
            videoRoot.forceActiveFocus();
        }
    }

    Rectangle {
        width: parent.width
        height: parent.height
        property color tempColor: Qt.darker(Kirigami.Theme.backgroundColor, 2)
        color: Qt.rgba(tempColor.r, tempColor.g, tempColor.b, 0.8)
        y: opened ? 0 : parent.height

        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: Mycroft.Units.gridUnit / 4
            color: Kirigami.Theme.highlightColor
        }

        ColumnLayout {
            id: mainLayout

            anchors {
                fill: parent
                margins: Kirigami.Units.largeSpacing
            }

            RowLayout {
                id: mainLayout2
                Layout.fillHeight: true

                VideoPlayerControl {
                    id: playPauseButton
                    controlIcon: avVideo.playbackState == MediaPlayer.PlayingState ? Qt.resolvedUrl("../images/media-playback-pause.svg") : Qt.resolvedUrl("../images/media-playback-start.svg")

                    KeyNavigation.up: videoControl
                    KeyNavigation.right: prevButton
                    Keys.onReturnPressed: {
                        clicked()
                    }

                    onClicked: {
                        currentState === avVideo.playbackState == MediaPlayer.PlayingState ? videoControl.pause() : videoControl.currentState == MediaPlayer.PausedState ? videoControl.resume() : videoControl.play()
                        hideTimer.restart();
                    }
                }

                VideoPlayerControl {
                    id: prevButton
                    controlIcon: Qt.resolvedUrl("../images/media-skip-backward.svg")

                    KeyNavigation.up: videoControl
                    KeyNavigation.left: playPauseButton
                    KeyNavigation.right: nextButton
                    Keys.onReturnPressed: {
                        clicked()
                    }

                    onClicked: {
                        videoControl.previous()
                        hideTimer.restart();
                    }
                }

                VideoPlayerControl {
                    id: nextButton
                    controlIcon: Qt.resolvedUrl("../images/media-skip-forward.svg")

                    KeyNavigation.up: videoControl
                    KeyNavigation.left: prevButton
                    KeyNavigation.right: slider
                    Keys.onReturnPressed: {
                        clicked()
                    }

                    onClicked: {
                        videoControl.next()
                        hideTimer.restart();
                    }
                }

                Templates.Slider {
                    id: slider
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignVCenter
                    implicitHeight: Kirigami.Units.gridUnit
                    value: seekControl.playPosition
                    from: 0
                    to: seekControl.duration
                    z: 1000
                    property bool navSliderItem
                    property int minimumValue: 0
                    property int maximumValue: 20

                    onMoved: {
                        seekControl.seekPosition = value;
                        hideTimer.restart();
                    }

                    handle: Item {
                        x: slider.visualPosition * (parent.width - (Kirigami.Units.largeSpacing + Kirigami.Units.smallSpacing))
                        anchors.verticalCenter: parent.verticalCenter
                        height: parent.height + Mycroft.Units.gridUnit

                        Rectangle {
                            id: hand
                            anchors.verticalCenter: parent.verticalCenter
                            implicitWidth: Kirigami.Units.iconSizes.small + Kirigami.Units.smallSpacing
                            implicitHeight: parent.height / 2
                            color: slider.activeFocus ? Kirigami.Theme.highlightColor : Kirigami.Theme.backgroundColor
                            border.color: slider.activeFocus ? Kirigami.Theme.textColor : Kirigami.Theme.highlightColor
                        }
                    }

                    background: Item {
                        Rectangle {
                            id: groove
                            anchors {
                                verticalCenter: parent.verticalCenter
                                left: parent.left
                                right: parent.right
                            }
                            height: Math.round(Kirigami.Units.gridUnit/3)
                            color: Qt.lighter(Kirigami.Theme.highlightColor, 1.5)

                            Rectangle {
                                anchors {
                                    left: parent.left
                                    top: parent.top
                                    bottom: parent.bottom
                                }
                                gradient: Gradient {
                                    orientation: Gradient.Horizontal
                                    GradientStop { position: 0.0; color: Kirigami.Theme.highlightColor }
                                    GradientStop { position: 1.0; color: Qt.darker(Kirigami.Theme.highlightColor, 1.5) }
                                }
                                width: slider.position * (parent.width - slider.handle.width/2) + slider.handle.width/2
                            }
                        }

                        Controls.Label {
                            anchors {
                                left: parent.left
                                top: groove.bottom
                                topMargin: Kirigami.Units.smallSpacing
                            }
                            horizontalAlignment: Text.AlignLeft
                            verticalAlignment: Text.AlignVCenter
                            text: formatedPosition(playPosition)
                            color: Kirigami.Theme.textColor
                        }

                        Controls.Label {
                            anchors {
                                right: parent.right
                                top: groove.bottom
                                topMargin: Kirigami.Units.smallSpacing
                            }
                            horizontalAlignment: Text.AlignRight
                            verticalAlignment: Text.AlignVCenter
                            text: formatedDuration(duration)
                            color: Kirigami.Theme.textColor
                        }
                    }
                    KeyNavigation.up: videoControl
                    KeyNavigation.left: nextButton
                    KeyNavigation.right: stopButton
                    Keys.onReturnPressed: {
                        hideTimer.restart();
                        if(!navSliderItem){
                            navSliderItem = true
                        } else {
                            navSliderItem = false
                        }
                    }

                    Keys.onLeftPressed: {
                        hideTimer.restart();
                        if(navSliderItem) {
                            videoControl.seek(video.position - 5000)
                        } else {
                            nextButton.forceActiveFocus()
                        }
                    }

                    Keys.onRightPressed: {
                        hideTimer.restart();
                        if(navSliderItem) {
                            videoControl.seek(video.position + 5000)
                        } else {
                            stopButton.forceActiveFocus()
                        }
                    }
                }

                VideoPlayerControl {
                    id: stopButton
                    controlIcon: Qt.resolvedUrl("../images/media-playback-stop.svg")

                    KeyNavigation.up: videoControl
                    KeyNavigation.left: slider
                    KeyNavigation.right: exitButton
                    Keys.onReturnPressed: {
                        clicked()
                    }

                    onClicked: {
                        videoControl.stop();
                        hideTimer.restart();
                        Mycroft.MycroftController.sendRequest("ovos.common_play.home", {})
                    }
                }

                VideoPlayerControl {
                    id: exitButton
                    controlIcon: "window-close-symbolic"

                    KeyNavigation.up: videoControl
                    KeyNavigation.left: stopButton
                    Keys.onReturnPressed: {
                        clicked()
                    }
                    onClicked: {
                        videoControl.stop();
                        hideTimer.restart();
                        Mycroft.MycroftController.sendRequest("system.display.homescreen", {})
                    }
                }
            }
        }
    }

    function formatedDuration(millis){
        var minutes = Math.floor(millis / 60000);
        var seconds = ((millis % 60000) / 1000).toFixed(0);
        return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
    }

    function formatedPosition(millis){
        var minutes = Math.floor(millis / 60000);
        var seconds = ((millis % 60000) / 1000).toFixed(0);
        return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
    }
}

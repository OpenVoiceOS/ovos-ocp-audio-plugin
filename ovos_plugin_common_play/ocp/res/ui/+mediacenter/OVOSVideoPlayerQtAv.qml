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

import QtMultimedia 5.12
import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12 as Controls
import org.kde.kirigami 2.10 as Kirigami
import QtQuick.Window 2.3
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft
import "." as Local
import QtAV 1.7

Rectangle {
    id: root
    readonly property var videoService: Mycroft.MediaService
    property Component controlBar
    color: "black"

    readonly property Item controlBarItem: {
        if (controlBar) {
            return controlBar.createObject(root, {"z": 9999});
        } else {
            return null;
        }
    }

    property var videoSource
    property var videoStatus
    property var videoRepeat
    property var videoThumb
    property var videoTitle: sessionData.title
    property var videoAuthor: sessionData.artist
    property var playerMeta
    property var cpsMeta
    property bool busyIndicate: false

    //Player Button Control Actions
    property var currentState: avVideo.playbackState

    //Mediaplayer Related Properties To Be Set By Probe MediaPlayer
    property var playerDuration
    property var playerPosition

    Keys.onDownPressed: {
        controlBarItem.opened = true
        controlBarItem.itemKeyFocus()
    }

    onVideoSourceChanged: {
        root.play()
        delay(6000, function() {
            infomationBar.visible = false;
        })
    }

    function play(){
        avVideo.source = videoSource
    }

    function pause(){
        avVideo.pause()
    }

    function stop(){
        avVideo.stop()
    }

    function resume(){
        avVideo.play()
    }

    function seek(val){
        avVideo.seek(val)
    }

    function next(){
        videoService.playerNext()
    }

    function previous(){
        videoService.playerPrevious()
    }

    Connections {
        target: Window.window
        onVisibleChanged: {
            if(video.playbackState == MediaPlayer.PlayingState) {
                stop()
            }
        }
    }

    Connections {
        target: Mycroft.MediaService

        onPlayRequested: {
            videoSource = videoService.getTrack()
        }

        onStopRequested: {
            videoSource = ""
        }

        onMediaStatusChanged: {
            triggerGuiEvent("media.state", {"state": status})
            if (status == MediaPlayer.EndOfMedia) {
                pause()
            }
        }

        onMetaUpdated: {
            root.playerMeta = videoService.getPlayerMeta()

            if(root.playerMeta.hasOwnProperty("Title")) {
                root.videoTitle = root.playerMeta.Title ? root.playerMeta.Title : ""
            }

            if(root.playerMeta.hasOwnProperty("Artist")) {
                root.videoAuthor = root.playerMeta.Artist
            } else if(root.playerMeta.hasOwnProperty("ContributingArtist")) {
                root.videoAuthor = root.playerMeta.ContributingArtist
            }
        }

        onMetaReceived: {
            root.cpsMeta = videoService.getCPSMeta()
            root.videoThumb = root.cpsMeta.thumbnail
            root.videoAuthor = root.cpsMeta.artist
            root.videoTitle = root.cpsMeta.title
        }
    }


    Timer {
        id: delaytimer
    }

    function delay(delayTime, cb) {
        delaytimer.interval = delayTime;
        delaytimer.repeat = false;
        delaytimer.triggered.connect(cb);
        delaytimer.start();
    }

    controlBar: Local.OVOSSeekControlQtAv {
        id: seekControl

        anchors {
            bottom: parent.bottom
        }
        title: videoTitle
        videoControl: root
        duration: avVideo.duration
        playPosition: avVideo.position
        onSeekPositionChanged: seek(seekPosition);
        z: 1000
    }

    Item {
        id: videoRoot
        anchors.fill: parent

        Rectangle {
            id: infomationBar
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            visible: false
            color: Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.6)
            implicitHeight: vidTitle.implicitHeight + Kirigami.Units.largeSpacing * 2
            z: 1001

            onVisibleChanged: {
                delay(15000, function() {
                    infomationBar.visible = false;
                })
            }

            Controls.Label {
                id: vidTitle
                visible: true
                maximumLineCount: 2
                wrapMode: Text.Wrap
                anchors.left: parent.left
                anchors.leftMargin: Kirigami.Units.largeSpacing
                anchors.verticalCenter: parent.verticalCenter
                text: videoTitle
                z: 100
            }
        }

        Video {
            id: avVideo
            anchors.fill: parent
            autoLoad: true
            autoPlay: true

            Keys.onReturnPressed: {
                avVideo.playbackState == MediaPlayer.PlayingState ? avVideo.pause() : avVideo.play()
            }

            Keys.onDownPressed: {
                controlBarItem.opened = true
                controlBarItem.forceActiveFocus()
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    controlBarItem.opened = !controlBarItem.opened
                }
            }

            onStatusChanged: {
                triggerGuiEvent("media.state", {"state": status})
                if (status == MediaPlayer.EndOfMedia) {
                    pause()
                }
            }
        }
    }
}



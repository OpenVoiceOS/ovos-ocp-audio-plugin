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

import QtQuick.Layouts 1.15
import QtQuick 2.15
import QtQuick.Controls 2.15 as Controls
import org.kde.kirigami 2.19 as Kirigami
import QtQuick.Window 2.15
import Mycroft 1.0 as Mycroft
import QtMultimedia
import Qt5Compat.GraphicalEffects
import "." as Local

Rectangle {
    id: root
    readonly property var videoService: Mycroft.MediaService
    property var currentState: Mycroft.MediaService.playbackState
    property int currentMediaState: Mycroft.MediaService.mediaState

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

    //Mediaplayer Related Properties To Be Set By Probe MediaPlayer
    property var playerDuration
    property var playerPosition

    Keys.onDownPressed: (event)=> {
        controlBarItem.opened = true
        controlBarItem.forceActiveFocus()
    }

    onVideoSourceChanged: {
        root.play()
        delay(6000, function() {
            infomationBar.visible = false;
        })
    }


    function play(){
        Mycroft.MediaService.videoOutput = videoOutput;
        Mycroft.MediaService.videoSink = videoOutput.videoSink;
        videoService.mediaLoadUrl(Qt.resolvedUrl(source), audioService.VideoProvider)
    }

    function pause(){
        videoService.mediaPause()
    }

    function stop(){
        videoService.mediaStop()
    }

    function resume(){
        videoService.mediaContinue()
    }

    function next(){
        videoService.mediaNext()
    }

    function previous(){
        videoService.mediaPrevious()
    }

    function repeat(){
        videoService.mediaRepeat()
    }

    function shuffle(){
        videoService.mediaShuffle()
    }

    function seek(val){
        videoService.mediaSeek(val)
    }

    function restart(){
        videoService.mediaRestart()
    }

    Connections {
        target: Window.window
        function onVisibleChanged(visible): {
            if(video.playbackState == MediaPlayer.PlayingState) {
                stop()
            }
        }
    }

    Connections {
        target: Mycroft.MediaService

        function onDurationChanged(dur) {
            playerDuration = dur
        }

        function onPositionChanged(pos) {
            playerPosition = pos
        }

        function onPlayRequested(): {
            source = audioService.requestServiceInfo("loadedUrl")
        }

        function onStopRequested(): {
            source = ""
            root.title = ""
            root.author = ""
        }

        function onMetaDataReceived(): {
            root.playerMeta = audioService.requestServiceMetaData()

            if(root.playerMeta.hasOwnProperty("Title")) {
                root.title = root.playerMeta.Title ? root.playerMeta.Title : ""
            }

            if(root.playerMeta.hasOwnProperty("Artist")) {
                root.author = root.playerMeta.Artist
            } else if(root.playerMeta.hasOwnProperty("ContributingArtist")) {
                root.author = root.playerMeta.ContributingArtist
            }
            console.log("From QML Meta Updated Loading Metainfo")
            console.log("Author: " + root.author + " Title: " + root.title)
        }

        function onMetaDataUpdated(): {
            root.cpsMeta = audioService.requestCommonPlayMetaData()
            root.thumbnail = root.cpsMeta.thumbnail
            root.author = root.cpsMeta.artist
            root.title = root.cpsMeta.title ? root.cpsMeta.title : ""

            console.log("From QML Media Received Loading Metainfo")
            console.log(JSON.stringify(root.cpsMeta))
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

    controlBar: Local.OVOSSeekControl {
        id: seekControl
        anchors {
            bottom: parent.bottom
        }
        title: videoTitle
        videoControl: root
        duration: root.playerDuration
        playPosition: root.playerPosition
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

        VideoOutput {
            id: videoOutput
            anchors.fill: parent
            z: 5

            Keys.onReturnPressed: (event)=> {
                video.playbackState == MediaPlayer.PlayingState ? video.pause() : video.play()
            }

            Keys.onDownPressed: (event)=> {
                controlBarItem.opened = true
                controlBarItem.forceActiveFocus()
            }

            MouseArea {
                anchors.fill: parent
                onClicked: (mouse)=> {
                    controlBarItem.opened = !controlBarItem.opened
                }
            }
        }
    }
}



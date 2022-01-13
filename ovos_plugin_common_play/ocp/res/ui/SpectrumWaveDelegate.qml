import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Layouts 1.12
import QtMultimedia 5.12
import QtGraphicalEffects 1.0
import QtQuick.Shapes 1.12
import QtQuick.Templates 2.12 as T
import QtQuick.Controls 2.12 as Controls
import org.kde.kirigami 2.11 as Kirigami
import Mycroft 1.0 as Mycroft

// Wave animation
Rectangle {
    id: rect
    color: "transparent"
    width: parent.width
    height: parent.height
    property var position: rect.width
    property var spectrumLocalLength
    property var spectrumLocalData
    //property var spectrumVal: 25
    opacity: root.currentState === MediaPlayer.PlayingState ? 1 : 0
    property color spectrumWavePrimaryColor: Qt.rgba(33/255, 190/255, 166/255, 0.5)
    property color spectrumWaveSecondayColor: Qt.rgba(33/255, 148/255, 190/255, 0.5)
    y: 9

    function returnRandomFromList() {
        var nums = [15, 25, 35]
        return nums[Math.floor(Math.random() * nums.length)]
    }

    Component.onCompleted: {
            console.log("renderType", controlShape.rendererType)
    }

    Shape {
        id: controlShape
        width: parent.width
        height: parent.height
        anchors.horizontalCenter: parent.horizontalCenter
        layer.enabled: true
        layer.samples: 16
        rotation: 180
        asynchronous: true

        ShapePath {
            objectName: "path1"
            fillColor: spectrumWaveSecondayColor //Qt.rgba(0, 0.4, 0.7, 0.4)
            strokeColor: spectrumWaveSecondayColor //Qt.rgba(0, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width
            startY: 0

            PathQuad {
                x: 0; y: 0
                controlX: 0; controlY: 15 + spectrumLocalData[12] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path2"
            fillColor: spectrumWavePrimaryColor //Qt.rgba(0.5, 0.4, 0.7, 0.4)
            strokeColor: spectrumWavePrimaryColor  //Qt.rgba(0.5, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 2
            startY: 0

            PathQuad {
                x: 0; y: 0
                controlX: 0; controlY: 15 + spectrumLocalData[13] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path3"
            fillColor: spectrumWaveSecondayColor //Qt.rgba(0, 0.4, 0.7, 0.4)
            strokeColor: spectrumWaveSecondayColor //Qt.rgba(0, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 1.5
            startY: 0


            PathQuad {
                x: 100; y: 0
                controlX: controlShape.width / 3; controlY: 15 + spectrumLocalData[14] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path4"
            fillColor: spectrumWavePrimaryColor //Qt.rgba(0.5, 0.4, 0.7, 0.4)
            strokeColor: spectrumWavePrimaryColor //Qt.rgba(0.5, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 2 - 300
            startY: 0

            PathQuad {
                x: 60 * 10; y: 0
                controlX: 440; controlY: randSlider.value
            }
        }

        ShapePath {
            objectName: "path5"
            fillColor: spectrumWaveSecondayColor //Qt.rgba(0, 0.4, 0.7, 0.4)
            strokeColor: spectrumWaveSecondayColor //Qt.rgba(0, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 6
            startY: 0

            PathQuad {
                x: 500; y: 0
                controlX: 400; controlY: 15 + spectrumLocalData[15] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path6"
            fillColor: spectrumWavePrimaryColor //Qt.rgba(0.5, 0.4, 0.7, 0.4)
            strokeColor: spectrumWavePrimaryColor //Qt.rgba(0.5, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 8
            startY: 0

            PathQuad {
                x: controlShape.width; y: 0
                controlX: controlShape.width / 1.2 * spectrumLocalData[16]; controlY: 15 + spectrumLocalData[16] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path7"
            fillColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 2
            startY: 0

            PathQuad {
                x: controlShape.width; y: 0
                controlX: controlShape.width - 10; controlY: 15 + spectrumLocalData[17] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path8"
            fillColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 100
            startY: 0

            PathQuad {
                x: controlShape.width / 1; y: 0
                controlX: controlShape.width / 2; controlY: 15 + spectrumLocalData[18] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path9"
            fillColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 200
            startY: 0

            PathQuad {
                x: controlShape.width / 1.5; y: 0
                controlX: controlShape.width / 7; controlY: 15 + spectrumLocalData[11] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path10"
            fillColor: spectrumWavePrimaryColor //Qt.rgba(0.5, 0.4, 0.7, 0.4)
            strokeColor: spectrumWavePrimaryColor //Qt.rgba(0.5, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 20
            startY: 0

            PathQuad {
                x: controlShape.width / 1.25; y: 0
                controlX: controlShape.width / 2; controlY: 15 + spectrumLocalData[10] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path11"
            fillColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width
            startY: 0

            PathQuad {
                x: controlShape.width / 1.8; y: 0
                controlX: controlShape.width / 1.2; controlY: 15 + spectrumLocalData[9] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path12"
            fillColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 2.5
            startY: 0

            PathQuad {
                x: controlShape.width / 1.3; y: 0
                controlX: controlShape.width / 1.6; controlY: 15 + spectrumLocalData[8] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path13"
            fillColor: spectrumWavePrimaryColor //Qt.rgba(0.6, 0.4, 0.7, 0.4)
            strokeColor: spectrumWavePrimaryColor //Qt.rgba(0.6, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 20
            startY: 0

            PathQuad {
                x: controlShape.width / 1.9; y: 0
                controlX: controlShape.width / 3; controlY: 15 + spectrumLocalData[19] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        ShapePath {
            objectName: "path14"
            fillColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeColor: spectrumWaveSecondayColor //Qt.rgba(0.0, 0.4, 0.7, 0.4)
            strokeWidth: 0
            startX: controlShape.width / 50
            startY: 0

            PathQuad {
                x: controlShape.width / 3.5; y: 0
                controlX: controlShape.width / 6 * spectrumLocalData[7]; controlY: 15 + spectrumLocalData[7] * (root.spectrumHeight + returnRandomFromList())
            }
        }

        Behavior on y {
            NumberAnimation {
                duration: 150
                easing.type: Easing.Linear
            }
        }
        
        Behavior on opacity {
            NumberAnimation{
                duration: 1500 * spectrumLocalData[12] + parent.height
                easing.type: Easing.Linear
            }
        }
    }    

//    Shape {
//        id: controlShape
//        width: parent.width
//        height: parent.height
//        anchors.horizontalCenter: parent.horizontalCenter
//        layer.enabled: true
//        layer.samples: 8
//        rotation: 180

//        ShapePath {
//            fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeWidth: 0
//            startX: controlShape.width
//            startY: 0

//            PathQuad {
//                x: 0; y: 0
//                controlX: 0; controlY: 15 + spectrumLocalData[12] * root.spectrumHeight
//            }
//        }
//    }

//    Shape {
//        id: controlShape2
//        width: parent.width
//        height: parent.height
//        anchors.horizontalCenter: parent.horizontalCenter
//        layer.enabled: true
//        layer.samples: 8
//        rotation: 180

//        ShapePath {
//            fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeWidth: 0
//            startX: controlShape2.width / 2
//            startY: 0

//            PathQuad {
//                x: 0; y: 0
//                controlX: 0; controlY: 15 + spectrumLocalData[13] * root.spectrumHeight
//            }
//        }
//    }

//    Shape {
//        id: controlShape3
//        width: parent.width
//        height: parent.height
//        anchors.horizontalCenter: parent.horizontalCenter
//        layer.enabled: true
//        layer.samples: 8
//        rotation: 180
//        z: 0


//        ShapePath {
//            fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeWidth: 0
//            startX: controlShape3.width / 1.5
//            startY: 0


//            PathQuad {
//                x: 100; y: 0
//                controlX: controlShape3.width / 3; controlY: 15 + spectrumLocalData[14] * root.spectrumHeight
//            }
//        }
//    }

//    Shape {
//        id: controlShape4
//        width: parent.width
//        height: parent.height
//        anchors.horizontalCenter: parent.horizontalCenter
//        layer.enabled: true
//        layer.samples: 8
//        rotation: 180
//        z: 4


//        ShapePath {
//            fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeWidth: 0
//            startX: controlShape.width / 2 - 300
//            startY: 0

//            PathQuad {
//                x: 60 * 10; y: 0
//                controlX: 440; controlY: 15 + spectrumLocalData[11] * root.spectrumHeight
//            }
//        }
//    }

//    Shape {
//        id: controlShape5
//        width: parent.width
//        height: parent.height
//        anchors.horizontalCenter: parent.horizontalCenter
//        layer.enabled: true
//        layer.samples: 8
//        rotation: 180

//        ShapePath {
//            fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeWidth: 0
//            startX: controlShape2.width / 6
//            startY: 0

//            PathQuad {
//                x: 500; y: 0
//                controlX: 400; controlY: 15 + spectrumLocalData[15] * root.spectrumHeight
//            }
//        }
//    }

//    Shape {
//        id: controlShape6
//        width: parent.width
//        height: parent.height
//        anchors.horizontalCenter: parent.horizontalCenter
//        layer.enabled: true
//        layer.samples: 8
//        rotation: 180

//        ShapePath {
//            fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
//            strokeWidth: 0
//            startX: controlShape2.width / 10
//            startY: 0

//            PathQuad {
//                x: 900; y: 0
//                controlX: 800; controlY: 15 + spectrumLocalData[16] * root.spectrumHeight
//            }
//        }
//    }


    // Shape {
    //         id: controlShape
    //         width: parent.width
    //         height: parent.height
    //         anchors.horizontalCenter: parent.horizontalCenter
    //         layer.enabled: true
    //         layer.samples: 8
    //         rotation: 180

    //         ShapePath {
    //             fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //             strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //             strokeWidth: 0
    //             startX: index > 0 ? controlShape.width / Math.random(3) : controlShape.width
    //             startY: 0

    //             PathQuad {
    //                 x: parseInt(index + "00"); y: 0
    //                 controlX: index > 0 ? x + 100 : x - 100; controlY: spectrumVal * 2
    //             }
    //         }
    //     }

    // Shape {
    //     id: controlShape
    //     width: parent.width
    //     height: parent.height
    //     anchors.horizontalCenter: parent.horizontalCenter
    //     layer.enabled: true
    //     layer.samples: 8

    //     ShapePath {
    //         fillColor: Qt.rgba(0, 0, 0.2, 0.4)
    //         strokeColor: Qt.rgba(0, 0, 0.2, 0.4)
    //         strokeWidth: 0
    //         startX: 0
    //         startY: 0

    //                     PathLine {
    //                         x: -controlShape.width
    //                         y: 0
    //                     }

    //                     PathLine {
    //                         x: controlShape.width / 2 - 8
    //                         y: 0 + spectrumVal + index
    //                     }

    //                     PathLine {
    //                         x: controlShape.width / 2 - 8
    //                         y: 0 + spectrumVal + index
    //                     }

    //                     PathLine {
    //                         x: controlShape.width / 2 + 8
    //                         y: 0 + spectrumVal + index
    //                     }

    //                     PathLine {
    //                         x: controlShape.width / 2 + 8
    //                         y: 0 + spectrumVal + index
    //                     }

    //                     PathLine {
    //                         x: controlShape.width * 2
    //                         y: 0
    //                     }

    //         // PathLine {
    //         //     x: -controlShape.width
    //         //     y: 0
    //         // }

    //         // PathLine {
    //         //     x: controlShape.width / 2
    //         //     y: 0 + spectrumVal
    //         // }

    //         // PathLine {
    //         //     x: controlShape.width * 2
    //         //     y: 0
    //         // }

    //         // PathLine {
    //         //     x: -controlShape.width + 20
    //         //     y: 0
    //         // }

    //         // PathLine {
    //         //     x: controlShape.width - 20
    //         //     y: 0 + spectrumVal
    //         // }

    //         // PathLine {
    //         //     x: controlShape.width - 20
    //         //     y: 0 + spectrumVal
    //         // }

    //         // PathLine {
    //         //     x: controlShape.width + 20
    //         //     y: 0
    //         // }
    //     }
    // }

    // Shape {
    //     id: controlShape
    //     width: parent.width
    //     height: parent.height
    //     anchors.horizontalCenter: parent.horizontalCenter
    //     layer.enabled: true
    //     layer.samples: 8
    //     rotation: 180
        
    //     ShapePath {
    //         fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeWidth: 0
    //         startX: controlShape.width
    //         startY: 0
            
    //         PathQuad {
    //             x: 0; y: 0
    //             controlX: 0; controlY: spectrumVal
    //         }
    //     }
    // }
    
    // Shape {
    //     id: controlShape2
    //     width: parent.width
    //     height: parent.height
    //     anchors.horizontalCenter: parent.horizontalCenter
    //     layer.enabled: true
    //     layer.samples: 8
    //     rotation: 180
        
    //     ShapePath {
    //         fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeWidth: 0
    //         startX: controlShape2.width / 2
    //         startY: 0
            
    //         PathQuad {
    //             x: 0; y: 0
    //             controlX: 0; controlY: spectrumVal
    //         }
    //     }
    // }
    
    // Shape {
    //     id: controlShape3
    //     width: parent.width
    //     height: parent.height
    //     anchors.horizontalCenter: parent.horizontalCenter
    //     layer.enabled: true
    //     layer.samples: 8
    //     rotation: 180
    //     z: 0
        
        
    //     ShapePath {
    //         fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeWidth: 0
    //         startX: controlShape3.width / 1.5
    //         startY: 0
            
            
    //         PathQuad {
    //             x: 100; y: 0
    //             controlX: controlShape3.width / 3; controlY: spectrumVal
    //         }
    //     }
    // }
    
    // Shape {
    //     id: controlShape4
    //     width: parent.width
    //     height: parent.height
    //     anchors.horizontalCenter: parent.horizontalCenter
    //     layer.enabled: true
    //     layer.samples: 8
    //     rotation: 180
    //     z: 4
        
        
    //     ShapePath {
    //         fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeWidth: 0
    //         startX: controlShape.width / 2 - 300
    //         startY: 0
            
    //         PathQuad {
    //             x: 60 * 10; y: 0
    //             controlX: 440; controlY: spectrumVal
    //         }
    //     }
    // }
    
    // Shape {
    //     id: controlShape5
    //     width: parent.width
    //     height: parent.height
    //     anchors.horizontalCenter: parent.horizontalCenter
    //     layer.enabled: true
    //     layer.samples: 8
    //     rotation: 180
        
    //     ShapePath {
    //         fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeWidth: 0
    //         startX: controlShape2.width / 6
    //         startY: 0
            
    //         PathQuad {
    //             x: 500; y: 0
    //             controlX: 400; controlY: spectrumVal
    //         }
    //     }
    // }
    
    // Shape {
    //     id: controlShape6
    //     width: parent.width
    //     height: parent.height
    //     anchors.horizontalCenter: parent.horizontalCenter
    //     layer.enabled: true
    //     layer.samples: 8
    //     rotation: 180
        
    //     ShapePath {
    //         fillColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeColor: Qt.rgba(0, 0.4, 0.7, 0.4)
    //         strokeWidth: 0
    //         startX: controlShape2.width / 10
    //         startY: 0
            
    //         PathQuad {
    //             x: 900; y: 0
    //             controlX: 800; controlY: spectrumVal
    //         }
    //     }
    // }
}
